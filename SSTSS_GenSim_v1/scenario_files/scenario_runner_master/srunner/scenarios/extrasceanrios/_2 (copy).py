#!/usr/bin/env python

# Copyright (c) 2019-2020 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.



#!/usr/bin/env python
#!/usr/bin/env python

import random
import threading
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
                                                                      ChangeActorTargetSpeed)
from srunner.scenariomanager.scenarioatomics.atomic_criteria import CollisionTest
from srunner.scenariomanager.scenarioatomics.atomic_trigger_conditions import InTriggerDistanceToLocation, InTriggerDistanceToNextIntersection, DriveDistance
from srunner.scenarios.basic_scenario import BasicScenario
from srunner.tools.scenario_helper import get_waypoint_in_distance


class _2(BasicScenario):

    timeout = 40

    def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True,
                 timeout=40):

        self.timeout = timeout
        self._map = CarlaDataProvider.get_map()
        self._velocity = 35
        self._delta_velocity = 10
        self._first_vehicle_location = 25
        self._first_vehicle_speed = 40
        self._traffic_light = None
        self._green_light_duration = 20 # Green for 10 seconds
        
        self._other_actor_stop_in_front_intersection = 40
        point = config.trigger_points[0].location
        self._grp = GlobalRoutePlanner(CarlaDataProvider.get_map(), 2.0)
        
        super(_2, self).__init__("_2",
                                 ego_vehicles,
                                 config,
                                 world,
                                 debug_mode,
                                 criteria_enable=criteria_enable)
        
        # Set traffic light behavior at the start
        self._traffic_light = self._find_traffic_light_near_intersection()
        self._set_traffic_light_green()

    def _initialize_actors(self, config):
        for actor in config.other_actors:
            vehicle = CarlaDataProvider.request_new_actor(actor.model, actor.transform)
            self.other_actors.append(vehicle)
            vehicle.set_simulate_physics(enabled=True)

    def _find_traffic_light_near_intersection(self):
        """
        Find the traffic light affecting the ego vehicle.
        """
        if self.ego_vehicles and self.ego_vehicles[0].is_at_traffic_light():
            return self.ego_vehicles[0].get_traffic_light()
        return None

    def _set_traffic_light_green(self):
        """
        Set the traffic light to green for 10 seconds, then turn it red.
        """
        if self._traffic_light:
            self._traffic_light.set_green_time(self._green_light_duration)
            self._traffic_light.set_red_time(30.0)
            self._traffic_light.set_yellow_time(3.0)
            self._traffic_light.set_state(carla.TrafficLightState.Green)

            # Schedule transition to red after 10 seconds
            threading.Timer(self._green_light_duration, lambda: self._traffic_light.set_state(carla.TrafficLightState.Red)).start()

    def _create_behavior(self):
        pos = self.other_actors[0].get_location()
        destpos = carla.Location(-98, -23, 0)
        plan = self._grp.trace_route(pos, destpos)

        DriveStraight = py_trees.composites.Parallel(
            "DriveStraight",
            policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE)
        DriveStraight.add_child(WaypointFollower(self.other_actors[0], 10, plan=plan))
        DriveStraight.add_child(InTriggerDistanceToLocation(
            self.ego_vehicles[0], carla.Location(-42.9, -2.7, 0), 3))

        sequence = py_trees.composites.Sequence("Sequence Behavior")
        sequence.add_child(DriveStraight)
        sequence.add_child(ActorDestroy(self.other_actors[0]))

        return sequence

    def _create_test_criteria(self):
        criteria = []
        collision_criterion = CollisionTest(self.ego_vehicles[0])
        criteria.append(collision_criterion)
        return criteria

    def __del__(self):
        self.remove_all_actors()

