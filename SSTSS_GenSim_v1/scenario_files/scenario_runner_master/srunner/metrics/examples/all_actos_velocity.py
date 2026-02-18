import math
import matplotlib.pyplot as plt
import csv  # ✅ CSV support
import os

from srunner.metrics.examples.basic_metric import BasicMetric


class allactorsvelocity(BasicMetric):
    
    def _create_metric(self, town_map, log, criteria):
        """
        Plot and export speed (in km/h) of all actors (including ego) vs simulation frame number.
        """

        # Get actor IDs (including ego)
        actor_ids = log.get_actor_ids_with_role_name("scenario")
        ego_id = log.get_ego_vehicle_id()
        if ego_id not in actor_ids:
            actor_ids.append(ego_id)

        # Initialize data structures
        velocity_data = {actor_id: [] for actor_id in actor_ids}
        frames_list = []

        # Get the frame range where the ego vehicle is alive
        start_frame, end_frame = log.get_actor_alive_frames(ego_id)

        # Loop over each frame and collect velocity magnitudes
        for frame in range(start_frame, end_frame + 1):
            valid_frame = False

            for actor_id in actor_ids:
                try:
                    velocities = log.get_all_actor_velocities(actor_id, first_frame=frame, last_frame=frame)
                    velocity = velocities[0] if velocities else None
                except IndexError:
                    velocity = None

                if velocity:
                    speed = math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2) * 3.6  # m/s to km/h
                else:
                    speed = 0.0

                velocity_data[actor_id].append(speed)
                valid_frame = True

            if valid_frame:
                frames_list.append(frame)

        # ✅ Export to CSV
        output_file = os.path.join(os.getcwd(), "actor_velocities.csv")
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Header: Frame + actor IDs
            header = ["Frame"] + [f"Actor_{actor_id}" if actor_id != ego_id else "Ego_Vehicle" for actor_id in actor_ids]
            writer.writerow(header)

            # Write frame-by-frame rows
            for i, frame in enumerate(frames_list):
                row = [frame]
                for actor_id in actor_ids:
                    row.append(round(velocity_data[actor_id][i], 2))  # round to 2 decimal places
                writer.writerow(row)

        print(f"[INFO] Velocity data exported to: {output_file}")

        # ✅ Plot
        plt.figure(figsize=(10, 5))
        for actor_id, speeds in velocity_data.items():
            label = "Ego Vehicle" if actor_id == ego_id else f"Actor {actor_id}"
            color = 'b' if actor_id == ego_id else 'orange'
            plt.plot(frames_list, speeds, label=label, color=color)

        plt.xlabel("Frame Number")
        plt.ylabel("Speed (km/h)")
        plt.title("Speed of All Actors Over Time (by Frame)")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

