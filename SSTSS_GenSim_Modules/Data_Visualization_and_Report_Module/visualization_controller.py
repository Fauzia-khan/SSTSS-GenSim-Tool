import os
import pandas as pd
from datetime import datetime

from .results_utils import (
    find_latest_result_timestamp,
    get_result_files,
    read_summary_log,
    zip_results,
)

from .plot_metrics import plot_speed_and_distance, plot_jerk


# -------- DIRECTORIES --------
TOOL_ROOT = os.path.expanduser("~/Desktop/SSTSS Tool 1st september/SSTSS_GenSim_Modules")

METRICS_DIR = os.path.join(TOOL_ROOT, "Safety_Evaluation_Module", "results")
PLOT_OUTPUT_DIR = os.path.join(METRICS_DIR, "plots")

RAW_DATA_DIR = os.path.expanduser(
    "~/Desktop/SSTSS Tool 1st september/SSTSS_GenSim_Modules/Data_Collection_Module/raw_data"
)

os.makedirs(PLOT_OUTPUT_DIR, exist_ok=True)


# -------- MAIN VISUALIZATION LOGIC --------
def process_visualization():
    """
    1. Load newest metrics CSV
    2. Generate plots
    3. Prepare summary info
    4. Return everything for GUI
    """

    # ----------------------------
    # 1) Find latest metrics file
    # ----------------------------
    latest_ts = find_latest_result_timestamp(METRICS_DIR)
    if not latest_ts:
        print("[VIS] No timestamp found in metrics folder.")
        return None

    metrics_filename = f"FollowScenario_{latest_ts}_metrics.csv"
    metrics_path = os.path.join(METRICS_DIR, metrics_filename)

    if not os.path.exists(metrics_path):
        print("[VIS] Metrics CSV missing:", metrics_path)
        return None

    print(f"[VIS] Using metrics file: {metrics_path}")

    # ----------------------------
    # 2) Load CSV
    # ----------------------------
    df = pd.read_csv(metrics_path)

    # ----------------------------
    # 3) Generate plots
    # ----------------------------
    plot_speed = os.path.join(PLOT_OUTPUT_DIR, f"{latest_ts}_speed_distance.png")
    plot_jerk_ = os.path.join(PLOT_OUTPUT_DIR, f"{latest_ts}_jerk.png")

    plot_speed_and_distance(df, plot_speed)
    plot_jerk(df, plot_jerk_)

    # ----------------------------
    # 4) Read summary if exists
    # ----------------------------
    summary_text, summary_path = read_summary_log(METRICS_DIR)

    # ----------------------------
    # 5) Collect ALL result files
    # ----------------------------
    file_list = [
        metrics_path,  # processed metrics
        plot_speed,  # speed-distance plot
        plot_jerk_,  # jerk plot
    ]

    # -------- ADD RAW DATA CSV ----------
    raw_csv = os.path.join(
        RAW_DATA_DIR,
        f"FollowScenario_{latest_ts}_data.csv"
    )

    if os.path.exists(raw_csv):
        file_list.append(raw_csv)
        print("[VIS] Added RAW data:", raw_csv)
    else:
        print("[VIS] RAW data file missing:", raw_csv)
    # -------------------------------------

    # -------- ADD SCENARIORUNNER LOG/JSON AND ALL EXTRA FILES (NO DUPLICATES) --------
    extra_files = get_result_files(METRICS_DIR, latest_ts)

    for f in extra_files:
        if f not in file_list:
            file_list.append(f)
    # -------------------------------------

    # Add ScenarioRunner log/json if present
    file_list.extend(get_result_files(METRICS_DIR, latest_ts))

    return {
        "timestamp": latest_ts,
        "metrics_csv": metrics_path,
        "plot_speed": plot_speed,
        "plot_jerk": plot_jerk_,
        "summary_text": summary_text,
        "summary_path": summary_path,
        "all_files": file_list
    }


def create_zip_for_download(save_path, file_list, summary_path):
    zip_results(save_path, file_list, summary_path)
    return True

