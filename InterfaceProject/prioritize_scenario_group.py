
import pandas as pd

# Function to prioritize the scenario groups based on the dataset (US, EU, etc.)
def prioritize_scenario_groups(dataset='US'):
    #input_file = 'formulated_scenario_groups.xlsx'  # Replace with your file path
    input_file = 'ODD_selected_scenarios.xlsx'
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
    if dataset == 'US':
        priority_order = priority_order_us
    elif dataset == 'EU':
        priority_order = priority_order_eu
    else:
        raise ValueError(f"Dataset {dataset} not supported.")

    # Check if 'Scenario_Group' column exists
    if 'Scenario_Group' not in df.columns:
        raise KeyError("The column 'Scenario_Group' does not exist in the Excel sheet.")

    # Map the priority order to the 'Scenario Group' column
    df['Priority'] = df['Scenario_Group'].map(priority_order)

    # Sort the DataFrame by the 'Priority' column (ascending)
    df_sorted = df.sort_values(by='Priority')

    # Drop the 'Priority' column since it's no longer needed
    df_sorted = df_sorted.drop(columns=['Priority'])

    # Save the sorted DataFrame back to an Excel file
    output_file = f'prioritized_scenarios_{dataset.lower()}.xlsx'
    df_sorted.to_excel(output_file, index=False)

    print(f"scenarios are prioritized, see file {output_file}")

    # Optional: Display the first few rows of the sorted DataFrame
    #print(df_sorted.head())

