#!/usr/bin/env python

# Copyright (c) 2019-2020 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.


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

    timeout = 30

    def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True,
                 timeout=30):

        self.timeout = timeout
        self._map = CarlaDataProvider.get_map()
        self._velocity = 35
        self._delta_velocity = 10
        self._first_vehicle_location = 25
        self._first_vehicle_speed = 40
        self._traffic_light = None
        self._green_light_duration = 20  # Green for 5 seconds
        
        self._other_actor_stop_in_front_intersection = 40
        point = config.trigger_points[0].location
        self._grp = GlobalRoutePlanner(self._map, 2.0)
        
        super(_2, self).__init__("_2",
                                                      ego_vehicles,
                                                      config,
                                                      world,
                                                      debug_mode,
                                                      criteria_enable=criteria_enable)

    def _initialize_actors(self, config):
        for actor in config.other_actors:
            vehicle = CarlaDataProvider.request_new_actor(actor.model, actor.transform)
            self.other_actors.append(vehicle)
            vehicle.set_simulate_physics(enabled=True)

    def _find_traffic_light_near_intersection(self):
        """
        Find the traffic light affecting the intersection.
        """
        if not self.ego_vehicles:
            return None
            
        ego_location = self.ego_vehicles[0].get_location()
        all_lights = CarlaDataProvider.get_world().get_actors().filter('traffic.traffic_light')
        
        closest_light = None
        min_distance = float('inf')
        
        for light in all_lights:
            distance = ego_location.distance(light.get_location())
            if distance < min_distance:
                min_distance = distance
                closest_light = light
                
        return closest_light

    def _setup_traffic_light(self):
        """
        Setup the traffic light behavior
        """
        self._traffic_light = self._find_traffic_light_near_intersection()
        if self._traffic_light:
            # Set initial state to green
            self._traffic_light.set_state(carla.TrafficLightState.Green)
            self._traffic_light.set_green_time(self._green_light_duration)
            self._traffic_light.set_red_time(30.0)
            self._traffic_light.set_yellow_time(2.0)
            
            # Freeze other lights in the same group
            for light in self._traffic_light.get_group_traffic_lights():
                if light.id != self._traffic_light.id:
                    light.freeze(True)
            
            print(f"Traffic light {self._traffic_light.id} set to GREEN for {self._green_light_duration} seconds")

    def _create_behavior(self):
        # Setup traffic light first
        self._setup_traffic_light()

        # Create behavior for the other vehicle
        pos = self.other_actors[0].get_location()
        destpos = carla.Location(-98, -23, 0)
        plan = self._grp.trace_route(pos, destpos)

        drive_straight = py_trees.composites.Parallel(
            "DriveStraight",
            policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE)
        drive_straight.add_child(WaypointFollower(self.other_actors[0], 10, plan=plan))
        drive_straight.add_child(InTriggerDistanceToLocation(
            self.ego_vehicles[0], carla.Location(-42.9, -2.7, 0), 3))

        # Create sequence for traffic light change
        traffic_light_sequence = py_trees.composites.Sequence("TrafficLightSequence")
        
        # Wait for green duration
        traffic_light_sequence.add_child(py_trees.timers.Timer(
            duration=self._green_light_duration,
            name="GreenLightTimer"))
        
        # Then change to red (using a custom behavior)
        class ChangeTrafficLightToRed(py_trees.behaviour.Behaviour):
            def __init__(self, traffic_light):
                super(ChangeTrafficLightToRed, self).__init__("ChangeToRed")
                self.traffic_light = traffic_light
            
            def update(self):
                if self.traffic_light:
                    self.traffic_light.set_state(carla.TrafficLightState.Red)
                    print(f"Traffic light {self.traffic_light.id} changed to RED")
                return py_trees.common.Status.SUCCESS

        traffic_light_sequence.add_child(ChangeTrafficLightToRed(self._traffic_light))

        # Combine everything
        root = py_trees.composites.Parallel(
            "Root",
            policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE)
        
        root.add_child(traffic_light_sequence)
        root.add_child(drive_straight)

        sequence = py_trees.composites.Sequence("MainSequence")
        sequence.add_child(root)
        sequence.add_child(ActorDestroy(self.other_actors[0]))

        return sequence

    def _create_test_criteria(self):
        criteria = []
        collision_criterion = CollisionTest(self.ego_vehicles[0])
        criteria.append(collision_criterion)
        return criteria

    def __del__(self):
        # Reset traffic light to default behavior when scenario ends
        if self._traffic_light:
            for light in self._traffic_light.get_group_traffic_lights():
                light.freeze(False)
        self.remove_all_actors()
