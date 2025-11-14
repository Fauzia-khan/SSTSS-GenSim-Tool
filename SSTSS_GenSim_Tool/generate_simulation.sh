#!/bin/bash
source /opt/ros/noetic/setup.bash
#export PYTHONPATH=$PYTHONPATH:/path/to/CARLA/PythonAPI/carla:/path/to/CARLA/PythonAPI/carla/dist/carla-<ver>-py3.*-linux-x86_64.egg

# Time gaps between launches (adjust if needed)
CARLA_WAIT=10
AUTOWARE_WAIT=10

# Start CARLA in the background
echo "Starting CARLA..."
cd ~/Documents/CARLA_0.9.13
./CarlaUE4.sh -prefernvidia > carla.log 2>&1 &
CARLA_PID=$!
wait $CARLA_PID


# Wait for CARLA
#echo "Waiting $CARLA_WAIT seconds for CARLA to load..."
#sleep $CARLA_WAIT

# Source ROS
#source /opt/ros/noetic/setup.bash

# Source your workspaces
#source ~/ali/ali_ws/devel/setup.bash
#source ~/Documents/autoware_mini_ws/devel/setup.bash

# Export CARLA Python paths
#export CARLA_ROOT=~/Documents/CARLA_0.9.13
#export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.13-py3.7-linux-x86_64.egg
#export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/agents
#export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla

#source ~/Documents/autoware_mini_ws/devel/setup.bash
#cd ~/Documents/autoware_mini_ws
#roslaunch autoware_mini start_carla.launch map_name:=Town01 generate_traffic:=false speed_limit:=10 > autoware.log 2>&1 &


# Wait for Autoware
#echo "Waiting $AUTOWARE_WAIT seconds for Autoware to load..."
#sleep $AUTOWARE_WAIT

# Start Scenario Runner in the foreground
#echo "Starting Scenario Runner..."
#cd ~/Documents/scenario_runner-master
#python3.8 scenario_runner.py --scenario FollowLeadingVehicle_1 --waitForEgo --record results/test

