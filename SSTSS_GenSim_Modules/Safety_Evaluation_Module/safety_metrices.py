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
# MAIN PROCESSOR
# ----------------------------
def process_raw_file(raw_csv_path):
    df = pd.read_csv(raw_csv_path)
    base_name = os.path.basename(raw_csv_path).replace("_data.csv", "")
    print(f"[SAFETY] Processing: {base_name}")

    # --- 1. Speeds to m/s ---
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

    # Merge back
    df.set_index("Time (s)", inplace=True)
    df_1hz.set_index("Time (s)", inplace=True)
    df["Jerk (m/s³) (1 Hz)"] = df_1hz["Jerk (m/s³)"]
    df.reset_index(inplace=True)

    # --- 5. RSS ---
    df["RSS Distance (m)"] = df.apply(
        lambda r: calculate_rss(r["Ego Speed (m/s)"], r["Lead Speed (m/s)"]),
        axis=1
    )

    # --- 6. Save metrics ---
    metrics_csv = os.path.join(OUTPUT_DIR, f"{base_name}_metrics.csv")
    df.to_csv(metrics_csv, index=False)
    print(f"[SAFETY] Written: {metrics_csv}")


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
