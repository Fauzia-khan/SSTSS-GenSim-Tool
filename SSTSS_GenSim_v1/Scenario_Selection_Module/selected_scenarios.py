import pandas as pd
from Scenario_Selection_Module import (
    SELECTED_SCENARIOS_US_PATH,
    SELECTED_SCENARIOS_EU_PATH
)

def run_eu_based_scenario_selector(file_path):
    df = pd.read_excel(file_path)

    # ---------------- SCORING FUNCTIONS ----------------
    def assign_actor_score(row):
        if row['Actors_Vehicle'] == 1: return 4
        elif row['Actors_Pedestrian'] == 1: return 3
        elif row['Actors_Motorcyclist'] == 1: return 2
        elif row['Actors_Pedal cyclist'] == 1: return 1
        elif row['Actors_Animal'] == 1: return 1
        elif row['Actors_Other'] == 1: return 1
        return 0

    def assign_maneuver_score(row):
        if row['Driving Maneuver_Driving Straight'] == 1: return 7
        elif row['Driving Maneuver_Negotiating a Curve'] == 1: return 5
        elif row['Driving Maneuver_Turning Left'] == 1: return 6
        elif row['Driving Maneuver_Passing or Overtaking Another Vehicle'] == 1: return 0
        elif row['Driving Maneuver_Merging/Changing Lanes'] == 1: return 4
        elif row['Driving Maneuver_Stopped in Roadway'] == 1: return 0
        elif row['Driving Maneuver_Turning Right'] == 1: return 3
        elif row['Driving Maneuver_Backing Up'] == 1: return 2
        return 0

    def assign_weather_score(row):
        if row['Weather_Dry'] == 1: return 4
        elif row['Weather_Rain'] == 1: return 2
        elif row['Weather_Fog'] == 1: return 3
        elif row['Weather_Snow'] == 1: return 1
        return 0

    def assign_lighting_score(row):
        if row['Light_Day'] == 1: return 4
        elif row['Light_Dark'] == 1: return 3
        elif row['Light_Twilight'] == 1: return 1
        return 0

    # ---------------- APPLY SCORING ----------------
    df['actor_score'] = df.apply(assign_actor_score, axis=1)
    df['maneuver_score'] = df.apply(assign_maneuver_score, axis=1)
    df['weather_score'] = df.apply(assign_weather_score, axis=1)
    df['lighting_score'] = df.apply(assign_lighting_score, axis=1)

    df['total_score'] = (
        df['actor_score']
        + df['maneuver_score']
        + df['weather_score']
        + df['lighting_score']
    )

    # Preserve group order
    df['original_index'] = df.index
    df = df.sort_values(by=['Scenario_Group', 'total_score'], ascending=[True, False])
    df = df.sort_values(by=['original_index']).drop(columns=['original_index'])

    # ---------------- PRIORITY CALCULATION ----------------
    current_priority = 0
    priority_list = []

    for _, group in df.groupby('Scenario_Group', sort=False):
        group_priority = group['total_score'].rank(method='dense', ascending=False).astype(int)
        group_priority += current_priority
        current_priority = group_priority.max()
        priority_list.extend(group_priority)

    df['priority'] = priority_list

    # Sort by priority
    df = df.sort_values(by='priority', ascending=True)

    # Save output
    df.to_excel(SELECTED_SCENARIOS_EU_PATH, index=False)
    print(f"EU scenarios selected → {SELECTED_SCENARIOS_EU_PATH}")

    return df


def run_us_based_scenario_selector(file_path):
    df = pd.read_excel(file_path)

    # ---------------- SCORING FUNCTIONS ----------------
    def assign_actor_score(row):
        if row['Actors_Vehicle'] == 1: return 5
        elif row['Actors_Pedestrian'] == 1: return 4
        elif row['Actors_Pedal cyclist'] == 1: return 2
        elif row['Actors_Animal'] == 1: return 1
        elif row['Actors_Other'] == 1: return 1
        return 0

    def assign_maneuver_score(row):
        if row['Driving Maneuver_Driving Straight'] == 1: return 14
        elif row['Driving Maneuver_Negotiating a Curve'] == 1: return 13
        elif row['Driving Maneuver_Turning Left'] == 1: return 12
        elif row['Driving Maneuver_Passing or Overtaking Another Vehicle'] == 1: return 11
        elif row['Driving Maneuver_Merging/Changing Lanes'] == 1: return 10
        elif row['Driving Maneuver_Stopped in Roadway'] == 1: return 9
        elif row['Driving Maneuver_Other Maneuver'] == 1: return 8
        elif row['Driving Maneuver_Turning Right'] == 1: return 7
        elif row['Driving Maneuver_Backing Up'] == 1: return 4
        return 0

    def assign_weather_score(row):
        if row['Weather_Dry'] == 1: return 4
        elif row['Weather_Rain'] == 1: return 3
        elif row['Weather_Fog'] == 1: return 2
        elif row['Weather_Snow'] == 1: return 1
        return 0

    def assign_lighting_score(row):
        if row['Light_Day'] == 1: return 5
        elif row['Light_Dark'] == 1: return 4
        elif row['Light_Twilight'] == 1: return 3
        return 0

    # ---------------- APPLY SCORING ----------------
    df['actor_score'] = df.apply(assign_actor_score, axis=1)
    df['maneuver_score'] = df.apply(assign_maneuver_score, axis=1)
    df['weather_score'] = df.apply(assign_weather_score, axis=1)
    df['lighting_score'] = df.apply(assign_lighting_score, axis=1)

    df['total_score'] = (
        df['actor_score']
        + df['maneuver_score']
        + df['weather_score']
        + df['lighting_score']
    )

    # Preserve group order
    df['original_index'] = df.index
    df = df.sort_values(by=['Scenario_Group', 'total_score'], ascending=[True, False])
    df = df.sort_values(by=['original_index']).drop(columns=['original_index'])

    # ---------------- PRIORITY CALCULATION ----------------
    current_priority = 0
    priority_list = []

    for _, group in df.groupby('Scenario_Group', sort=False):
        group_priority = group['total_score'].rank(method='dense', ascending=False).astype(int)
        group_priority += current_priority
        current_priority = group_priority.max()
        priority_list.extend(group_priority)

    df['priority'] = priority_list

    # Sort by priority
    df = df.sort_values(by='priority', ascending=True)

    # Save output
    df.to_excel(SELECTED_SCENARIOS_US_PATH, index=False)
    print(f"US scenarios selected → {SELECTED_SCENARIOS_US_PATH}")

    return df
