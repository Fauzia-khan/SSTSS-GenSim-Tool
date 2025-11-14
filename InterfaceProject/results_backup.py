import os
import shutil
import glob


def backup_simulation_outputs(timestamp, base_dir="/home/laima/Documents/scenario_runner-master/results/test"):
    """
    Backup simulation result files into a new directory labeled with the timestamp.
    """
    backup_dir = os.path.join(base_dir, f"FollowLeadingVehicle_1_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)

    print(f"[INFO] Backing up outputs to: {backup_dir}")

    # 1. Copy .log and .json files
    for ext in ["log", "json"]:
        src = os.path.join(base_dir, f"FollowLeadingVehicle_1.{ext}")
        if os.path.exists(src):
            shutil.copy(src, backup_dir)
            print(f"[✓] Copied {src}")
        else:
            print(f"[!] Missing: {src}")

    # 2. Copy metrics files (speed, jerk, metrics.csv)
    patterns = ["metrics.csv", "speed_distance.png", "jerk_1hz.png"]

    for ext in patterns:
        pattern = f"FollowScenario_{timestamp}_{ext}"
        matches = glob.glob(os.path.join(base_dir, pattern))
        for f in matches:
            shutil.copy(f, backup_dir)
            print(f"[✓] Copied {f}")

        if not matches:
            print(f"[!] No match for: {pattern}")

    return backup_dir
