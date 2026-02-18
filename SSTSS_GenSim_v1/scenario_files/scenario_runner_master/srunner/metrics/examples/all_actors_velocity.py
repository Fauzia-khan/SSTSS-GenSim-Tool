import math
import matplotlib.pyplot as plt

from srunner.metrics.examples.basic_metric import BasicMetric

class allactorsvelocity(BasicMetric):
    
    def _create_metric(self, town_map, log, criteria):
        """
        Implementation of the metric. This is an example to show how to use the recorder,
        accessed via the log.
        """

        # Get the IDs of all actors
        actor_ids = log.get_actor_ids_with_role_name("scenario")  # Get all scenario actors
        ego_id = log.get_ego_vehicle_id()
        if ego_id not in actor_ids:
            actor_ids.append(ego_id)  # Ensure ego vehicle is included

        velocity_data = {actor_id: [] for actor_id in actor_ids}  # Store velocity per actor
        frames_list = []

        # Get the simulation frame range
        start_frame, end_frame = log.get_actor_alive_frames(ego_id)
        
        for frame in range(start_frame, end_frame + 1):
            valid_frame = False  # Track if any valid data was collected

            for actor_id in actor_ids:
                velocities = log.get_all_actor_velocities(actor_id, first_frame=frame, last_frame=frame)
                #if velocities:
                if velocities[0] is not None:
                    speed = math.sqrt(velocities[0].x**2 + velocities[0].y**2 + velocities[0].z**2) * 3.6  # Convert m/s to km/h
                else:
                    speed = 0.0  # Default to 0 if no velocity data
                
                velocity_data[actor_id].append(speed)
                valid_frame = True  # Mark as valid frame

            if valid_frame:
                frames_list.append(frame)  # Only store frames with valid data

        # Plot speeds of different actors
        #plt.figure(figsize=(10, 5))
        #for actor_id, speeds in velocity_data.items():
          #  plt.plot(frames_list, speeds, label=f"Actor {actor_id}")

        #plt.xlabel("Frame Number")
        #plt.ylabel("Speed (km/h)")
        #plt.title("Speed of All Actors Over Time")
        #plt.legend()
        #plt.grid()
        #plt.show()
        
         # Plot speeds of different actors
        plt.figure(figsize=(10, 5))
        for actor_id, speeds in velocity_data.items():
            if actor_id == ego_id:
                plt.plot(frames_list, speeds, label=f"Ego Vehicle", color='b')
            else:
                plt.plot(frames_list, speeds, label=f"Actor {actor_id}", color='orange')

        plt.xlabel("Frame Number")
        plt.ylabel("Speed (km/h)")
        plt.title("Speed of All Actors Over Time")
        plt.legend()
        plt.grid()
        plt.show()



