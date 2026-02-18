from modules.constants import scenarios_excel_file_name

import pandas as pd
from Scenario_Selection_Module import SELECTED_SCENARIO_BASEDon_ODD_PATH,PRIORITIZED_SCENARIO_GROUPS_US_PATH,PRIORITIZED_SCENARIO_GROUPS_EU_PATH
# Function to prioritize the scenario groups based on the dataset (US, EU, etc.)
def prioritize_scenario_groups(dataset='US'):
    #input_file = 'formulated_scenario_groups.xlsx'  # Replace with your file path
    input_file = SELECTED_SCENARIO_BASEDon_ODD_PATH
    # Load the Excel file into a pandas DataFrame
    df = pd.read_excel(input_file)


    # Define priority for different datasets
    priority_order_us = {
        "Follow Lead Vehicle": 1,
        "Crossing Path": 2,
        "Lane Change Scenario": 3,
        "Control Loss": 4,
        "Animal Interaction": 5,
        "Opposite Direction": 6,
        "Pedestrian Interaction": 7,
        "Cyclist Interaction": 8,
        # "Turning Scenario": 9,
        # "Visibility": 9,
        # "Human fault": 9,
        # "Miscellaneous": 9,
        # "Uncategorized": 9
    }

    priority_order_eu = {
        "Cyclist Interaction": 1,
        "Crossing Path": 2,
        "Pedestrian Interaction": 3,
        "Control Loss": 4,
        "Opposite Direction": 5,
        "Follow Lead Vehicle": 6,
        "Human fault": 7,
        "Lane Change Scenario": 8,
        "Miscellaneous": 9,
        "Animal Interaction": 10,
        "Reversing": 11,
        "Visibility": 12,
        "Uncategorized": 13
    }

    # Map the dataset to the correct priority order
    if dataset.upper() == 'US':
        priority_order = priority_order_us
        output_file = PRIORITIZED_SCENARIO_GROUPS_US_PATH
    elif dataset.upper() == 'EU':
        priority_order = priority_order_eu
        output_file = PRIORITIZED_SCENARIO_GROUPS_EU_PATH
    else:
        raise ValueError(f"Dataset {dataset} not supported.")

    if 'Scenario_Group' not in df.columns:
        raise KeyError("The column 'Scenario_Group' does not exist.")

    df['Priority'] = df['Scenario_Group'].map(priority_order)
    df_sorted = df.sort_values(by='Priority').drop(columns=['Priority'])

    df_sorted.to_excel(output_file, index=False)

    print(f"Scenarios are prioritized and saved to: {output_file}")

