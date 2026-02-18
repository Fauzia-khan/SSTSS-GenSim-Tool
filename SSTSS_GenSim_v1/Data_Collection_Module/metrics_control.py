import os
import sys
import subprocess
import shutil

from config import SCENARIO_RUNNER_ROOT, PYTHONPATH_ENTRIES

TOOL_ROOT = os.path.expanduser("~/Desktop/GenSim_v2")
if TOOL_ROOT not in sys.path:
    sys.path.append(TOOL_ROOT)

SAFETY_RESULTS_DIR = os.path.join(TOOL_ROOT, "Safety_Evaluation_Module", "results")

def run_metrics():
    # PYTHONPATH'i config'ten oluştur
    env = os.environ.copy()
    extra = ":".join(PYTHONPATH_ENTRIES)
    env["PYTHONPATH"] = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (env["PYTHONPATH"] + ":" if env["PYTHONPATH"] else "") + extra

    try:
        subprocess.run(
            [
                "python",
                "metrics_manager.py",
                "--metric", "srunner/metrics/examples/velocity_and_distance_metric.py",
                "--log", "results/test/FollowLeadingVehicle_1.log",
            ],
            cwd=SCENARIO_RUNNER_ROOT,
            env=env,
            check=True,
        )

        print("[✓] Metrics script finished.")

        # Safety Metrics
        try:
            print("[✓] Starting Safety Metrics Module...")
            from Safety_Evaluation_Module.safety_metrices import process_latest_raw_file
            process_latest_raw_file()
            print("[✓] Safety metrics completed.")
        except Exception as e:
            print(f"[ERROR] Safety metrics failed: {e}")

        # Copy summary log
        os.makedirs(SAFETY_RESULTS_DIR, exist_ok=True)
        SCENARIO_RESULTS_DIR = os.path.join(SCENARIO_RUNNER_ROOT, "results", "test")

        summary_src = os.path.join(SCENARIO_RESULTS_DIR, "scenario_summary.log")
        summary_dst = os.path.join(SAFETY_RESULTS_DIR, "scenario_summary.log")

        if os.path.exists(summary_src):
            shutil.copy(summary_src, summary_dst)
            print(f"[✓] Copied scenario summary to: {summary_dst}")
        else:
            print(f"[WARN] scenario_summary.log not found at: {summary_src}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to run metrics script: {e}")
        return False
