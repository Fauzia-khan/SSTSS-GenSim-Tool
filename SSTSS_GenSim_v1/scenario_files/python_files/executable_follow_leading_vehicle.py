#!/usr/bin/env python

# Copyright (c) 2018-2020 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

timeout = 0
other_vehicle_distance = 0
other_vehicle_speed =  0

import py_trees
import carla
import time
import os
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.scenarios.basic_scenario import BasicScenario
from srunner.tools.scenario_helper import get_waypoint_in_distance
from srunner.scenariomanager.scenarioatomics.atomic_criteria import CollisionTest
from srunner.scenariomanager.scenarioatomics.atomic_behaviors import Idle


class FollowLeadingVehicle(BasicScenario):

    def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True, timeout=timeout):
        self._map = CarlaDataProvider.get_map()
        self._lead_start_distance = other_vehicle_distance ## previously 10
        self._lead_speed = other_vehicle_speed # km/h
 

        self._reference_waypoint = self._map.get_waypoint(config.trigger_points[0].location)
        self.timeout = timeout

        super(FollowLeadingVehicle, self).__init__("FollowLeadVehicle",
                                                   ego_vehicles,
                                                   config,
                                                   world,
                                                   debug_mode,
                                                   criteria_enable=criteria_enable)

    def _initialize_actors(self, config):
        waypoint, _ = get_waypoint_in_distance(self._reference_waypoint, self._lead_start_distance)
        transform = waypoint.transform
        transform.location.z += 0.5
        lead_vehicle = CarlaDataProvider.request_new_actor('vehicle.nissan.patrol', transform)
        self.other_actors.append(lead_vehicle)

    def _create_behavior(self):
        lead = self.other_actors[0]
        ego = self.ego_vehicles[0]

        controller = LeadVehicleController(
            lead_vehicle=lead,
            target_speed_mps=self._lead_speed / 3.6,
            brake_distances=[80], # Start braking after 100 meters
            wait_time=25.0
        )

        infinite_wait = Idle(name="KeepScenarioAlive")
        scenario = py_trees.composites.Sequence("LeadVehicleScenario")
        scenario.add_child(controller)
        scenario.add_child(infinite_wait)

        return scenario

    def _create_test_criteria(self):
        return [CollisionTest(self.ego_vehicles[0])]

    def __del__(self):
        self.remove_all_actors()


