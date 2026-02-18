import subprocess
import time
import os

# === Step 1: Update the FollowLeadingVehicle scenario file ===
def update_scenario_script(file_path, distance, lead_speed):
    """
    Modify follow_leading_vehicle.py to set new distance and lead vehicle speed.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        if "self._first_vehicle_location" in line:
            new_lines.append(f"        self._first_vehicle_location = {distance}  # updated by test\n")
        elif "self._first_vehicle_speed" in line:
            new_lines.append(f"        self._first_vehicle_speed = {lead_speed}  # updated by test\n")
        else:
            new_lines.append(line)

    with open(file_path, 'w') as file:
        file.writelines(new_lines)

# === Step 2: Launch Autoware Mini ===
def launch_autoware(speed_limit):
    """
    Launch Autoware Mini stack with a specific speed limit.
    """
    print(f"Launching Autoware with speed limit: {speed_limit}")
    return subprocess.Popen([
        "roslaunch", "autoware_mini", "start_carla.launch",
        "map_name:=Town01",
        "generate_traffic:=false",
        f"speed_limit:={speed_limit}"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# === Step 3: Run ScenarioRunner and save output to log ===
def run_scenario(log_file="scenario_output.log"):
    """
    Run the FollowLeadingVehicle scenario and log output.
    """
    print("Running FollowLeadingVehicle scenario")
    with open(log_file, "w") as f:
        return subprocess.run([
            "python3", "scenario_runner.py",
            "--scenario", "FollowLeadingVehicle_1",
            "--waitForEgo"
        ], cwd="/home/fauzia/Documents/scenario_runner", stdout=f, stderr=subprocess.STDOUT)

# === Step 4: Analyze the result ===
def check_safety(log_file_path):
    """
    Check if scenario run was safe (no collision).
    """
    try:
        with open(log_file_path, 'r') as file:
            log_content = file.read()
    except FileNotFoundError:
        print("Log file not found!")
        return False

    if "CollisionTest: FAILURE" in log_content:
        return False
    return True

# === Main Execution ===
if __name__ == "__main__":
    # PARAMETERS TO TEST
    distance = 20         # distance between ego and lead vehicle
    lead_speed = 30       # lead vehicle speed in km/h
    ego_speed = 15        # ego vehicle speed set via Autoware

    print(f"\n=== Starting test: distance={distance}, lead_speed={lead_speed}, ego_speed={ego_speed} ===")

    # STEP 1: Update scenario parameters
    update_scenario_script(
        "/home/fauzia/Documents/scenario_runner/srunner/scenarios/follow_leading_vehicle.py",
        distance=distance,
        lead_speed=lead_speed
    )

    # STEP 2: Launch Autoware
    autoware_process = launch_autoware(ego_speed)
    time.sleep(30)  # Wait for Autoware to initialize and spawn ego vehicle

    # STEP 3: Run scenario and log output
    log_path = "scenario_output.log"
    run_scenario(log_file=log_path)

    # STEP 4: Check if the result was safe
    safe = check_safety(log_path)
    print(f"\n>>> Test result: {'SAFE ✅' if safe else 'UNSAFE ❌'}")

    # STEP 5: Cleanup
    autoware_process.terminate()
    print("Autoware terminated.")

