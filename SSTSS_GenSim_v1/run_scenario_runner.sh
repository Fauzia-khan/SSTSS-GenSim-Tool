#!/bin/bash
source /opt/ros/noetic/setup.bash

#source "$HOME/Desktop/GenSim_v2/venv/bin/activate"

# Source your workspaces
source ~/autoware_mini_ws/devel/setup.bash

# Export CARLA Python paths
export CARLA_ROOT=/home/fauzia/Documents/CARLA_ROOT/
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/agents
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla

source ~/autoware_mini_ws/devel/setup.bash

# Start Scenario Runner in the foreground
echo "Starting Scenario Runner..."
cd ~/scenario_runner

#python3.8 scenario_runner.py --scenario FollowLeadingVehicle_1 --waitForEgo --record results/test
#python3.8 scenario_runner.py \
 # --scenario FollowLeadingVehicle_1 \
  #--additionalScenario /home/laima/Documents/scenario_runner-master/srunner/scenarios/follow_leading_vehicle.py \
  #--waitForEgo \
  #--record results/test/FollowLeadingVehicle_1.log

# RECORD INTO A DIRECTORY


LOG_DIR="results/test"
mkdir -p "$LOG_DIR"

python scenario_runner.py \
  --scenario FollowLeadingVehicle_1 \
  --additionalScenario "/home/fauzia/scenario_runner/srunner/scenarios/follow_leading_vehicle.py" \
  --waitForEgo \
  --record "$LOG_DIR"