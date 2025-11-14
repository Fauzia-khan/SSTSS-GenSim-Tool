import subprocess
import time

def launch_carla():
    """
    Launch CARLA simulation using the generate_simulation.sh script.
    """
    print("[INFO] Launching CARLA simulation...")

    # Start CARLA using your shell script
    subprocess.Popen([
        "gnome-terminal",
        "--",
        "bash",
        "-c", "./generate_simulation.sh; exec bash"
    ])

    # Wait for CARLA server to fully boot
    time.sleep(10)

    print("[✓] CARLA launched successfully.")
