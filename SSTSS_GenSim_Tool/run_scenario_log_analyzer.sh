#!/bin/bash
set -e
cd

# Source ROS and workspaces
source /opt/ros/noetic/setup.bash
source ~/ali/ali_ws/devel/setup.bash
source ~/Documents/autoware_mini_ws/devel/setup.bash

# Export CARLA Python paths
export CARLA_ROOT=~/Documents/CARLA_0.9.13
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.13-py3.7-linux-x86_64.egg
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/agents
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla


python runandsaveplots.py
