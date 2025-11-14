import subprocess
import time

def launch_autoware():
    print("[INFO] Launching Autoware Mini...")

    cmd = (
        "source /opt/ros/noetic/setup.bash && "
        "source ~/ali/ali_ws/devel/setup.bash && "
        "source ~/Documents/autoware_mini_ws/devel/setup.bash && "
        "export CARLA_ROOT=$HOME/Documents/CARLA_0.9.13 && "
        "export PYTHONPATH=/home/laima/ali/ali_ws/devel/lib/python3/dist-packages:"
        "/home/laima/Documents/autoware_mini_ws/devel/lib/python3/dist-packages:"
        "/opt/ros/noetic/lib/python3/dist-packages:"
        "/home/laima/Documents/CARLA_0.9.13/PythonAPI/carla/dist/carla-0.9.13-py3.7-linux-x86_64.egg:"
        "/home/laima/Documents/CARLA_0.9.13/PythonAPI/carla/agents:"
        "/home/laima/Documents/CARLA_0.9.13/PythonAPI/carla && "
        "roslaunch autoware_mini start_carla.launch map_name:=Town01 generate_traffic:=false speed_limit:=10; exec bash"
    )

    subprocess.Popen([
        "terminator",
        "-e",
        f"bash -c \"{cmd}\""
    ])

    time.sleep(7)
    print("[✓] Autoware Mini launched.")
