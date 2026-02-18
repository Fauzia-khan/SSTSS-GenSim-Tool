import random
import py_trees
import carla
from agents.navigation.global_route_planner import GlobalRoutePlanner

from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.scenariomanager.scenarioatomics.atomic_behaviors import (
    ActorTransformSetter,
    StopVehicle,
    LaneChange,
    ActorDestroy,
    WaypointFollower,
    AccelerateToCatchUp,
    ChangeActorTargetSpeed
)
from srunner.scenariomanager.scenarioatomics.atomic_criteria import CollisionTest
from srunner.scenariomanager.scenarioatomics.atomic_trigger_conditions import (
    InTriggerDistanceToLocation, 
    InTriggerDistanceToNextIntersection, 
    DriveDistance
)
from srunner.scenarios.basic_scenario import BasicScenario
from srunner.tools.scenario_helper import get_waypoint_in_distance


class _2(BasicScenario):
    timeout = 1200

    def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True, timeout=60):
        self.timeout = timeout
        self._map = CarlaDataProvider.get_map()
        self._velocity = 35
        self._delta_velocity = 10
        self._first_vehicle_location = 25
        self._first_vehicle_speed = 10
        self._other_actor_stop_in_front_intersection = 10
        point = config.trigger_points[0].location
        self._grp = GlobalRoutePlanner(CarlaDataProvider.get_map(), 2.0)
        
        # Traffic light timing parameters
        self._green_duration = 2  # Green light duration in seconds
        self._yellow_duration = 3  # Yellow light duration in seconds
        self._traffic_light = None
        
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

    def _find_ego_traffic_light(self):
        """Finds the traffic light that the ego vehicle will encounter"""
        if not self.ego_vehicles:
            return None
            
        all_lights = CarlaDataProvider.get_world().get_actors().filter('traffic.traffic_light')
        if not all_lights:
            return None
            
        ego_location = self.ego_vehicles[0].get_location()
        closest_light = None
        min_distance = float('inf')
        
        for light in all_lights:
            distance = ego_location.distance(light.get_location())
            if distance < min_distance:
                min_distance = distance
                closest_light = light
                
        return closest_light

    def _setup_traffic_light(self):
        """Directly controls the traffic light state"""
        self._traffic_light = self._find_ego_traffic_light()
        if not self._traffic_light:
            print("Warning: No traffic light found for ego vehicle route")
            return
            
        # Freeze the light to prevent automatic changes
        self._traffic_light.freeze(True)
        
        # Set initial state to green
        self._traffic_light.set_state(carla.TrafficLightState.Green)
        print(f"\nTraffic light {self._traffic_light.id} set to GREEN")

    class TrafficLightController(py_trees.behaviour.Behaviour):
        """Directly controls traffic light timing"""
        def __init__(self, traffic_light, green_time, yellow_time):
            super(_2.TrafficLightController, self).__init__("TrafficLightController")
            self.traffic_light = traffic_light
            self.green_time = green_time
            self.yellow_time = yellow_time
            self.start_time = 0
            self.current_state = "green"

        def initialise(self):
            self.start_time = CarlaDataProvider.get_world().get_snapshot().timestamp.elapsed_seconds
            print(f"Traffic light timer started at: {self.start_time:.1f}s (GREEN)")

        def update(self):
            current_time = CarlaDataProvider.get_world().get_snapshot().timestamp.elapsed_seconds
            elapsed = current_time - self.start_time
            
            if self.current_state == "green" and elapsed >= self.green_time:
                self.traffic_light.set_state(carla.TrafficLightState.Yellow)
                self.start_time = current_time
                self.current_state = "yellow"
                print(f"Changed to YELLOW at {current_time:.1f}s")
                
            elif self.current_state == "yellow" and elapsed >= self.yellow_time:
                self.traffic_light.set_state(carla.TrafficLightState.Red)
                print(f"Changed to RED at {current_time:.1f}s")
                return py_trees.common.Status.SUCCESS
                
            return py_trees.common.Status.RUNNING

    def _create_behavior(self):
        # Setup traffic light first
        self._setup_traffic_light()
        
        # Create parallel root for behaviors
        root = py_trees.composites.Parallel(
            "Root",
            policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE)
        
        # Traffic light control sequence
        light_control = py_trees.composites.Sequence("LightControl")
        light_control.add_child(self.TrafficLightController(
            self._traffic_light, 
            self._green_duration,
            self._yellow_duration
        ))
        
        # Vehicle behavior
        drive_behavior = py_trees.composites.Sequence("DriveBehavior")
        pos = self.other_actors[0].get_location()
        destpos = carla.Location(-98, -23, 0)
        plan = self._grp.trace_route(pos, destpos)
        
        drive_straight = py_trees.composites.Parallel(
            "DriveStraight",
            policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE)
        drive_straight.add_child(WaypointFollower(self.other_actors[0], 10, plan=plan))
        drive_straight.add_child(InTriggerDistanceToLocation(
            self.ego_vehicles[0], carla.Location(-42.9, -2.7, 0), 3))
        
        drive_behavior.add_child(drive_straight)
        
        # Combine everything
        root.add_child(light_control)
        root.add_child(drive_behavior)
        
        # Main sequence
        sequence = py_trees.composites.Sequence("Sequence Behavior")
        sequence.add_child(root)
        sequence.add_child(ActorDestroy(self.other_actors[0]))

        return sequence

    def _create_test_criteria(self):
        criteria = []
        collision_criterion = CollisionTest(self.ego_vehicles[0])
        criteria.append(collision_criterion)
        return criteria

    def __del__(self):
        if self._traffic_light:
            self._traffic_light.freeze(False)
            self._traffic_light.set_state(carla.TrafficLightState.Red)
        self.remove_all_actors()
