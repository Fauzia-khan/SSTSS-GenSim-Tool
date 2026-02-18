#!/usr/bin/env bash
set -euo pipefail

# Optional: pull in your normal terminal env
source ~/.bashrc || true

echo $ROS_PACKAGE_PATH | tr ':' '\n'

# Source ROS and workspace
source /opt/ros/noetic/setup.bash
source "$HOME/autoware_mini_ws/devel/setup.bash"

# Debug (remove later)
echo "BASH_VERSION=${BASH_VERSION:-none}"
echo "ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH"
which roslaunch
rospack find carla_ros_bridge || true

# CARLA paths
export CARLA_ROOT="$HOME/Documents/CARLA_ROOT"
export PYTHONPATH="$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/agents"
export PYTHONPATH="$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla"

cd "$HOME/autoware_mini_ws"

# Start
exec roslaunch autoware_mini start_carla.launch map_name:=Town01 generate_traffic:=false speed_limit:=10
