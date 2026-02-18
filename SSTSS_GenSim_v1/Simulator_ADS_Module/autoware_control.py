import subprocess
import time
import shlex



def launch_autoware(map_name="Town01", speed_limit=10):
    print("[INFO] Launching Autoware Mini...")

    carla_root = "$HOME/Documents/CARLA_ROOT"
    py_paths = [
        "$HOME/autoware_mini_ws/devel/lib/python3/dist-packages",
        "/opt/ros/noetic/lib/python3/dist-packages",
        f"{carla_root}/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg",
        f"{carla_root}/PythonAPI/carla/agents",
        f"{carla_root}/PythonAPI/carla",
    ]

    cmd = " && ".join([
        "source /opt/ros/noetic/setup.bash",
        "source $HOME/autoware_mini_ws/devel/setup.bash",
        f"export CARLA_ROOT={carla_root}",
        f'export PYTHONPATH="$PYTHONPATH:{":".join(py_paths)}"',
        f"roslaunch autoware_mini start_carla.launch map_name:={shlex.quote(map_name)} generate_traffic:=false speed_limit:={int(speed_limit)}",
        #"exec bash"
    ])


    subprocess.Popen(["terminator", "-e", f"bash -lc {shlex.quote(cmd)}"], start_new_session=True)

    time.sleep(7)
    print("[✓] Autoware Mini launched.")
