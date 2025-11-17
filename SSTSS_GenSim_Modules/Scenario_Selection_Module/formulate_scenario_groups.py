import pandas as pd
#from modules.constants import scenarios_excel_file_name
from Scenario_Selection_Module import USER_SELECTED_SCENARIOS_PATH, CATALOG_SCENARIOS_PATH,FORMULATED_SCENARIOS_PATH
import re

def formulate_scenario_groups():
    # Load the Excel file into a pandas DataFrame
    #df = pd.read_excel('ODD_selected_scenarios.xlsx', header=[0, 1])  # Read multi-level headers
    df = pd.read_excel(USER_SELECTED_SCENARIOS_PATH, header=[0, 1])  # Read multi-level headers
    # Flatten the MultiIndex columns by combining the two levels of column headers
    df.columns = ['_'.join(col).strip() for col in df.columns.values]
    df.columns.values[-1] = 'image'

    # Create a new column for scenario group
    df['Scenario_Group'] = None  # Create a new column for scenario group (without MultiIndex)

    # Step 1: Assign scenario groups based on row conditions (actors, driving maneuvers)
    def classify_by_row_conditions(row):
        if row['Actors_Pedestrian'] == 1:
            return "Pedestrian Interaction"
        elif row['Actors_Animal'] == 1:
            return "Animal Interaction"
        elif row['Actors_Pedal cyclist'] == 1:
            return "Cyclist Interaction"
        elif row['Actors_Vehicle'] == 1 and row['Driving Maneuver_Merging/Changing Lanes'] == 1:
            return "Lane Change Scenario"
        return None

    # Step 2: Assign remaining scenarios based on keyword matching in the description
    def classify_by_keywords(description):
        description = description.lower()

        turning_keywords = ['turning left', 'turning right','curve','bend','empty roundabout']
        lane_keywords = ['merge', 'lane change', 'switch lanes', 'cut-in', 'cut-out', 'swerve','impassable', 'swerving']
        opposite_keywords = ['oncoming traffic', 'oncoming vehicle']
        crossing_keywords = ['junction', 'non-signalized']
        trafficsignal_keywords = ['running red traffic light','running amber traffic light','approaching red traffic light','approaching green traffic light', 'approaching amber traffic light' ]
        followinglead_keywords = ['rear-end','lead vehicle', 'following lead', 'vehicle behind']
        controlloss_keywords = ['loss control', 'brake failure', 'slippery', 'poor road conditions']
        visibility_keywords = ['visibility', 'fog', 'weather', 'obstruction', 'hurdles', 'construction']
        humanfault_keywords = ['human error', 'aggressive driving', 'negligent', 'distracted driving']

        if any(keyword in description for keyword in turning_keywords):
            return "Turning Scenario"
        elif any(keyword in description for keyword in lane_keywords):
            return "Lane Change Scenario"
        elif any(keyword in description for keyword in opposite_keywords):
            return "Opposite Direction"
        elif any(keyword in description for keyword in crossing_keywords):
            return "Crossing Path"
        elif any(keyword in description for keyword in trafficsignal_keywords):
            return "Traffic Signal"
        elif any(keyword in description for keyword in followinglead_keywords):
            return "Follow Lead Vehicle"
        elif any(keyword in description for keyword in controlloss_keywords):
            return "Control Loss"
        elif any(keyword in description for keyword in visibility_keywords):
            return "Visibility"
        elif any(keyword in description for keyword in humanfault_keywords):
            return "Human Fault"

        return "Miscellaneous"

    # Iterate over the DataFrame rows to classify scenarios
    for index, row in df.iterrows():
        scenario_group = classify_by_row_conditions(row)
        if scenario_group is None:
            description = row['Name_Unnamed: 2_level_1']  # Adjust column name as needed
            if pd.notna(description):
                scenario_group = classify_by_keywords(description)
        df.at[index, 'Scenario_Group'] = scenario_group

    # Save the updated DataFrame back to the Excel file (or a new file)

    output_file = FORMULATED_SCENARIOS_PATH
    df.to_excel(output_file, index=False)
    print(f"scenarios are grouped to the formulated scenario groups in the SSTSS process, see file {output_file}")

    # Load the updated file and select the relevant columns
    #updated_df = pd.read_excel('updated_scenario_flattened.xlsx')
    #selected_columns_updated = updated_df[['Road Topology_SG', 'Scenario_Group']]

    # Set pandas option to display all rows
    #pd.set_option('display.max_rows', None)

    # Display all the rows of the selected columns
    #print(selected_columns_updated)

