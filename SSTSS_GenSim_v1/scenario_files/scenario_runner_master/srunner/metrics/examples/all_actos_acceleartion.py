import math
import matplotlib.pyplot as plt

from srunner.metrics.examples.basic_metric import BasicMetric


class AllActorsAccelerationFromVelocity(BasicMetric):

    def _create_metric(self, town_map, log, criteria):
        actor_ids = log.get_actor_ids_with_role_name("scenario")
        ego_id = log.get_ego_vehicle_id()
        if ego_id not in actor_ids:
            actor_ids.append(ego_id)

        velocity_data = {actor_id: [] for actor_id in actor_ids}
        acceleration_data = {actor_id: [] for actor_id in actor_ids}
        frames_list = []

        # Use the ego actor's alive frame range
        start_frame, end_frame = log.get_actor_alive_frames(ego_id)
        delta_t = 1.0 / 20.0  # Assuming 20 FPS

        for frame in range(start_frame, end_frame + 1):
            valid_frame = False

            for actor_id in actor_ids:
                try:
                    vel_list = log.get_all_actor_velocities(actor_id, first_frame=frame, last_frame=frame)
                except IndexError:
                    vel_list = []

                if vel_list and vel_list[0]:
                    v = vel_list[0]
                    speed = math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)
                    velocity_data[actor_id].append(speed)
                    valid_frame = True
                else:
                    velocity_data[actor_id].append(None)

            if valid_frame:
                frames_list.append(frame)

        # Compute acceleration from velocity difference
        for actor_id in actor_ids:
            speeds = velocity_data[actor_id]
            accs = []

            for i in range(1, len(speeds)):
                if speeds[i] is not None and speeds[i-1] is not None:
                    a = (speeds[i] - speeds[i-1]) / delta_t
                else:
                    a = 0.0
                accs.append(a)

            # Pad first frame
            accs.insert(0, 0.0)
            acceleration_data[actor_id] = accs

        # Plot
        plt.figure(figsize=(10, 5))
        for actor_id, accs in acceleration_data.items():
            label = "Ego Vehicle" if actor_id == ego_id else f"Actor {actor_id}"
            color = 'b' if actor_id == ego_id else 'orange'
            plt.plot(frames_list, accs, label=label, color=color)

        plt.xlabel("Frame Number")
        plt.ylabel("Acceleration (m/s²)")
        plt.title("Acceleration (Computed from Velocity) of All Actors Over Time")
        plt.legend()
        plt.grid()
        plt.show()


