#!/usr/bin/env python

# Copyright (c) 2020 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
This metric calculates the distance between the ego vehicle and
another actor, dumping it to a json file.

It is meant to serve as an example of how to use the information from
the recorder
"""

import math
import matplotlib.pyplot as plt

from srunner.metrics.examples.basic_metric import BasicMetric

class egovehiclevelocity(BasicMetric):
    
    def _create_metric(self, town_map, log, criteria):
        """
        Implementation of the metric. This is an example to show how to use the recorder,
        accessed via the log.
        """

        # Get the ID of the ego vehicle
        ego_id = log.get_ego_vehicle_id()

        velocity_list = []
        frames_list = []

        # Get the frames the ego vehicle was alive
        start_ego, end_ego = log.get_actor_alive_frames(ego_id)
        
         #Extract velocity for each frame
        for frame in range(start_ego, end_ego + 1):
            velocity = log.get_actor_velocity(ego_id, frame)
            if velocity:
                speed = math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2) * 3.6 # Compute magnitude
            else:
                speed = 0.0  # Default to 0 if velocity is None
            velocity_list.append(speed)
            frames_list.append(frame)
        
        # Plot velocity against frame number
        plt.figure(figsize=(10, 5))
        plt.plot(frames_list, velocity_list, label='Ego Vehicle Speed', color='b')
        plt.xlabel("Frame Number")
        plt.ylabel("Speed (m/s)")
        plt.title("Ego Vehicle speed Over Time")
        plt.legend()
        plt.grid()
        plt.show()
            

