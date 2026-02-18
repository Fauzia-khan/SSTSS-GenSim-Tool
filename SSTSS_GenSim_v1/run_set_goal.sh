#!/bin/bash
set -e

echo "Starting Autoware Mini..."

# Source ROS and workspaces
source /opt/ros/noetic/setup.bash

source ~/autoware_mini_ws/devel/setup.bash

# Export CARLA Python paths
export CARLA_ROOT=~/Documents/CARLA_ROOT
#export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.13-py3.7-linux-x86_64.egg
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/agents
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla

rosrun autoware_mini set_goal.py
