#!/bin/bash
source /opt/ros/noetic/setup.bash

# Time gaps between launches (adjust if needed)
CARLA_WAIT=10
AUTOWARE_WAIT=10

echo "Starting CARLA..."
cd ~/Documents/CARLA_ROOT
./CarlaUE4.sh -prefernvidia > carla.log 2>&1 &
CARLA_PID=$!
wait $CARLA_PID

