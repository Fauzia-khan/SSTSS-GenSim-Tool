#!/bin/bash
set -e

# Proje köküne git (runandsaveplots.py burada olmalı)
cd "$HOME/Desktop/GenSim_v2"

# Source ROS and workspace
source /opt/ros/noetic/setup.bash
source ~/autoware_mini_ws/devel/setup.bash

# Export CARLA Python paths
export CARLA_ROOT="$HOME/Documents/CARLA_ROOT"
export PYTHONPATH="$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg"
export PYTHONPATH="$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/agents"
export PYTHONPATH="$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla"

python runandsaveplots.py
