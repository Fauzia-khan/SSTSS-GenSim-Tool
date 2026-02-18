
import math
import os
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import csv
from srunner.metrics.examples.basic_metric import BasicMetric


class VelocityAndDistanceMetric(BasicMetric):

    def calculate_rss_distance(self, v_r, v_f, rho, a_max, b_min, b_max):
        term1 = v_r * rho
        term2 = 0.5 * a_max * rho ** 2
        term3 = ((v_r + rho * a_max) ** 2) / (2 * b_min)
        term4 = (v_f ** 2) / (2 * b_max)
        d_min = term1 + term2 + term3 - term4
        return max(d_min, 0)

    def _create_metric(self, town_map, log, criteria):
        ego_id = log.get_ego_vehicle_id()
        actor_ids = log.get_actor_ids_with_role_name("scenario")
        adv_id = actor_ids[0] if actor_ids else None

        if ego_id is None or adv_id is None:
            print("Ego or adversary vehicle not found.")
            return

        velocity_data = {ego_id: [], adv_id: []}
        distance_data = []
        ego_distance_covered = []
        adv_distance_covered = []
        ego_x_data = []
        ego_y_data = []
        adv_x_data = []
        adv_y_data = []
        frames_list = []

        ego_total_distance = 0.0
        adv_total_distance = 0.0
        prev_ego_location = None
        prev_adv_location = None

        start_ego, end_ego = log.get_actor_alive_frames(ego_id)
        start_adv, end_adv = log.get_actor_alive_frames(adv_id)
        start = max(start_ego, start_adv)
        end = min(end_ego, end_adv)

        time_per_frame = 1.0 / 20.0

        for frame in range(start, end + 1):
            ego_vel = log.get_all_actor_velocities(ego_id, frame, frame)
            adv_vel = log.get_all_actor_velocities(adv_id, frame, frame)

            ego_speed = math.sqrt(ego_vel[0].x**2 + ego_vel[0].y**2 + ego_vel[0].z**2) * 3.6 if ego_vel and ego_vel[0] else 0.0
            adv_speed = math.sqrt(adv_vel[0].x**2 + adv_vel[0].y**2 + adv_vel[0].z**2) * 3.6 if adv_vel and adv_vel[0] else 0.0

            velocity_data[ego_id].append(ego_speed)
            velocity_data[adv_id].append(adv_speed)

            ego_transform = log.get_actor_transform(ego_id, frame)
            adv_transform = log.get_actor_transform(adv_id, frame)

            if adv_transform.location.z < -10:
                continue

            # Save positions
            ego_x_data.append(ego_transform.location.x)
            ego_y_data.append(ego_transform.location.y)
            adv_x_data.append(adv_transform.location.x)
            adv_y_data.append(adv_transform.location.y)

            dist_v = ego_transform.location - adv_transform.location
            dist = math.sqrt(dist_v.x**2 + dist_v.y**2 + dist_v.z**2)
            distance_data.append(dist)
            frames_list.append(frame)

            if prev_ego_location:
                delta = ego_transform.location - prev_ego_location
                ego_total_distance += math.sqrt(delta.x**2 + delta.y**2 + delta.z**2)
            ego_distance_covered.append(ego_total_distance)
            prev_ego_location = ego_transform.location

            if prev_adv_location:
                delta = adv_transform.location - prev_adv_location
                adv_total_distance += math.sqrt(delta.x**2 + delta.y**2 + delta.z**2)
            adv_distance_covered.append(adv_total_distance)
            prev_adv_location = adv_transform.location

        time_list = [(frame - frames_list[0]) * time_per_frame for frame in frames_list]

        lead_speed_series = pd.Series(velocity_data[adv_id])
        lead_speed_smoothed = lead_speed_series.rolling(window=10, min_periods=1).mean()

        output_dir = "/home/fauzia/Documents/scenario_runner/results/test"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_prefix = f"{output_dir}/FollowScenario_{timestamp}"
        csv_file_path = f"{file_prefix}_metrics.csv"

        # === Build DataFrame ===
        df = pd.DataFrame({
            "Time (s)": time_list,
            "Ego Speed (km/h)": velocity_data[ego_id],
            "Lead Speed (km/h)": velocity_data[adv_id],
            "Smoothed Lead Speed (km/h)": lead_speed_smoothed,
            "Distance Between (m)": distance_data,
            "Ego Distance Covered (m)": ego_distance_covered,
            "Lead Vehicle Distance Covered (m)": adv_distance_covered,
            "Ego X (m)": ego_x_data,
            "Ego Y (m)": ego_y_data,
            "Lead X (m)": adv_x_data,
            "Lead Y (m)": adv_y_data
        })

        # === Derived Metrics ===
        df["Ego Speed (m/s)"] = df["Ego Speed (km/h)"] / 3.6
        df["Smoothed Lead Speed (m/s)"] = df["Smoothed Lead Speed (km/h)"] / 3.6
        df["Ego Acceleration (m/s²)"] = df["Ego Speed (m/s)"].diff() / df["Time (s)"].diff()
        df["Lead Acceleration (m/s²)"] = df["Smoothed Lead Speed (m/s)"].diff() / df["Time (s)"].diff()

        # Positional acceleration
        df["Ego Pos Vel X (m/s)"] = df["Ego X (m)"].diff() / df["Time (s)"].diff()
        df["Ego Pos Vel Y (m/s)"] = df["Ego Y (m)"].diff() / df["Time (s)"].diff()
        df["Ego Accel X (m/s²)"] = df["Ego Pos Vel X (m/s)"].diff() / df["Time (s)"].diff()
        df["Ego Accel Y (m/s²)"] = df["Ego Pos Vel Y (m/s)"].diff() / df["Time (s)"].diff()
        df["Ego Accel Magnitude (m/s²)"] = (df["Ego Accel X (m/s²)"]**2 + df["Ego Accel Y (m/s²)"]**2)**0.5

        # === Jerk Calculation ===
        df["Ego Jerk (m/s³)"] = df["Ego Accel Magnitude (m/s²)"].diff() / df["Time (s)"].diff()

        # === RSS ===
        response_time = 0.001
        a_max = 1.0
        b_min = 1.0
        b_max = 1.5

        df["RSS Safety Distance (m)"] = df.apply(
            lambda row: self.calculate_rss_distance(
                row["Ego Speed (m/s)"],
                row["Smoothed Lead Speed (m/s)"],
                response_time,
                a_max,
                b_min,
                b_max
            ),
            axis=1
        )

        # === Rounding ===
        round_2_cols = [
            "Ego Speed (km/h)", "Ego Speed (m/s)",
            "Lead Speed (km/h)", "Smoothed Lead Speed (km/h)", "Smoothed Lead Speed (m/s)",
            "Distance Between (m)", "Ego Distance Covered (m)", "Lead Vehicle Distance Covered (m)",
            "RSS Safety Distance (m)", "Ego X (m)", "Ego Y (m)", "Lead X (m)", "Lead Y (m)"
        ]
        round_3_cols = [
            "Ego Acceleration (m/s²)", "Lead Acceleration (m/s²)",
            "Ego Pos Vel X (m/s)", "Ego Pos Vel Y (m/s)",
            "Ego Accel X (m/s²)", "Ego Accel Y (m/s²)",
            "Ego Accel Magnitude (m/s²)", "Ego Jerk (m/s³)"
        ]

        df[round_2_cols] = df[round_2_cols].round(2)
        df[round_3_cols] = df[round_3_cols].round(3)

        # === Save CSV ===
        df.to_csv(csv_file_path, index=False)
        print(f"Saved CSV with metrics: {csv_file_path}")

        # === Plot 1: Speed & Distance ===
        time = df["Time (s)"]

        fig1, ax1 = plt.subplots(figsize=(12, 6))
        ax1.set_xlabel("Time (seconds)")
        ax1.set_ylabel("Speed (km/h)", color='tab:blue')
        ax1.plot(time, df["Ego Speed (km/h)"], label="Ego Speed", color='tab:blue')
        ax1.plot(time, df["Smoothed Lead Speed (km/h)"], label="Lead Speed", color='orange')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax1.legend(loc='upper left')

        ax1b = ax1.twinx()
        ax1b.set_ylabel("Distance (m)", color='tab:red')
        ax1b.plot(time, df["Distance Between (m)"], label="Actual Distance b/w Vehicles", color='tab:red')
        ax1b.plot(time, df["RSS Safety Distance (m)"], label="RSS Safety Distance", color='tab:red', linestyle='--')
        ax1b.tick_params(axis='y', labelcolor='tab:red')
        ax1b.legend(loc='upper right')

        fig1.suptitle("Speed of Vehicles, RSS, and Actual Distance Between Both Vehicles")
        fig1.tight_layout()
        ax1.grid()
        fig1_path = csv_file_path.replace("_metrics.csv", "_speed_distance.png")
        fig1.savefig(fig1_path)
        print(f"Saved: {fig1_path}")
        #plt.show()

        # === Plot 2: Acceleration and Jerk ===
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        #ax2.plot(time, df["Ego Accel Magnitude (m/s²)"], label="Ego Acceleration", color='green')
        ax2.plot(time, df["Ego Jerk (m/s³)"], label="Ego Vehicle Jerk", color='tab:blue')
        ax2.set_xlabel("Time (seconds)")
        ax2.set_ylabel("Jerk (m/s$^3$)")
        ax2.set_title("Ego Vehicle Jerk Over Time")
        ax2.legend()
        ax2.grid()
        fig2.tight_layout()
        fig2_path = csv_file_path.replace("_metrics.csv", "_accel_jerk.png")
        fig2.savefig(fig2_path)
        print(f"Saved: {fig2_path}")
        #plt.show()


