import pandas as pd
from Scenario_Selection_Module import (
    PRIORITIZED_SCENARIO_GROUPS_US_PATH,
    PRIORITIZED_SCENARIO_GROUPS_EU_PATH,
    FILTERED_SCENARIOS_CARLA_PATH,
    FILTERED_SCENARIOS_GAZEBO_PATH,
    FILTERED_SCENARIOS_AUDACITY_PATH,
    FILTERED_SCENARIOS_LGSVL_PATH
)

def filter_scenarios_based_on_simulator(simulator_name, dataset_name):

    # Dataset selection
    dataset_name = dataset_name.upper()
    if dataset_name == "US":
        input_file = PRIORITIZED_SCENARIO_GROUPS_US_PATH
    elif dataset_name == "EU":
        input_file = PRIORITIZED_SCENARIO_GROUPS_EU_PATH
    else:
        raise ValueError(f"Dataset {dataset_name} not supported.")

    # Load dataset
    df = pd.read_excel(input_file)

    # Scenarios to remove for all simulators
    scenarios_to_remove = ["Control Loss", "Human fault", "Animal Interaction", "Visibility"]

    # Filter
    df_filtered = df[~df['Scenario_Group'].isin(scenarios_to_remove)]

    # Output path based on simulator selection
    simulator_output_map = {
        "Carla": FILTERED_SCENARIOS_CARLA_PATH,
        "Gazebo": FILTERED_SCENARIOS_GAZEBO_PATH,
        "Audacity": FILTERED_SCENARIOS_AUDACITY_PATH,
        "LGSVL": FILTERED_SCENARIOS_LGSVL_PATH
    }

    if simulator_name not in simulator_output_map:
        raise ValueError(f"Simulator {simulator_name} not supported.")

    output_file = simulator_output_map[simulator_name]

    # Save output
    df_filtered.to_excel(output_file, index=False)

    print(f"Scenarios filtered for {simulator_name}, saved to: {output_file}")
