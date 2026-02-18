import os
import re
import zipfile


def find_latest_result_timestamp(results_dir):
    """
    Scan directory for latest FollowScenario timestamp.
    """
    all_files = os.listdir(results_dir)
    pattern = re.compile(r"FollowScenario_(\d{8}_\d{6})")
    timestamps = [m.group(1) for f in all_files if (m := pattern.search(f))]
    return max(timestamps) if timestamps else None


def get_result_files(results_dir, timestamp):
    """
    Return a list of PNG/JPG/CSV files matching the timestamp,
    plus log and json if present.
    """
    selected = []

    if not timestamp:
        return selected

    for f in os.listdir(results_dir):
        if timestamp in f and f.lower().endswith((".png", ".jpg", ".jpeg")):
            selected.append(os.path.join(results_dir, f))

    # Add log + json always if they exist
    log_path = os.path.join(results_dir, "FollowLeadingVehicle_1.log")
    json_path = os.path.join(results_dir, "FollowLeadingVehicle_1.json")

    if os.path.exists(log_path): selected.append(log_path)
    if os.path.exists(json_path): selected.append(json_path)

    return selected


def read_summary_log(results_dir):
    """
    Return summary text if summary log exists.
    """
    summary_path = os.path.join(results_dir, "scenario_summary.log")
    if not os.path.exists(summary_path):
        return None, None

    with open(summary_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read(), summary_path


def zip_results(output_zip_path, selected_files, summary_path=None):
    """
    Create a ZIP file containing all selected files and summary.
    """
    with zipfile.ZipFile(output_zip_path, "w") as zipf:
        for f in selected_files:
            zipf.write(f, os.path.basename(f))

        if summary_path:
            zipf.write(summary_path, os.path.basename(summary_path))

    return True
