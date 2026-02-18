from config import SCENARIO_RUNNER_ROOT
import os
import signal
import subprocess


from modules.constants import SCENARIO_RUNNER_ROOT
import os
import subprocess
import signal

from config import PYTHONPATH_ENTRIES

env = os.environ.copy()
env["PYTHONPATH"] = ":".join(PYTHONPATH_ENTRIES)


def run_scenario_runner(summary_log: str):
    """
    Run ScenarioRunner via a shell script and write all output to the given summary log file.
    """

    # Correct: Build script path
    scenario_runner_script = os.path.join(SCENARIO_RUNNER_ROOT, "run_scenario_runner.sh")

    print(f"[INFO] Running ScenarioRunner from {scenario_runner_script}")
    print(f"[INFO] Saving output to {summary_log}")

    os.makedirs(os.path.dirname(summary_log), exist_ok=True)

    with open(summary_log, "w", encoding="utf-8", errors="ignore") as f:
        process = subprocess.Popen(
            ["bash", scenario_runner_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            print(line, end="")
            f.write(line)

        process.wait()

    print(f"[✓] ScenarioRunner finished. Summary saved to {summary_log}")



import subprocess
import time

import subprocess
import time

def stop_carla():
    """
    Brute-force stop CARLA server.
    Adjust patterns if your process name differs.
    """
    patterns = [
        r"CarlaUE4",          # common CARLA executable name
        r"CarlaUnreal",       # some builds
        r"UE4Editor",         # if running editor build
    ]

    for p in patterns:
        subprocess.run(["pkill", "-TERM", "-f", p], check=False)

    time.sleep(3)

    for p in patterns:
        subprocess.run(["pkill", "-KILL", "-f", p], check=False)

    # Optional: free port 2000 if something is stuck holding it
    subprocess.run(["bash", "-lc", "fuser -k 2000/tcp >/dev/null 2>&1 || true"], check=False)

    print("[✓] CARLA brute-force stop done.")


def stop_autoware():
    """
    Brute-force stop Autoware Mini + common ROS/CARLA bridge leftovers.
    Minimalistic: uses pkill by pattern.
    """
    patterns = [
        r"roslaunch autoware_mini start_carla.launch",
        r"autoware_mini",                 # optional extra coverage
        r"roscore",
        r"rosmaster",
        r"rosout",
        r"robot_state_publisher",
        r"rviz",
        r"carla_ros_bridge",
        r"carla_",
        r"scenario_runner",               # only if you sometimes leave it running
        r"run_set_goal\.sh",
        r"terminator",                    # because you launch via terminator
    ]

    # Try graceful first
    for p in patterns:
        subprocess.run(["pkill", "-TERM", "-f", p], check=False)

    time.sleep(3)

    # Then force kill
    for p in patterns:
        subprocess.run(["pkill", "-KILL", "-f", p], check=False)

    print("[✓] Autoware/ROS brute-force stop done.")


"""def stop_autoware():
    
    try:
        result = subprocess.run(
            ["pgrep", "-f", "roslaunch autoware_mini start_carla.launch"],
            capture_output=True,
            text=True
        )
        pids = result.stdout.strip().splitlines()
        for pid in pids:
            if not pid:
                continue
            print(f"[INFO] Stopping Autoware process {pid}")
            os.kill(int(pid), signal.SIGTERM)
        if not pids or all(not p for p in pids):
            print("[INFO] No Autoware process found to stop.")
    except Exception as e:
        print(f"[ERROR] Failed to stop Autoware: {e}")
"""