class LeadVehicleController(py_trees.behaviour.Behaviour):
    def __init__(self, lead_vehicle, target_speed_mps, brake_distances, wait_time=5.0, name="LeadVehicleController"):
        super(LeadVehicleController, self).__init__(name)
        self.lead_vehicle = lead_vehicle
        self.target_speed = target_speed_mps
        self.brake_distances = sorted(brake_distances)
        self.wait_time = wait_time

        self._initial_location = None
        self._current_stop_index = 0
        self._braking = False
        self._wait_start_time = None
        self._running = False
        self._restarting = False

        self._brake_start_time = None
        self._brake_phase_started = False
        self._reaction_time = 0.7
        self._mu = 0.9
        self._g = 9.81
        self._initial_speed = self.target_speed
        self._required_deceleration = None

        # [Smooth Start]
        self._startup = True
        self._start_time = None
        self._acceleration = 1.5  # m/s²
        self._current_speed = 0.0  # smoothing base
        self._smoothing_factor = 0.1  # between 0 and 1

    def initialise(self):
        self._initial_location = self.lead_vehicle.get_location()
        self._current_stop_index = 0
        self._braking = False
        self._wait_start_time = None
        self._running = True
        self._restarting = False
        self._brake_start_time = None
        self._brake_phase_started = False
        self._initial_speed = self.target_speed
        self._required_deceleration = None

        self._startup = True
        self._start_time = time.time()
        self._current_speed = 0.0

        print(f"[LeadVehicleController] Initialized at {self._initial_location}")

    def update(self):
        if not self._running:
            return py_trees.common.Status.FAILURE

        current_time = time.time()

        # [Smooth Acceleration Phase]
        if self._startup:
            elapsed = current_time - self._start_time
            raw_speed = min(self.target_speed, self._acceleration * elapsed)  #   V=at, linear accealaration,Calculating raw speed when starting

            # [Smooth the transition to avoid jitter]
            self._current_speed += self._smoothing_factor * (raw_speed - self._current_speed)  #  V=Vcurrent _alpha*(Vraw-Vcurrent), Smooth speed ramp-up

            forward = self.lead_vehicle.get_transform().get_forward_vector()
            velocity = carla.Vector3D(forward.x * self._current_speed,
                                      forward.y * self._current_speed,
                                      forward.z * self._current_speed)
            self.lead_vehicle.set_target_velocity(velocity)

            if self._current_speed >= self.target_speed - 0.1:
                self._startup = False
                self._current_speed = self.target_speed
                print(f"[LeadVehicleController] Reached cruising speed smoothly: {self._current_speed:.2f} m/s")

            return py_trees.common.Status.RUNNING

        if self._current_stop_index >= len(self.brake_distances):
            self._set_velocity(self.target_speed)
            return py_trees.common.Status.RUNNING

        current_location = self.lead_vehicle.get_location()    #  Monitor Distance During Driving
        distance_traveled = current_location.distance(self._initial_location)
        next_brake_distance = self.brake_distances[self._current_stop_index]

        if not self._braking and distance_traveled >= next_brake_distance:
            print(f"[LeadVehicleController] Triggering braking at {next_brake_distance} m!")
            self._braking = True
            self._brake_start_time = None
            self._brake_phase_started = False
            self._initial_speed = self.target_speed
            return py_trees.common.Status.RUNNING

        if self._braking and not self._restarting:
            if self._brake_start_time is None:
                self._brake_start_time = current_time

            elapsed = current_time - self._brake_start_time

            if elapsed < self._reaction_time:   #The vehicle doesn’t brake immediately. some delay due to reaction
                self._set_velocity(self.target_speed)   # Keep moving with same speed speed
            else:
                if not self._brake_phase_started:
                    self._brake_phase_started = True
                    braking_distance = (self._initial_speed ** 2) / (2 * self._mu * self._g)  #once the reaction time is over than start slwoing down
                    self._required_deceleration = self._mu * self._g #Max deceleration
                    print(f"[LeadVehicleController] Starting braking... braking_distance={braking_distance:.2f} m, deceleration={self._required_deceleration:.2f} m/s²")

                braking_elapsed = elapsed - self._reaction_time  #how long you've been braking
                current_speed = max(0.0, self._initial_speed - self._required_deceleration * braking_elapsed)  #v=v0−a⋅t uniform deaccearation

                self._set_velocity(current_speed, apply_brake=True)

                if current_speed <= 0.2:
                    print("[LeadVehicleController] Vehicle stopped. Waiting...")
                    self.lead_vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))
                    self._wait_start_time = current_time
                    self._restarting = True

            return py_trees.common.Status.RUNNING

        if self._restarting:
            elapsed = current_time - self._wait_start_time
            if elapsed >= self.wait_time:
                print("[LeadVehicleController] Resuming motion.")
                self.lead_vehicle.apply_control(carla.VehicleControl(brake=0.0))
                self._initial_location = self.lead_vehicle.get_location()
                self._braking = False
                self._restarting = False
                self._wait_start_time = None
                self._brake_start_time = None
                self._brake_phase_started = False
                self._initial_speed = self.target_speed
                self._current_stop_index += 1

            return py_trees.common.Status.RUNNING

        self._set_velocity(self.target_speed)
        return py_trees.common.Status.RUNNING

    def _set_velocity(self, speed, apply_brake=False):
        self._current_speed += self._smoothing_factor * (speed - self._current_speed)
        forward = self.lead_vehicle.get_transform().get_forward_vector()
        velocity = carla.Vector3D(forward.x * self._current_speed,
                                  forward.y * self._current_speed,
                                  forward.z * self._current_speed)
        self.lead_vehicle.set_target_velocity(velocity)
        if apply_brake:
            brake_ratio = min(1.0, self._required_deceleration / (self._mu * self._g))
            self.lead_vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=brake_ratio))

    def terminate(self, new_status):
        print("[LeadVehicleController] Terminated.")
        self._running = False






####### running code with accealration and deacearaltion, but the car is not going straight.
# import py_trees
# import carla
# import time
# from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
# from srunner.scenarios.basic_scenario import BasicScenario
# from srunner.tools.scenario_helper import get_waypoint_in_distance
# from srunner.scenariomanager.scenarioatomics.atomic_criteria import CollisionTest


# class FollowLeadingVehicle(BasicScenario):
#     timeout = 120

#     def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True, timeout=70):
#         self._map = CarlaDataProvider.get_map()
#         self._reference_waypoint = self._map.get_waypoint(config.trigger_points[0].location)
#         self.timeout = timeout
#         super().__init__("FollowLeadVehicle", ego_vehicles, config, world, debug_mode, criteria_enable=criteria_enable)

#     def _initialize_actors(self, config):
#         waypoint, _ = get_waypoint_in_distance(self._reference_waypoint, 10)
#         transform = waypoint.transform
#         transform.location.z += 0.5
#         lead_vehicle = CarlaDataProvider.request_new_actor('vehicle.nissan.patrol', transform)
#         self.other_actors.append(lead_vehicle)