###old running code orevious grapgh are taken from the code below/

# import math
# import os
# import datetime
# import matplotlib.pyplot as plt
# import pandas as pd
# import csv
# from srunner.metrics.examples.basic_metric import BasicMetric


# class VelocityAndDistanceMetric(BasicMetric):

#     def calculate_rss_distance(self, v_r, v_f, rho, a_max, b_min, b_max):
#         term1 = v_r * rho
#         term2 = 0.5 * a_max * rho ** 2
#         term3 = ((v_r + rho * a_max) ** 2) / (2 * b_min)
#         term4 = (v_f ** 2) / (2 * b_max)
#         d_min = term1 + term2 + term3 - term4
#         return max(d_min, 0)

#     def _create_metric(self, town_map, log, criteria):
#         ego_id = log.get_ego_vehicle_id()
#         actor_ids = log.get_actor_ids_with_role_name("scenario")
#         adv_id = actor_ids[0] if actor_ids else None

#         if ego_id is None or adv_id is None:
#             print("Ego or adversary vehicle not found.")
#             return

#         velocity_data = {ego_id: [], adv_id: []}
#         distance_data = []
#         ego_distance_covered = []
#         adv_distance_covered = []
#         frames_list = []

#         ego_total_distance = 0.0
#         adv_total_distance = 0.0
#         prev_ego_location = None
#         prev_adv_location = None

