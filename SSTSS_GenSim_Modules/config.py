import os

# --------------------
# User-editable paths
# --------------------

# Root installation directories
CARLA_ROOT = os.path.expanduser("~/Documents/CARLA_0.9.13")
SCENARIO_RUNNER_ROOT = os.path.expanduser("~/Documents/scenario_runner-master")

# ROS / Autoware paths
ROS_SETUP = "/opt/ros/noetic/setup.bash"
USER_WS_SETUP = os.path.expanduser("~/ali/ali_ws/devel/setup.bash")
AUTOWARE_WS_SETUP = os.path.expanduser("~/Documents/autoware_mini_ws/devel/setup.bash")

# --------------------
# Subdirectories
# --------------------

TOOL_ROOT = os.path.dirname(os.path.abspath(__file__))

# Save results inside Data_Collection_Module/raw_data
RESULTS_DIR = os.path.join(TOOL_ROOT, "Data_Collection_Module", "raw_data")

# Create directory if not exists
os.makedirs(RESULTS_DIR, exist_ok=True)
#RESULTS_DIR = os.path.join(SCENARIO_RUNNER_ROOT, "results", "test")
SCENARIO_XML = os.path.join(SCENARIO_RUNNER_ROOT, "srunner/examples/FollowLeadingVehicle.xml")
SCENARIO_TEMPLATE_PATH = "scenario_files/python_files/template_follow_leading_vehicle.py"

# Python module search paths
PYTHONPATH_ENTRIES = [
    USER_WS_SETUP.replace("/setup.bash", "/lib/python3/dist-packages"),
    AUTOWARE_WS_SETUP.replace("/setup.bash", "/lib/python3/dist-packages"),
    "/opt/ros/noetic/lib/python3/dist-packages",
    os.path.join(CARLA_ROOT, "PythonAPI/carla/dist/carla-0.9.13-py3.7-linux-x86_64.egg"),
    os.path.join(CARLA_ROOT, "PythonAPI/carla/agents"),
    os.path.join(CARLA_ROOT, "PythonAPI/carla")
]
# Metrics configuration
METRIC_FILE = "srunner/metrics/examples/velocity_and_distance_metric.py"
RESULTS_LOG_DIR = RESULTS_DIR