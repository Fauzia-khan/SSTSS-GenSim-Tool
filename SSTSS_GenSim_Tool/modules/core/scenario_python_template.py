#!/usr/bin/env python

# Copyright (c) 2019-2020 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
Crossing Path scenario:
 

"""

import random
import py_trees
import carla
from agents.navigation.global_route_planner import GlobalRoutePlanner

from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.scenariomanager.scenarioatomics.atomic_behaviors import (ActorTransformSetter,
                                                                      StopVehicle,
                                                                      LaneChange,
                                                                      ActorDestroy,
                                                                      WaypointFollower,
                                                                      AccelerateToCatchUp,
                                                                      ChangeActorTargetSpeed
                                                                       
                                                                      )
from srunner.scenariomanager.scenarioatomics.atomic_criteria import CollisionTest
from srunner.scenariomanager.scenarioatomics.atomic_trigger_conditions import InTriggerDistanceToLocation, InTriggerDistanceToNextIntersection, DriveDistance
from srunner.scenarios.basic_scenario import BasicScenario
from srunner.tools.scenario_helper import get_waypoint_in_distance


class <CLASS_NAME>(BasicScenario):

    """
    T Right turn at an intersection with crossing traffic.The ego-vehicle is performing a right turn at an intersection, yielding to crossing traffic. 

    """

    timeout = <TIMEOUT>

    def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True,
                 timeout=60):

        self.timeout = timeout
        self._map = CarlaDataProvider.get_map()
        self.timeout = timeout
        self._velocity = <EGO_VEHICLE_VELOCITY>
        self._delta_velocity = 10
        self._first_vehicle_location = 25
        self._first_vehicle_speed = <OTHER_VEHICLE_VELOCITY>
        self._other_actor_stop_in_front_intersection = 10
        point = config.trigger_points[0].location
        self._grp = GlobalRoutePlanner(CarlaDataProvider.get_map(), 2.0)
        super(<CLASS_NAME>, self).__init__("<CLASS_NAME>",
                                       ego_vehicles,
                                       config,
                                       world,
                                       debug_mode,
                                       criteria_enable=criteria_enable)

    
    def _initialize_actors(self, config):

        # Spawn actor on other lane


        # transform visible
        
        print

        for actor in config.other_actors:
            vehicle = CarlaDataProvider.request_new_actor(actor.model, actor.transform)
            self.other_actors.append(vehicle)
            vehicle.set_simulate_physics(enabled=True)
        
   

    
    def _create_behavior(self):
        """
        write Order of sequence for example :
        - car_visible: spawn car at a visible transform
        - just_drive: drive until in trigger distance to ego_vehicle
        - accelerate: accelerate to catch up distance to ego_vehicle
        - lane_change: change the lane
        - endcondition: drive for a defined distance
        """
     
        sequence = py_trees.composites.Sequence("Sequence Behavior")
       
        return sequence
    def _create_test_criteria(self):
        """
        A list of all test criteria is created, which is later used in the parallel behavior tree.
        """
        criteria = []

        collision_criterion = CollisionTest(self.ego_vehicles[0])

        criteria.append(collision_criterion)

        return criteria
   
    def __del__(self):
        """
        Remove all actors after deletion.
        """
        self.remove_all_actors()
