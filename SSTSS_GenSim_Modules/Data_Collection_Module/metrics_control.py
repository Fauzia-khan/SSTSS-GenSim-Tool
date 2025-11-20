from config import SCENARIO_RUNNER_ROOT, RESULTS_DIR
import os
import sys
import subprocess
import shutil

# ----------------------------------------------------------
# Add TOOL ROOT so we can import Safety_Evaluation_Module
# ----------------------------------------------------------
TOOL_ROOT = os.path.expanduser("~/Desktop/SSTSS Tool 1st september/SSTSS_GenSim_Modules")

if TOOL_ROOT not in sys.path:
    sys.path.append(TOOL_ROOT)

SAFETY_RESULTS_DIR = os.path.join(TOOL_ROOT, "Safety_Evaluation_Module", "results")
def run_metrics():
    """
    1) Run the metrics_manager.py script (ScenarioRunner metrics)
    2) Run the Safety_Evaluation_Module to compute extra metrics
    3) Copy scenario_summary.log into Safety_Evaluation_Module/results
    """
    try:
        # --- 1. Run ScenarioRunner Metrics ---
        subprocess.run(
            [
                "python3.8",
                "metrics_manager.py",
                "--metric", "srunner/metrics/examples/velocity_and_distance_metric.py",
                "--log", "results/test/FollowLeadingVehicle_1.log",
            ],
            cwd=SCENARIO_RUNNER_ROOT,
            env={
                **os.environ,
                "CARLA_ROOT": "/home/laima/Documents/CARLA_0.9.13",
                "PYTHONPATH": (
                    "/home/laima/ali/ali_ws/devel/lib/python3/dist-packages:"
                    "/home/laima/Documents/autoware_mini_ws/devel/lib/python3/dist-packages:"
                    "/opt/ros/noetic/lib/python3/dist-packages:"
                    "/home/laima/Documents/CARLA_0.9.13/PythonAPI/carla/dist/"
                    "carla-0.9.13-py3.7-linux-x86_64.egg:"
                    "/home/laima/Documents/CARLA_0.9.13/PythonAPI/carla/agents:"
                    "/home/laima/Documents/CARLA_0.9.13/PythonAPI/carla"
                ),
            },
            check=True,
        )

        print("[✓] Metrics script finished.")

        # --- 2. Run Safety Metrics (your separate module) ---
        try:
            print("[✓] Starting Safety Metrics Module...")
            from Safety_Evaluation_Module.safety_metrices import process_latest_raw_file

            process_latest_raw_file()
            print("[✓] Safety metrics completed.")
        except Exception as e:
            print(f"[ERROR] Safety metrics failed: {e}")

        # --- 3. Copy scenario_summary.log into Safety_Evaluation_Module/results ---
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
