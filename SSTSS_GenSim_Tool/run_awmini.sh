#!/bin/bash
set -e

echo "Starting Autoware Mini..."

# Source ROS and workspaces
source /opt/ros/noetic/setup.bash
source ~/ali/ali_ws/devel/setup.bash
source ~/Documents/autoware_mini_ws/devel/setup.bash

# Export CARLA Python paths
export CARLA_ROOT=~/Documents/CARLA_0.9.13
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.13-py3.7-linux-x86_64.egg
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/agents
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla

cd ~/Documents/autoware_mini_ws

# Run in background, logs go to awmini.log
roslaunch autoware_mini start_carla.launch map_name:=Town01 generate_traffic:=false speed_limit:=10 > awmini.log 2>&1 &
AUTOWARE_PID=$!

echo "Autoware Mini started with PID $AUTOWARE_PID"