#         start_ego, end_ego = log.get_actor_alive_frames(ego_id)
#         start_adv, end_adv = log.get_actor_alive_frames(adv_id)
#         start = max(start_ego, start_adv)
#         end = min(end_ego, end_adv)

#         time_per_frame = 1.0 / 20.0

#         for frame in range(start, end + 1):
#             ego_vel = log.get_all_actor_velocities(ego_id, frame, frame)
#             adv_vel = log.get_all_actor_velocities(adv_id, frame, frame)

#             ego_speed = math.sqrt(ego_vel[0].x**2 + ego_vel[0].y**2 + ego_vel[0].z**2) * 3.6 if ego_vel and ego_vel[0] else 0.0
#             adv_speed = math.sqrt(adv_vel[0].x**2 + adv_vel[0].y**2 + adv_vel[0].z**2) * 3.6 if adv_vel and adv_vel[0] else 0.0

#             velocity_data[ego_id].append(ego_speed)
#             velocity_data[adv_id].append(adv_speed)

#             ego_transform = log.get_actor_transform(ego_id, frame)
#             adv_transform = log.get_actor_transform(adv_id, frame)

#             if adv_transform.location.z < -10:
#                 continue

#             dist_v = ego_transform.location - adv_transform.location
#             dist = math.sqrt(dist_v.x**2 + dist_v.y**2 + dist_v.z**2)
#             distance_data.append(dist)
#             frames_list.append(frame)

