#!/bin/bash

# Load ROS
source /opt/ros/noetic/setup.bash

# Load your ali workspace
source ~/ali/ali_ws/devel/setup.bash

# Load Autoware Mini
source ~/Documents/autoware_mini_ws/devel/setup.bash

# Set CARLA env
export CARLA_ROOT=$HOME/Documents/CARLA_0.9.13
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.13-py3.7-linux-x86_64.egg
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/agents
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla

# Activate your project venv
source venv/bin/activate

# Run your Python app
python main.py