#     def _create_behavior(self):
#         behavior = py_trees.composites.Sequence("Lead Vehicle Behavior")
#         behavior.add_child(LeadVehicleController(self.other_actors[0]))
#         return behavior

#     def _create_test_criteria(self):
#         return [CollisionTest(self.ego_vehicles[0])]

# class LeadVehicleController(py_trees.behaviour.Behaviour):
#     def __init__(self, vehicle, lead_speed_kmh=20, stop_trigger_distance=40.0, name="LeadVehicleController"):
#         super().__init__(name)
#         self.vehicle = vehicle
#         self._lead_speed = lead_speed_kmh / 3.6  # km/h to m/s
#         self._trigger_distance = stop_trigger_distance

#         self._acceleration = 1.5  # m/s²
#         self._safe_deceleration = 0.8  # m/s², realistic and smooth

#         self._braking_duration = 2.5  # seconds

#         self._phase = "accelerate"
#         self._start_time = None
#         self._current_speed = 0.0
#         self._initial_location = None
#         self._brake_start_time = None
#         self._wait_start_time = None
#         self._brake_initial_speed = None

#     def initialise(self):
#         self._start_time = time.time()
#         self._phase = "accelerate"
#         self._current_speed = 0.0
#         self._initial_location = self.vehicle.get_location()
#         self._brake_start_time = None
#         self._wait_start_time = None
#         self._brake_initial_speed = None
#         print("[LeadVehicleController] Initialized")

#     def update(self):
#         current_time = time.time()

#         if self._phase == "accelerate":
#             elapsed = current_time - self._start_time
#             self._current_speed = min(self._lead_speed, self._acceleration * elapsed)
#             self._apply_velocity(self._current_speed)

#             if self._current_speed >= self._lead_speed - 0.1:
#                 self._phase = "cruise"
#                 print("[LeadVehicleController] Cruising at target speed")

#         elif self._phase == "cruise":
#             self._apply_throttle_capped()
#             current_location = self.vehicle.get_location()
#             distance = current_location.distance(self._initial_location)

#             if distance >= self._trigger_distance:
#                 self._phase = "brake"
#                 self._brake_start_time = current_time
#                 self._brake_initial_speed = self._lead_speed
#                 print(f"[LeadVehicleController] Triggering brake after {self._trigger_distance} m")

#         elif self._phase == "brake":
#             elapsed = current_time - self._brake_start_time
#             deceleration = self._safe_deceleration  # e.g., 1.8 m/s²
#             braking_speed = max(0.0, self._brake_initial_speed - deceleration * elapsed)
            

#             control = carla.VehicleControl(
#                 throttle=0.0,
#                 brake=0.0,
#                 steer=0.0
#             )
#             if braking_speed > 0.1:
#                 control.brake = min(1.0, (self._brake_initial_speed - braking_speed) / self._brake_initial_speed)
#                 print(f"[Braking] Speed: {braking_speed:.2f} m/s | Brake: {control.brake:.2f}")
#             else:
#                control.brake = 1.0
#                self._phase = "wait"
#                self._wait_start_time = current_time
#                print("[LeadVehicleController] Fully stopped.")
#             self.vehicle.apply_control(control)

#             if braking_speed >= 1.0:
#                 self.vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0, steer=0.0))
#                 self._phase = "wait"
#                 self._wait_start_time = current_time
#                 print("[LeadVehicleController] Full stop reached")

#         elif self._phase == "wait":
#             if (current_time - self._wait_start_time) >= 1.0:
#                 self._phase = "resume"
#                 self._start_time = current_time
#                 self._current_speed = 0.0
#                 print("[LeadVehicleController] Resuming motion")

#         elif self._phase == "resume":
#             elapsed = current_time - self._start_time
#             self._current_speed = min(self._lead_speed, self._acceleration * elapsed)
#             self._apply_velocity(self._current_speed)

#             if self._current_speed >= self._lead_speed - 0.1:
#                 self._phase = "final_cruise"
#                 print("[LeadVehicleController] Final cruise started")

#         elif self._phase == "final_cruise":
#             self._apply_throttle_capped()

#         return py_trees.common.Status.RUNNING

#     def _apply_velocity(self, speed):
#         forward = self.vehicle.get_transform().get_forward_vector()
#         velocity = carla.Vector3D(forward.x * speed, forward.y * speed, forward.z * speed)
#         self.vehicle.set_target_velocity(velocity)

