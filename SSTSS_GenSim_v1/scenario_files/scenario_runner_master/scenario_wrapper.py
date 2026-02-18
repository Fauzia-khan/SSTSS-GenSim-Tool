import subprocess
import os

def run_follow_leading_vehicle(speed, distance):
    env = os.environ.copy()
    env["LEADING_VEHICLE_SPEED"] = str(speed)
    env["LEADING_VEHICLE_LOCATION"] = str(distance)

    process = subprocess.run(
        ["python3", "scenario_runner.py", "--scenario", "FollowLeadingVehicle_1", "--waitForEgo"],
        cwd="/home/fauzia/Documents/scenario_runner",
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120
    )

    output = process.stdout + process.stderr
    collision = "CollisionTest" in output and "FAILURE" in output

    fitness = 1.0 if collision else 0.0
    return fitness

