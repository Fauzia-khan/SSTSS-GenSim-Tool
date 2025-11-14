import os
import subprocess


def run_metrics():
    """
    Run the metrics_manager.py script with the configured metric and log file.
    Returns True if successful, False otherwise.
    """
    try:
        subprocess.run(
            [
                "python3.8",
                "metrics_manager.py",
                "--metric", "srunner/metrics/examples/velocity_and_distance_metric.py",
                "--log", "results/test/FollowLeadingVehicle_1.log",
            ],
            cwd="/home/laima/Documents/scenario_runner-master",
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
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to run metrics script: {e}")
        return False