#         control = carla.VehicleControl(
#             throttle=0.5,
#             brake=0.0,
#             steer=0.0
#         )
#         self.vehicle.apply_control(control)

#     def _apply_throttle_capped(self):
#         velocity = self.vehicle.get_velocity()
#         current_speed = math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)

#         speed_error = self._lead_speed - current_speed
#         control = carla.VehicleControl()
#         control.steer = 0.0
#         Kp=0.9

#         if speed_error > 0.1:
#         # Speed is too low → accelerate
#          control.throttle = min(1.0, Kp * speed_error)
#          control.brake = 0.0
#         elif speed_error < -0.1:
#         # Speed too high → gently brake
#          control.throttle = 0.0
#          control.brake = min(1.0, Kp * abs(speed_error))
#         else:
#         # Hold
#          control.throttle = 0.2
#          control.brake = 0.0

#         self.vehicle.apply_control(control)

#     def terminate(self, new_status):
#         print("[LeadVehicleController] Terminated.")



##uptothis one

# class LeadVehicleController(py_trees.behaviour.Behaviour):
#     def __init__(self, lead_vehicle, target_speed_mps, brake_distances, wait_time=5.0, name="LeadVehicleController"):
#         super(LeadVehicleController, self).__init__(name)
#         self.lead_vehicle = lead_vehicle
#         self.speed = target_speed_mps
#         self.brake_distances = sorted(brake_distances)
#         self.wait_time = wait_time

#         self._initial_location = None
#         self._current_stop_index = 0
#         self._braking = False
#         self._wait_start_time = None
#         self._running = False
#         self._restarting = False

#         self._brake_start_time = None
#         self._current_speed = target_speed_mps

#         # Physics constants
#         self._mu = 0.9
#         self._g = 9.81
#         self._reaction_time = 0.7
#         self._brake_phase_started = False

#     def initialise(self):
#         self._initial_location = self.lead_vehicle.get_location()
#         self._current_stop_index = 0
#         self._braking = False
#         self._wait_start_time = None
#         self._running = True
#         self._restarting = False
#         self._brake_start_time = None
#         self._brake_phase_started = False
#         self._current_speed = self.speed
#         print(f"[LeadVehicleController] Initialized at {self._initial_location}")

#     def update(self):
#         if not self._running:
#             return py_trees.common.Status.FAILURE

#         if self._current_stop_index >= len(self.brake_distances):
#             forward = self.lead_vehicle.get_transform().get_forward_vector()
#             velocity = carla.Vector3D(forward.x * self.speed,
#                                       forward.y * self.speed,
#                                       forward.z * self.speed)
#             self.lead_vehicle.set_target_velocity(velocity)
#             return py_trees.common.Status.RUNNING

#         current_location = self.lead_vehicle.get_location()
#         distance_traveled = current_location.distance(self._initial_location)
#         print(f"[LeadVehicleController] Distance traveled: {distance_traveled:.2f} m")

#         next_brake_distance = self.brake_distances[self._current_stop_index]

#         if not self._braking and distance_traveled >= next_brake_distance:
#             print(f"[LeadVehicleController] Triggering braking at {next_brake_distance} m!")
#             self._braking = True
#             self._brake_start_time = None
#             self._brake_phase_started = False
#             return py_trees.common.Status.RUNNING

#         if self._braking and not self._restarting:
#             if self._brake_start_time is None:
#                 self._brake_start_time = time.time()

#             elapsed = time.time() - self._brake_start_time

#             if elapsed < self._reaction_time:
#                 # Phase 1: Reaction delay
#                 forward = self.lead_vehicle.get_transform().get_forward_vector()
#                 velocity = carla.Vector3D(forward.x * self.speed,
#                                           forward.y * self.speed,
#                                           forward.z * self.speed)
#                 self.lead_vehicle.set_target_velocity(velocity)
#                 print(f"[LeadVehicleController] Reaction time: coasting ({elapsed:.2f}s)")
#             else:
#                 # Phase 2: Physics-based braking
#                 if not self._brake_phase_started:
#                     self._brake_phase_started = True
#                     print("[LeadVehicleController] Starting braking based on physics")

#                 velocity = self.lead_vehicle.get_velocity()
#                 speed_mps = (velocity.x**2 + velocity.y**2 + velocity.z**2) ** 0.5

#                 if speed_mps > 0.2:
#                     brake_force = min(1.0, self._mu)
#                     #brake_force = min(1.0, desired_deceleration / (mu * g))
#                     self.lead_vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=brake_force))
#                     print(f"[LeadVehicleController] Braking... speed={speed_mps:.2f} m/s, brake={brake_force:.2f}")
#                 else:
#                     print("[LeadVehicleController] Vehicle stopped. Waiting...")
#                     self.lead_vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))
#                     self._wait_start_time = time.time()
#                     self._restarting = True

