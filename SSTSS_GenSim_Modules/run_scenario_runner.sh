#!/bin/bash
source /opt/ros/noetic/setup.bash

# Source ROS
source /opt/ros/noetic/setup.bash

# Source your workspaces
source ~/ali/ali_ws/devel/setup.bash
source ~/Documents/autoware_mini_ws/devel/setup.bash

# Export CARLA Python paths
export CARLA_ROOT=~/Documents/CARLA_0.9.13
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.13-py3.7-linux-x86_64.egg
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/agents
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla

source ~/Documents/autoware_mini_ws/devel/setup.bash

# Start Scenario Runner in the foreground
echo "Starting Scenario Runner..."
cd ~/Documents/scenario_runner-master
#python3.8 scenario_runner.py --scenario FollowLeadingVehicle_1 --waitForEgo --record results/test
#python3.8 scenario_runner.py \
 # --scenario FollowLeadingVehicle_1 \
  #--additionalScenario /home/laima/Documents/scenario_runner-master/srunner/scenarios/follow_leading_vehicle.py \
  #--waitForEgo \
  #--record results/test/FollowLeadingVehicle_1.log

# RECORD INTO A DIRECTORY




LOG_DIR="results/test"
mkdir -p "$LOG_DIR"

python3.8 scenario_runner.py \
  --scenario FollowLeadingVehicle_1 \
  --additionalScenario /home/laima/Documents/scenario_runner-master/srunner/scenarios/follow_leading_vehicle.py \
  --waitForEgo \
  --record "$LOG_DIR"