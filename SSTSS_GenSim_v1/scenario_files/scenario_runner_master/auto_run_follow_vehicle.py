import subprocess
import time
import os

# Define parameter sets (speed in km/h, distance in meters)
parameter_sets = [
    (10, 80),
    (20, 30),
    (80, 5),
   
   
]

for idx, (location, speed) in enumerate(parameter_sets):
    print(f"\n--- Running scenario {idx+1} with speed={speed} km/h, distance={location} m ---")

    # Set parameters in the environment
    env = {
        **os.environ,
        "LEADING_VEHICLE_LOCATION": str(location),
        "LEADING_VEHICLE_SPEED": str(speed),
    }

    # Run scenario_runner
    subprocess.run(
        [
            "python3",
            "scenario_runner.py",
            "--scenario", "FollowLeadingVehicle_1",
            "--waitForEgo"
        ],
        env=env
    )

    print(f"Scenario {idx+1} complete. Waiting 5s before next...")
    time.sleep(5)