#             return py_trees.common.Status.RUNNING

#         if self._restarting:
#             elapsed = time.time() - self._wait_start_time
#             if elapsed >= self.wait_time:
#                 print("[LeadVehicleController] Resuming motion.")
#                 forward = self.lead_vehicle.get_transform().get_forward_vector()
#                 velocity = carla.Vector3D(forward.x * self.speed,
#                                           forward.y * self.speed,
#                                           forward.z * self.speed)
#                 self.lead_vehicle.apply_control(carla.VehicleControl(brake=0.0))
#                 self.lead_vehicle.set_target_velocity(velocity)

#                 self._braking = False
#                 self._restarting = False
#                 self._wait_start_time = None
#                 self._brake_start_time = None
#                 self._brake_phase_started = False
#                 self._current_speed = self.speed
#                 self._initial_location = current_location
#                 self._current_stop_index += 1

#             return py_trees.common.Status.RUNNING

#         # Default forward motion
#         if not self._braking:
#             forward = self.lead_vehicle.get_transform().get_forward_vector()
#             velocity = carla.Vector3D(forward.x * self.speed,
#                                       forward.y * self.speed,
#                                       forward.z * self.speed)
#             self.lead_vehicle.set_target_velocity(velocity)

#         return py_trees.common.Status.RUNNING

#     def terminate(self, new_status):
#         print("[LeadVehicleController] Terminated.")
#         self._running = False






####running code###3
# class FollowLeadingVehicle(BasicScenario):

#     timeout = 120

#     def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True, timeout=110):
#         self._map = CarlaDataProvider.get_map()
#         H
#         self._lead_speed = 20  # km/h
#         self._brake_trigger_distance = (self._lead_speed ** 2) / (2 * 0.7 * 0.9)
#         self._reference_waypoint = self._map.get_waypoint(config.trigger_points[0].location)
#         self.timeout = timeout

#         super(FollowLeadingVehicle, self).__init__("FollowLeadVehicle",
#                                                    ego_vehicles,
#                                                    config,
#                                                    world,
#                                                    debug_mode,
#                                                    criteria_enable=criteria_enable)

#     def _initialize_actors(self, config):
#         waypoint, _ = get_waypoint_in_distance(self._reference_waypoint, self._lead_start_distance)
#         transform = waypoint.transform
#         transform.location.z += 0.5
#         lead_vehicle = CarlaDataProvider.request_new_actor('vehicle.nissan.patrol', transform)
#         self.other_actors.append(lead_vehicle)

#     def _create_behavior(self):
#         lead = self.other_actors[0]
#         ego = self.ego_vehicles[0]

#         controller = LeadVehicleController(
#             lead_vehicle=lead,
#             target_speed_mps=self._lead_speed / 3.6,
#             brake_distances=[60],
#             wait_time=7.0
#         )

#         infinite_wait = Idle(name="KeepScenarioAlive")
#         scenario = py_trees.composites.Sequence("LeadVehicleScenario")
#         scenario.add_child(controller)
#         scenario.add_child(infinite_wait)

#         return scenario

#     def _create_test_criteria(self):
#         return [CollisionTest(self.ego_vehicles[0])]

#     def __del__(self):
#         self.remove_all_actors()


# import py_trees
# import carla
# import time

# class LeadVehicleController(py_trees.behaviour.Behaviour):
#     def __init__(self, lead_vehicle, target_speed_mps, brake_distances, wait_time=5.0, name="LeadVehicleController"):
#         super(LeadVehicleController, self).__init__(name)
#         self.lead_vehicle = lead_vehicle
#         self.speed = target_speed_mps
#         self.brake_distances = sorted(brake_distances)
#         self.wait_time = wait_time

#         self._initial_location = None
#         self._current_stop_index = 0
#         self._braking = False
#         self._wait_start_time = None
#         self._running = False
#         self._restarting = False

#         self._brake_start_time = None
#         self._current_speed = target_speed_mps
#         self._deceleration_rate = 1.5  # m/s^2

#     def initialise(self):
#         self._initial_location = self.lead_vehicle.get_location()
#         self._current_stop_index = 0
#         self._braking = False
#         self._wait_start_time = None
#         self._running = True
#         self._restarting = False
#         self._brake_start_time = None
#         self._current_speed = self.speed
#         print(f"[LeadVehicleController] Initialized at {self._initial_location}")

#     def update(self):
#         if not self._running:
#             return py_trees.common.Status.FAILURE

