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


class _2(BasicScenario):

    timeout = 120

    def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True,
                 timeout=60):

        self.timeout = timeout
        self._map = CarlaDataProvider.get_map()
        self.timeout = timeout
        self._velocity = 25
        self._delta_velocity = 10
        self._first_vehicle_location = 25
        self._first_vehicle_speed = 50
        self._other_actor_stop_in_front_intersection = 10
        point = config.trigger_points[0].location
        self._grp = GlobalRoutePlanner(CarlaDataProvider.get_map(), 2.0)
        super(_2, self).__init__("_2",
                                 ego_vehicles,
                                 config,
                                 world,
                                 debug_mode,
                                 criteria_enable=criteria_enable)

        # Set traffic light timing after scenario is initialized
        world = CarlaDataProvider.get_world()
        for light in world.get_actors().filter('traffic.traffic_light'):
            light.set_red_time(3.0)
            light.set_green_time(30.0)
            light.set_yellow_time(3.0)

        # Force initial traffic light to green for ego vehicle
        ego_vehicle = ego_vehicles[0]
        ego_location = ego_vehicle.get_location()
        ego_wp = self._map.get_waypoint(ego_location)

        ego_traffic_light = ego_vehicle.get_traffic_light()

        if ego_traffic_light is not None:
            ego_traffic_light.set_state(carla.TrafficLightState.Green)
            ego_traffic_light.set_green_time(3.0)
            ego_traffic_light.set_red_time(30.0)
            ego_traffic_light.set_yellow_time(3.0)

    def _initialize_actors(self, config):

        print

        for actor in config.other_actors:
            vehicle = CarlaDataProvider.request_new_actor(actor.model, actor.transform)
            self.other_actors.append(vehicle)
            vehicle.set_simulate_physics(enabled=True)

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
        """
        A list of all test criteria is created, which is later used in the parallel behavior tree.
        """
        criteria = []

        collision_criterion = CollisionTest(self.ego_vehicles[0])

        criteria.append(collision_criterion)

        return criteria

    def __del__(self):
        pass

