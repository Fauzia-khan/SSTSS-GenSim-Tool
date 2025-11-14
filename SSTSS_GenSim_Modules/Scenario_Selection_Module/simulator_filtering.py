import os
from modules.constants import scenarios_excel_file_name

import pandas as pd



def filter_scenarios_based_on_simulator(simulator_name, dataset_name):
    # Load the Excel file into a pandas DataFrame
    dataset_name = dataset_name.lower()

    df = pd.read_excel(os.getcwd() + f"/prioritized_scenario_groups_{dataset_name}.xlsx")

    # Define the scenario groups that are outside of the simulator's capabilities
    scenarios_to_remove = ["Control Loss", "Human fault", "Animal Interaction", "Visibility"]

    # Filter out the unwanted scenarios
    df_filtered = df[~df['Scenario_Group'].isin(scenarios_to_remove)]

    # Save the filtered DataFrame back to a new Excel file
    output_file = f'filtered_scenarios_{simulator_name}.xlsx'
    df_filtered.to_excel(output_file, index=False)

    print(f"scenarios are filter based on the selected simulator, see file {output_file}")