#         if self._current_stop_index >= len(self.brake_distances):
#             forward = self.lead_vehicle.get_transform().get_forward_vector()
#             velocity = carla.Vector3D(forward.x * self.speed,
#                                       forward.y * self.speed,
#                                       forward.z * self.speed)
#             self.lead_vehicle.set_target_velocity(velocity)
#             return py_trees.common.Status.RUNNING

#         current_location = self.lead_vehicle.get_location()
#         distance_traveled = current_location.distance(self._initial_location)
#         print(f"[LeadVehicleController] Distance traveled: {distance_traveled:.2f} m")

#         next_brake_distance = self.brake_distances[self._current_stop_index]

#         if not self._braking and distance_traveled >= next_brake_distance:
#             print(f"[LeadVehicleController] Starting gradual braking at {next_brake_distance} m!")
#             self._braking = True
#             self._brake_start_time = None
#             self._current_speed = self.speed
#             return py_trees.common.Status.RUNNING

#         if self._braking and not self._restarting:
#             if self._brake_start_time is None:
#                 self._brake_start_time = time.time()

#             time_elapsed = time.time() - self._brake_start_time
#             decel = self._deceleration_rate * time_elapsed
#             self._current_speed = max(0.0, self.speed - decel)

#             print(f"[LeadVehicleController] Decelerating... Speed: {self._current_speed:.2f} m/s")

#             forward = self.lead_vehicle.get_transform().get_forward_vector()
#             velocity = carla.Vector3D(forward.x * self._current_speed,
#                                       forward.y * self._current_speed,
#                                       forward.z * self._current_speed)
#             self.lead_vehicle.set_target_velocity(velocity)

#             if self._current_speed <= 0.3:
#                 print("[LeadVehicleController] Vehicle stopped. Waiting...")
#                 self.lead_vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=0.7))
#                 self.lead_vehicle.set_target_velocity(carla.Vector3D(0, 0, 0))
#                 if self._wait_start_time is None:
#                     self._wait_start_time = time.time()
#                 self._restarting = True

#                 return py_trees.common.Status.RUNNING

#         if self._restarting:
#             elapsed = time.time() - self._wait_start_time
#             if elapsed >= self.wait_time:
#                 print("[LeadVehicleController] Resuming motion.")
#                 forward = self.lead_vehicle.get_transform().get_forward_vector()
#                 velocity = carla.Vector3D(forward.x * self.speed,
#                                           forward.y * self.speed,
#                                           forward.z * self.speed)
#                 self.lead_vehicle.apply_control(carla.VehicleControl(brake=0.0))
#                 self.lead_vehicle.set_target_velocity(velocity)

#                 self._braking = False
#                 self._restarting = False
#                 self._wait_start_time = None
#                 self._brake_start_time = None
#                 self._current_speed = self.speed
#                 self._initial_location = current_location  # Reset for next segment
#                 self._current_stop_index += 1

#             return py_trees.common.Status.RUNNING

#         # Regular motion
#         if not self._braking:
#             forward = self.lead_vehicle.get_transform().get_forward_vector()
#             velocity = carla.Vector3D(forward.x * self.speed,
#                                       forward.y * self.speed,
#                                       forward.z * self.speed)
#             self.lead_vehicle.set_target_velocity(velocity)

#         return py_trees.common.Status.RUNNING

#     def terminate(self, new_status):
#         print("[LeadVehicleController] Terminated.")
#         self._running = False

####################form above

    # def _create_behavior(self):
    #     lead = self.other_actors[0]
    #     ego = self.ego_vehicles[0]

    #     controller = LeadVehicleController(
    #     lead,
    #     target_speed_mps=self._lead_speed / 3.6,
    #     brake_after_distance_meters=80  # lead car will brake after 30m
    # )
    #     stop_check = py_trees.composites.Parallel("WaitForStop",policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ALL)
    #     stop_check.add_child(StandStill(ego, name="EgoStop", duration=1))
    #     sequence = py_trees.composites.Sequence("LeadVehicleScenario")
    #     sequence.add_child(controller)
    #     sequence.add_child(stop_check)
    #     #sequence.add_child(ActorDestroy(lead))
    #     return sequence
# class LeadVehicleController(py_trees.behaviour.Behaviour):
#     def __init__(self, lead_vehicle, target_speed_mps, brake_after_distance_meters, name="LeadVehicleController"):
#         super(LeadVehicleController, self).__init__(name)
#         self.lead_vehicle = lead_vehicle
#         self.speed = target_speed_mps
#         self.brake_distance = brake_after_distance_meters
#         self._initial_location = None
#         self._braking = False
#         self._running = False

