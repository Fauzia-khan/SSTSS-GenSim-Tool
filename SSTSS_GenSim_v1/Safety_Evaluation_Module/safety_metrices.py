import os
import pandas as pd
import numpy as np

# Try SciPy (optional)
try:
    from scipy.ndimage import gaussian_filter1d
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False

# ----------------------------
# DIRECTORIES (auto portable)
# ----------------------------
TOOL_ROOT = os.path.expanduser("~/Desktop/SSTSS Tool 1st september/SSTSS_GenSim_Modules")

#TOOL_ROOT = os.path.expanduser("~/Desktop/GenSim_v2")


RAW_INPUT_DIR = os.path.join(TOOL_ROOT, "Data_Collection_Module", "raw_data")
OUTPUT_DIR = os.path.join(TOOL_ROOT, "Safety_Evaluation_Module", "results")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sampling parameters
SAMPLING_RATE = 20
TARGET_RATE = 1
DOWNSAMPLE_EVERY = int(SAMPLING_RATE / TARGET_RATE)
GAUSSIAN_SIGMA = 2


# ----------------------------
# RSS Formula
# ----------------------------
def calculate_rss(v_r, v_f, rho=0.001, a_max=1.0, b_min=1.0, b_max=1.5):
    term1 = v_r * rho
    term2 = 0.5 * a_max * rho ** 2
    term3 = ((v_r + rho * a_max) ** 2) / (2 * b_min)
    term4 = (v_f ** 2) / (2 * b_max)
    return max(term1 + term2 + term3 - term4, 0)


# ----------------------------
# TTC (Time-To-Collision)
# ----------------------------
def calculate_ttc(ego_speed, lead_speed, distance_between):
    """
    ego_speed, lead_speed [m/s], distance_between [m]
    Kullanıcının verdiği formüle sadık kalır; kapanma yoksa TTC=inf olacak şekilde güvenli hale getirir.
    """
    ego_speed = np.asarray(ego_speed, dtype=float)
    lead_speed = np.asarray(lead_speed, dtype=float)
    distance_between = np.asarray(distance_between, dtype=float)

    closing = ego_speed - lead_speed  # >0 ise yaklaşıyor
    # Yaklaşmıyorsa TTC = inf (narrow-down için min ttc hesaplarken bunu dikkate almayacağız)
    ttc = np.where(closing > 0.0, distance_between / (closing + 1e-5), np.inf)
    # Negatif/NaN mesafelerde de inf yap
    ttc = np.where(np.isfinite(ttc) & (ttc > 0.0), ttc, np.inf)

    finite = ttc[np.isfinite(ttc)]
    min_ttc = float(np.min(finite)) if finite.size > 0 else None
    return ttc, min_ttc


def _find_distance_column(df: pd.DataFrame):
    """
    Raw CSV'de 'mesafe' kolon adı projeden projeye değişebiliyor.
    En güvenli yöntem: bilinen aday isimleri sırayla denemek.
    """
    candidates = [
        "Distance Between (m)",
        "distance_between",
        "Relative Distance (m)",
        "Relative distance (m)",
        "Lead Distance (m)",
        "Gap (m)",
        "Distance (m)",
        "distance (m)",
        "distance",
    ]
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _infer_collision_flag(df: pd.DataFrame) -> int:
    """
    Çarpışma kolonu varsa 1/0 üret. Yoksa 0.
    """
    candidates = [
        "Collision",
        "collision",
        "HasCollision",
        "Has Collision",
        "Collision Flag",
        "collision_flag",
        "is_collision",
    ]
    for c in candidates:
        if c in df.columns:
            try:
                return int(pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int).max())
            except Exception:
                return 0
    return 0