#             if prev_ego_location:
#                 delta = ego_transform.location - prev_ego_location
#                 ego_total_distance += math.sqrt(delta.x**2 + delta.y**2 + delta.z**2)
#             ego_distance_covered.append(ego_total_distance)
#             prev_ego_location = ego_transform.location

#             if prev_adv_location:
#                 delta = adv_transform.location - prev_adv_location
#                 adv_total_distance += math.sqrt(delta.x**2 + delta.y**2 + delta.z**2)
#             adv_distance_covered.append(adv_total_distance)
#             prev_adv_location = adv_transform.location

#         time_list = [(frame - frames_list[0]) * time_per_frame for frame in frames_list]

#         lead_speed_series = pd.Series(velocity_data[adv_id])
#         lead_speed_smoothed = lead_speed_series.rolling(window=10, min_periods=1).mean()

#         output_dir = "/home/laima/Documents/scenario_runner-master/results/test"
#         os.makedirs(output_dir, exist_ok=True)
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#         file_prefix = f"{output_dir}/FollowScenario_{timestamp}"
#         csv_file_path = f"{file_prefix}_metrics.csv"

#         # Create DataFrame
#         df = pd.DataFrame({
#             "Time (s)": time_list,
#             "Ego Speed (km/h)": velocity_data[ego_id],
#             "Lead Speed (km/h)": velocity_data[adv_id],
#             "Smoothed Lead Speed (km/h)": lead_speed_smoothed,
#             "Distance Between (m)": distance_data,
#             "Ego Distance Covered (m)": ego_distance_covered,
#             "Lead Vehicle Distance Covered (m)": adv_distance_covered
#         })

#         # Derived metrics
#         df["Ego Speed (m/s)"] = df["Ego Speed (km/h)"] / 3.6
#         df["Smoothed Lead Speed (m/s)"] = df["Smoothed Lead Speed (km/h)"] / 3.6
#         df["Ego Acceleration (m/s²)"] = df["Ego Speed (m/s)"].diff() / df["Time (s)"].diff()
#         df["Lead Acceleration (m/s²)"] = df["Smoothed Lead Speed (m/s)"].diff() / df["Time (s)"].diff()

#         theoretical_accel = 1.5
#         target_speed_mps = 10 / 3.6
#         accel_duration = target_speed_mps / theoretical_accel
#         start_time = df["Time (s)"].iloc[0]

#         df["Lead Acceleration (Theoretical)"] = [
#             theoretical_accel if t - start_time <= accel_duration else 0.0
#             for t in df["Time (s)"]
#         ]

#         # Braking phase detection
#         df["Lead Braking Distance (m)"] = None
#         df["Braking Phase"] = ""

#         initial_idx = df[df["Lead Vehicle Distance Covered (m)"] >= 60].index.min()
#         if pd.notnull(initial_idx):
#             brake_start_idx = None
#             for i in range(initial_idx, len(df) - 4):
#                 s1, s2, s3, s4 = df["Smoothed Lead Speed (m/s)"].iloc[i:i+4]
#                 if s1 > s2 > s3 > s4:
#                     brake_start_idx = i
#                     break

#             brake_end_idx = None
#             if brake_start_idx is not None:
#                 for i in range(brake_start_idx + 1, len(df) - 1):
#                     if (df["Smoothed Lead Speed (m/s)"].iloc[i:i+1] <= 0).all():
#                         brake_end_idx = i
#                         break