#     def initialise(self):
#         self._running = True
#         self._braking = False
#         self._initial_location = self.lead_vehicle.get_location()
#         print(f"[LeadVehicleController] Lead vehicle starts at {self._initial_location}")

#     def update(self):
#         if not self._running:
#             return py_trees.common.Status.FAILURE

#         current_location = self.lead_vehicle.get_location()
#         distance_traveled = current_location.distance(self._initial_location)
#         print(f"[LeadVehicleController] Distance traveled: {distance_traveled:.2f} m")

#         if not self._braking and distance_traveled >= self.brake_distance:
#             print("[LeadVehicleController] Brake triggered!")
#             self.lead_vehicle.set_target_velocity(carla.Vector3D(0, 0, 0))
#             self.lead_vehicle.apply_control(carla.VehicleControl(brake=1.0))
#             self._braking = True
#             return py_trees.common.Status.SUCCESS

#         if not self._braking:
#             forward = self.lead_vehicle.get_transform().get_forward_vector()
#             velocity = carla.Vector3D(forward.x * self.speed,
#                                       forward.y * self.speed,
#                                       forward.z * self.speed)
#             self.lead_vehicle.set_target_velocity(velocity)

#         return py_trees.common.Status.RUNNING

#     def terminate(self, new_status):
#         print("[LeadVehicleController] Finished.")
#         self._running = False
class FollowLeadingVehicleWithObstacle(BasicScenario):

    """
    This class holds a scenario similar to FollowLeadingVehicle
    but there is an obstacle in front of the leading vehicle

    This is a single ego vehicle scenario
    """

    timeout = 120            # Timeout of scenario in seconds

    def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True):
        """
        Setup all relevant parameters and create scenario
        """
        self._map = CarlaDataProvider.get_map()
        self._first_actor_location = 25
        self._second_actor_location = self._first_actor_location + 41
        self._first_actor_speed = 10
        self._second_actor_speed = 1.5
        self._reference_waypoint = self._map.get_waypoint(config.trigger_points[0].location)
        self._other_actor_max_brake = 1.0
        self._first_actor_transform = None
        self._second_actor_transform = None

        super(FollowLeadingVehicleWithObstacle, self).__init__("FollowLeadingVehicleWithObstacle",
                                                               ego_vehicles,
                                                               config,
                                                               world,
                                                               debug_mode,
                                                               criteria_enable=criteria_enable)
        if randomize:
            self._ego_other_distance_start = random.randint(4, 8)

    def _initialize_actors(self, config):
        """
        Custom initialization
        """

        first_actor_waypoint, _ = get_waypoint_in_distance(self._reference_waypoint, self._first_actor_location)
        second_actor_waypoint, _ = get_waypoint_in_distance(self._reference_waypoint, self._second_actor_location)
        first_actor_transform = carla.Transform(
            carla.Location(first_actor_waypoint.transform.location.x,
                           first_actor_waypoint.transform.location.y,
                           first_actor_waypoint.transform.location.z - 500),
            first_actor_waypoint.transform.rotation)
        self._first_actor_transform = carla.Transform(
            carla.Location(first_actor_waypoint.transform.location.x,
                           first_actor_waypoint.transform.location.y,
                           first_actor_waypoint.transform.location.z + 1),
            first_actor_waypoint.transform.rotation)
        yaw_1 = second_actor_waypoint.transform.rotation.yaw + 90
        second_actor_transform = carla.Transform(
            carla.Location(second_actor_waypoint.transform.location.x,
                           second_actor_waypoint.transform.location.y,
                           second_actor_waypoint.transform.location.z - 500),
            carla.Rotation(second_actor_waypoint.transform.rotation.pitch, yaw_1,
                           second_actor_waypoint.transform.rotation.roll))
        self._second_actor_transform = carla.Transform(
            carla.Location(second_actor_waypoint.transform.location.x,
                           second_actor_waypoint.transform.location.y,
                           second_actor_waypoint.transform.location.z + 1),
            carla.Rotation(second_actor_waypoint.transform.rotation.pitch, yaw_1,
                           second_actor_waypoint.transform.rotation.roll))

        first_actor = CarlaDataProvider.request_new_actor(
            'vehicle.nissan.patrol', first_actor_transform)
        second_actor = CarlaDataProvider.request_new_actor(
            'vehicle.diamondback.century', second_actor_transform)

        first_actor.set_simulate_physics(enabled=False)
        second_actor.set_simulate_physics(enabled=False)
        self.other_actors.append(first_actor)
        self.other_actors.append(second_actor)

    def _create_behavior(self):
        """
        The scenario defined after is a "follow leading vehicle" scenario. After
        invoking this scenario, it will wait for the user controlled vehicle to
        enter the start region, then make the other actor to drive towards obstacle.
        Once obstacle clears the road, make the other actor to drive towards the
        next intersection. Finally, the user-controlled vehicle has to be close
        enough to the other actor to end the scenario.
        If this does not happen within 60 seconds, a timeout stops the scenario
        """

        # let the other actor drive until next intersection
        driving_to_next_intersection = py_trees.composites.Parallel(
            "Driving towards Intersection",
            policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE)

        obstacle_clear_road = py_trees.composites.Parallel("Obstalce clearing road",
                                                           policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE)
        obstacle_clear_road.add_child(DriveDistance(self.other_actors[1], 4))
        obstacle_clear_road.add_child(KeepVelocity(self.other_actors[1], self._second_actor_speed))

        stop_near_intersection = py_trees.composites.Parallel(
            "Waiting for end position near Intersection",
            policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE)
        stop_near_intersection.add_child(WaypointFollower(self.other_actors[0], 10))
        stop_near_intersection.add_child(InTriggerDistanceToNextIntersection(self.other_actors[0], 20))

        driving_to_next_intersection.add_child(WaypointFollower(self.other_actors[0], self._first_actor_speed))
        driving_to_next_intersection.add_child(InTriggerDistanceToVehicle(self.other_actors[1],
                                                                          self.other_actors[0], 15))

        # end condition
        endcondition = py_trees.composites.Parallel("Waiting for end position",
                                                    policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ALL)
        endcondition_part1 = InTriggerDistanceToVehicle(self.other_actors[0],
                                                        self.ego_vehicles[0],
                                                        distance=20,
                                                        name="FinalDistance")
        endcondition_part2 = StandStill(self.ego_vehicles[0], name="FinalSpeed", duration=1)
        endcondition.add_child(endcondition_part1)
        endcondition.add_child(endcondition_part2)

        # Build behavior tree
        sequence = py_trees.composites.Sequence("Sequence Behavior")
        sequence.add_child(ActorTransformSetter(self.other_actors[0], self._first_actor_transform))
        sequence.add_child(ActorTransformSetter(self.other_actors[1], self._second_actor_transform))
        sequence.add_child(driving_to_next_intersection)
        sequence.add_child(StopVehicle(self.other_actors[0], self._other_actor_max_brake))
        sequence.add_child(TimeOut(3))
        sequence.add_child(obstacle_clear_road)
        sequence.add_child(stop_near_intersection)
        sequence.add_child(StopVehicle(self.other_actors[0], self._other_actor_max_brake))
        sequence.add_child(endcondition)
        sequence.add_child(ActorDestroy(self.other_actors[0]))
        sequence.add_child(ActorDestroy(self.other_actors[1]))

        return sequence

    def _create_test_criteria(self):
        """
        A list of all test criteria will be created that is later used
        in parallel behavior tree.
        """
        criteria = []

        collision_criterion = CollisionTest(self.ego_vehicles[0])

        criteria.append(collision_criterion)

        return criteria

    def __del__(self):
        """
        Remove all actors upon deletion
        """
        self.remove_all_actors()