# ----------------------------
# MAIN PROCESSOR
# ----------------------------
def process_raw_file(raw_csv_path):
    df = pd.read_csv(raw_csv_path)
    base_name = os.path.basename(raw_csv_path).replace("_data.csv", "")
    print(f"[SAFETY] Processing: {base_name}")

    # --- 1. Speeds to m/s ---
    # Bu kolonlar yoksa burada patlar; bu iyi çünkü "sessiz yanlış" istemiyoruz.
    df["Ego Speed (m/s)"] = df["Ego Speed (km/h)"] / 3.6
    df["Lead Speed (m/s)"] = df["Lead Speed (km/h)"] / 3.6

    # --- 2. Acceleration ---
    df["Ego Accel (m/s²)"] = df["Ego Speed (m/s)"].diff() / df["Time (s)"].diff()
    df["Lead Accel (m/s²)"] = df["Lead Speed (m/s)"].diff() / df["Time (s)"].diff()

    # --- 3. Smoothed Accel ---
    accel_raw = df["Ego Accel (m/s²)"].fillna(method="ffill")
    if HAVE_SCIPY:
        df["Smooth Accel (m/s²)"] = gaussian_filter1d(accel_raw, sigma=GAUSSIAN_SIGMA)
    else:
        window = GAUSSIAN_SIGMA * 4 + 1
        df["Smooth Accel (m/s²)"] = accel_raw.rolling(window, center=True, min_periods=1).mean()

    # --- 4. Downsample and compute jerk ---
    df_1hz = df.iloc[::DOWNSAMPLE_EVERY].copy().reset_index(drop=True)
    df_1hz["Jerk (m/s³)"] = df_1hz["Smooth Accel (m/s²)"].diff() / df_1hz["Time (s)"].diff()

    # Merge back (index Time)
    df.set_index("Time (s)", inplace=True)
    df_1hz.set_index("Time (s)", inplace=True)
    df["Jerk (m/s³) (1 Hz)"] = df_1hz["Jerk (m/s³)"]
    df.reset_index(inplace=True)

    # --- 5. RSS ---
    df["RSS Distance (m)"] = df.apply(
        lambda r: calculate_rss(r["Ego Speed (m/s)"], r["Lead Speed (m/s)"]),
        axis=1
    )

    # --- 6. TTC ---
    dist_col = _find_distance_column(df)
    if dist_col is None:
        # Kritik deney: mesafe kolonu yoksa TTC hesaplayamayız -> min_ttc None dön.
        # (GUI tarafı bunu penalize edecek; bu "sessiz yanlış"tan daha güvenli.)
        print("[SAFETY][ERROR] Distance column not found in raw CSV. TTC cannot be computed.")
        df["TTC (s)"] = np.nan
        min_ttc = None
    else:
        ttc, min_ttc = calculate_ttc(
            df["Ego Speed (m/s)"].values,
            df["Lead Speed (m/s)"].values,
            pd.to_numeric(df[dist_col], errors="coerce").fillna(np.inf).values
        )
        df["TTC (s)"] = ttc

    # --- 7. Collision flag (if available) ---
    collision = _infer_collision_flag(df)

    # --- 8. Save metrics ---
    metrics_csv = os.path.join(OUTPUT_DIR, f"{base_name}_metrics.csv")
    df.to_csv(metrics_csv, index=False)
    print(f"[SAFETY] Written: {metrics_csv}")

    # GUI/optimizer'ın beklediği dict formatı
    return {
        "min_ttc": min_ttc,
        "collision": collision,
        "metrics_csv": metrics_csv,
        "raw_csv": raw_csv_path,
        "distance_col": dist_col,
    }


def find_latest_raw_csv():
    files = [f for f in os.listdir(RAW_INPUT_DIR) if f.endswith("_data.csv")]
    if not files:
        print("[SAFETY] No raw CSV found!")
        return None

    files.sort(
        key=lambda f: os.path.getmtime(os.path.join(RAW_INPUT_DIR, f)),
        reverse=True
    )

    latest = os.path.join(RAW_INPUT_DIR, files[0])
    print(f"[SAFETY] Latest raw file: {latest}")
    return latest


# ----------------------------
# Public function for GUI button
# ----------------------------
def process_latest_raw_file():
    latest = find_latest_raw_csv()
    if latest:
        return process_raw_file(latest)
    return None