#             if brake_start_idx is not None and brake_end_idx is not None:
#                 start_dist = df["Lead Vehicle Distance Covered (m)"].iloc[brake_start_idx]
#                 end_dist = df["Lead Vehicle Distance Covered (m)"].iloc[brake_end_idx]
#                 braking_dist = round(end_dist - start_dist, 2)
#                 df.loc[0, "Lead Braking Distance (m)"] = braking_dist
#                 df.loc[brake_end_idx, "Lead Braking Distance (m)"] = braking_dist
#                 df.loc[brake_start_idx, "Braking Phase"] = "START"
#                 df.loc[brake_end_idx, "Braking Phase"] = "END"

#         # RSS Calculation
#         response_time = 0.001
#         a_max = 1.0
#         b_min = 1.0
#         b_max = 1.5

#         df["RSS Safety Distance (m)"] = df.apply(
#             lambda row: self.calculate_rss_distance(
#                 row["Ego Speed (m/s)"],
#                 row["Smoothed Lead Speed (m/s)"],
#                 response_time,
#                 a_max,
#                 b_min,
#                 b_max
#             ),
#             axis=1
#         )

#         # === Round off values ===
#         round_2_cols = [
#             "Ego Speed (km/h)", "Ego Speed (m/s)",
#             "Lead Speed (km/h)", "Smoothed Lead Speed (km/h)", "Smoothed Lead Speed (m/s)",
#             "Distance Between (m)", "Ego Distance Covered (m)", "Lead Vehicle Distance Covered (m)",
#             "RSS Safety Distance (m)", "Lead Braking Distance (m)"
#         ]
#         round_3_cols = [
#             "Ego Acceleration (m/s²)", "Lead Acceleration (m/s²)",
#             "Lead Acceleration (Theoretical)"
#         ]

#         df[round_2_cols] = df[round_2_cols].round(2)
#         df[round_3_cols] = df[round_3_cols].round(3)

#         # === Save final CSV ===
#         column_order = [
#             "Time (s)",
#             "Ego Speed (km/h)",
#             "Ego Speed (m/s)",
#             "Lead Speed (km/h)",
#             "Smoothed Lead Speed (m/s)",
#             "Smoothed Lead Speed (km/h)",
#             "Ego Acceleration (m/s²)",
#             "Lead Acceleration (m/s²)",
#             "Lead Acceleration (Theoretical)",
#             "Ego Distance Covered (m)",
#             "Lead Vehicle Distance Covered (m)",
#             "Distance Between (m)",
#             "Lead Braking Distance (m)",
#             "Braking Phase",
#             "RSS Safety Distance (m)"
#         ]

#         df.to_csv(csv_file_path, columns=column_order, index=False)
#         print(f"Saved final CSV with all metrics: {csv_file_path}")

#         # === Plot ===
#         time = df["Time (s)"]

#         fig1, ax1 = plt.subplots(figsize=(12, 6))
#         ax1.set_xlabel("Time (seconds)")
#         ax1.set_ylabel("Speed (km/h)", color='tab:blue')
#         ax1.plot(time, df["Ego Speed (km/h)"], label="Ego Speed", color='tab:blue')
#         ax1.plot(time, df["Smoothed Lead Speed (km/h)"], label="Lead Speed", color='orange')
#         ax1.tick_params(axis='y', labelcolor='tab:blue')
#         ax1.legend(loc='upper left')

#         ax1b = ax1.twinx()
#         ax1b.set_ylabel("Distance (m)", color='tab:red')
#         ax1b.plot(time, df["Distance Between (m)"], label="Actual Distance b/w Vehicles", color='tab:red')
#         ax1b.plot(time, df["RSS Safety Distance (m)"], label="RSS Safety Distance", color='tab:red', linestyle='--')
#         ax1b.tick_params(axis='y', labelcolor='tab:red')
#         ax1b.legend(loc='upper right')

#         fig1.suptitle("Speed of Vehicles, RSS, and Actual Distance Between Both Vehicles")
#         fig1.tight_layout()
#         ax1.grid()
#         fig1_path = csv_file_path.replace("_metrics.csv", "_speed_distance.png")
#         fig1.savefig(fig1_path)
#         print(f"Saved: {fig1_path}")
#         plt.show()


      