class FollowLeadingVehicleRoute(BasicScenario):

    """
    This class is the route version of FollowLeadingVehicle where the backgrounda activity is used,
    instead of spawning a specific vehicle and making it brake.

    This is a single ego vehicle scenario
    """

    timeout = 120            # Timeout of scenario in seconds

    def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True,
                 timeout=60):
        """
        Setup all relevant parameters and create scenario
        """
        self.timeout = timeout
        self._stop_duration = 15
        self._end_time_condition = 30

        super(FollowLeadingVehicleRoute, self).__init__("FollowLeadingVehicleRoute",
                                                        ego_vehicles,
                                                        config,
                                                        world,
                                                        debug_mode,
                                                        criteria_enable=criteria_enable)

    def _initialize_actors(self, config):
        """
        Custom initialization
        """
        pass

    def _create_behavior(self):
        """
        Uses the Background Activity API to force a hard break on the vehicles in front of the actor,
        then waits for a bit to check if the actor has collided.
        """
        sequence = py_trees.composites.Sequence("FollowLeadingVehicleRoute")
        sequence.add_child(Scenario2Manager(self._stop_duration))
        sequence.add_child(Idle(self._end_time_condition))

        return sequence

    def _create_test_criteria(self):
        """
        A list of all test criteria will be created that is later used
        in parallel behavior tree.
        """
        criteria = []
        criteria.append(CollisionTest(self.ego_vehicles[0]))

        return criteria

    def __del__(self):
        """
        Remove all actors upon deletion
        """
        self.remove_all_actors()
