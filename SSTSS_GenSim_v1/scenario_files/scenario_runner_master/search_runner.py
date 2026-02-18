import os
import subprocess
import time
import random
import yaml

# Define parameter ranges
#ego_speeds = [20, 30, 40]
#lead_speeds = [5, 10, 15]
#distances = [10, 20, 30]

test_cases = [
    {"ego": 20, "lead": 5, "dist": 10},
    {"ego": 30, "lead": 10, "dist": 50},
    {"ego": 40, "lead": 15, "dist": 80},
]

FOLLOW_VEHICLE_FILE = 'srunner/scenarios/follow_leading_vehicle.py'
PLANNING_FILE = '/home/fauzia/autoware_mini_ws/src/autoware_mini/config/planning.yaml'
RESULTS_FILE = 'results/results.csv'

# Modify follow_leading_vehicle.py file
def modify_follow_vehicle_file(lead_speed, distance):
    with open(FOLLOW_VEHICLE_FILE, 'r') as file:
        lines = file.readlines()

    with open(FOLLOW_VEHICLE_FILE, 'w') as file:
        for line in lines:
            if '# @lead_speed_edit' in line:
                file.write(f'        self._first_vehicle_speed = {lead_speed}     # @lead_speed_edit\n')
            elif '# @dist_edit' in line:
                file.write(f'        self._first_vehicle_location = {distance}  # @dist_edit\n')
            else:
                file.write(line)

# Modify Autoware Mini's planning.yaml
def modify_planning_yaml(ego_speed):
    with open(PLANNING_FILE, 'r') as file:
        data = yaml.safe_load(file)

    data['speed_limit'] = float(ego_speed)

    with open(PLANNING_FILE, 'w') as file:
        yaml.dump(data, file)

# Run scenario
def run_scenario():
    print("▶️ Launching scenario...")
    # Fully restart scenario runner so Python reloads modified .py files
    os.system("pkill -f scenario_runner.py")  # kill any running instances
    time.sleep(1)
    process = subprocess.Popen("python scenario_runner.py --scenario FollowLeadingVehicle_1 --waitForEgo",
                               shell=True)
    time.sleep(20)  # Wait for scenario to complete
    process.terminate()

# Evaluate scenario (mock - expand based on your logging setup)
def evaluate_result():
    # You can improve this by reading collision logs or metrics from ScenarioRunner
    return {"safe": random.choice([True, False])}

# Main search loop
results = []
for i, case in enumerate(test_cases):
    print(f"\n🔁 Run {i+1}: ego={case['ego']}, lead={case['lead']}, dist={case['dist']}")
    
    # Set environment variables for the scenario
    os.environ["LEAD_SPEED"] = str(case['lead'])
    os.environ["START_DIST"] = str(case['dist'])
    
    modify_planning_yaml(case['ego'])  # ego speed via planning.yaml
    run_scenario()
    result = evaluate_result()
    results.append({**case, **result})

#for ego in ego_speeds:
    #for lead in lead_speeds:
        #for dist in distances:
            #print(f"Running: ego={ego}, lead={lead}, distance={dist}")
           # modify_follow_vehicle_file(lead, dist)
           # modify_planning_yaml(ego)
           # run_scenario()
            #result = evaluate_result()
            #results.append({
               # "ego_speed": ego,
                #"lead_speed": lead,
                #"distance": dist,
               # **result
            #})

# Save results
import pandas as pd
df = pd.DataFrame(results)
os.makedirs("results", exist_ok=True)
df.to_csv(RESULTS_FILE, index=False)
print("Done. Results saved to:", RESULTS_FILE)

