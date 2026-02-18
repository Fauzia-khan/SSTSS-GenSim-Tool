from config import SCENARIO_RUNNER_ROOT
import os
import signal
import subprocess


from modules.constants import SCENARIO_RUNNER_ROOT
import os
import subprocess
import signal

def run_scenario_runner(summary_log: str):
    """
    Run ScenarioRunner via a shell script and write all output to the given summary log file.
    """

    # Correct: Build script path
    scenario_runner_script = os.path.join(SCENARIO_RUNNER_ROOT, "run_scenario_runner.sh")

    print(f"[INFO] Running ScenarioRunner from {scenario_runner_script}")
    print(f"[INFO] Saving output to {summary_log}")

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



def stop_autoware():
    """
    Find and stop Autoware process by name.
    """
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
