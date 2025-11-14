import pandas as pd

def run_eu_based_scenario_selector():
    file_path = 'filtered_scenarios_Carla.xlsx'  # Replace with the actual path to your file
    df = pd.read_excel(file_path)
    # Define the scoring functions (same as before)
    def assign_actor_score(row):
        if row['Actors_Vehicle'] == 1:
            return 4
        elif row['Actors_Pedestrian'] == 1:
            return 3
        elif row['Actors_Motorcyclist'] == 1:
            return 2
        elif row['Actors_Pedal cyclist'] == 1:
            return 1
        elif row['Actors_Animal'] == 1:
            return 1
        elif row['Actors_Other'] == 1:
            return 1
        else:
            return 0

    def assign_maneuver_score(row):
        if row['Driving Maneuver_Driving Straight'] == 1:
            return 7
        elif row['Driving Maneuver_Negotiating a Curve'] == 1:
            return 5
        elif row['Driving Maneuver_Turning Left'] == 1:
            return 6
        elif row['Driving Maneuver_Passing or Overtaking Another Vehicle'] == 1:
            return 0
        elif row['Driving Maneuver_Merging/Changing Lanes'] == 1:
            return 4
        elif row['Driving Maneuver_Stopped in Roadway'] == 1:
            return 0
        elif row['Driving Maneuver_Other Maneuver'] == 1:
            return 0
        elif row['Driving Maneuver_Turning Right'] == 1:
            return 3
        elif row['Driving Maneuver_Decelerating in Road'] == 1:
            return 0
        elif row['Driving Maneuver_Starting in Road'] == 1:
            return 0
        elif row['Driving Maneuver_Making a U-turn'] == 1:
            return 1
        elif row['Driving Maneuver_Backing Up'] == 1:
            return 2
        elif row['Driving Maneuver_Parked in Travel Lane'] == 1:
            return 0
        elif row['Driving Maneuver_Leaving a Parking Position'] == 1:
            return 0
        elif row['Driving Maneuver_Entering a Parking Position'] == 1:
            return 0
        else:
            return 0

    def assign_weather_score(row):
        if row['Weather_Dry'] == 1:
            return 4
        elif row['Weather_Rain'] == 1:
            return 2
        elif row['Weather_Fog'] == 1: #unknown/other
            return 3
        elif row['Weather_Snow'] == 1:
            return 1
        else:
            return 0

    def assign_lighting_score(row):
        if row['Light_Day'] == 1:
            return 4
        elif row['Light_Dark'] == 1: #streetlights
            return 3
        # elif row['Light_Unknown/other'] == 1: #dark,butlighted
        # return 2
        elif row['Light_Twilight'] == 1:
            return 1

        else:
            return 0

    # Apply the scoring functions
    df['actor_score'] = df.apply(assign_actor_score, axis=1)
    df['maneuver_score'] = df.apply(assign_maneuver_score, axis=1)
    df['weather_score'] = df.apply(assign_weather_score, axis=1)
    df['lighting_score'] = df.apply(assign_lighting_score, axis=1)

    # Compute total score
    df['total_score'] = df['actor_score'] + df['maneuver_score'] + df['weather_score'] + df['lighting_score']

    print("before sorting")
    print(df.head(5)["Scenario_Group"])

    # Add index to preserve original order of groups
    df['original_index'] = df.index

    # Sort within each Scenario Group by total_score (Descending), without changing group order
    df = df.sort_values(by=['Scenario_Group', 'total_score'], ascending=[True, False])

    # Restore original group order by sorting by original index
    df = df.sort_values(by=['original_index']).drop(columns=['original_index'])

    print("after sorting")
    print(df.head(5)["Scenario_Group"])

    # Step 2: Assign priority across all groups with continuous ranking
    current_priority = 0
    priorities = []

    for group_name, group in df.groupby('Scenario_Group', sort=False):
        # Rank within group and add offset
        group_priority = group['total_score'].rank(method='dense', ascending=False).astype(int)
        group_priority += current_priority  # Add offset from previous groups
        current_priority = group_priority.max()  # Update offset for the next group

        priorities.extend(group_priority)

    df['priority'] = priorities

    # Step 3: Sort by priority for better readability in Excel
    df = df.sort_values(by='priority', ascending=True)

    # Save the sorted data with priority to a new Excel file
    output_file = 'selected_scenarios_eu.xlsx'
    df.to_excel(output_file, index=False)

    # Display the relevant columns (optional)
    print(df[['Scenario_Group', 'total_score', 'priority']])
    return df


def run_us_based_scenario_selector():
    file_path = 'filtered_scenarios_Carla.xlsx'  # Replace with the actual path to your file
    df = pd.read_excel(file_path)

    # Define the scoring functions (same as before)
    def assign_actor_score(row):
        if row['Actors_Vehicle'] == 1:
            return 5
        elif row['Actors_Pedestrian'] == 1:
            return 4
        elif row['Actors_Pedal cyclist'] == 1:
            return 2
       # elif row['Actors_Pedal cyclist'] == 1:
           # return 2
        elif row['Actors_Animal'] == 1:
            return 1
        elif row['Actors_Other'] == 1:
            return 1
        else:
            return 0

    def assign_maneuver_score(row):
        if row['Driving Maneuver_Driving Straight'] == 1:
            return 14
        elif row['Driving Maneuver_Negotiating a Curve'] == 1:
            return 13
        elif row['Driving Maneuver_Turning Left'] == 1:
            return 12
        elif row['Driving Maneuver_Passing or Overtaking Another Vehicle'] == 1:
            return 11
        elif row['Driving Maneuver_Merging/Changing Lanes'] == 1:
            return 10
        elif row['Driving Maneuver_Stopped in Roadway'] == 1:
            return 9
        elif row['Driving Maneuver_Other Maneuver'] == 1:
            return 8
        elif row['Driving Maneuver_Turning Right'] == 1:
            return 7
        elif row['Driving Maneuver_Decelerating in Road'] == 1:
            return 6
        elif row['Driving Maneuver_Starting in Road'] == 1:
            return 5
        elif row['Driving Maneuver_Making a U-turn'] == 1:
            return 5
        elif row['Driving Maneuver_Backing Up'] == 1:
            return 4
        elif row['Driving Maneuver_Parked in Travel Lane'] == 1:
            return 3
        elif row['Driving Maneuver_Leaving a Parking Position'] == 1:
            return 2
        elif row['Driving Maneuver_Entering a Parking Position'] == 1:
            return 1
        else:
            return 0

    def assign_weather_score(row):
        if row['Weather_Dry'] == 1:
            return 4
        elif row['Weather_Rain'] == 1:
            return 3
        elif row['Weather_Fog'] == 1: #other/unknown
            return 2
        elif row['Weather_Snow'] == 1:
            return 1
        else:
            return 0

    def assign_lighting_score(row):
        if row['Light_Day'] == 1:
            return 5
        elif row['Light_Dark'] == 1:
            return 4
        elif row['Light_Twilight'] == 1: #dark,butlighted=2
            return 3
        #elif row['Light_Unknown/other'] == 1: #dark,butlighted
            #return 1
        else:
            return 0

    # Apply the scoring functions
    df['actor_score'] = df.apply(assign_actor_score, axis=1)
    df['maneuver_score'] = df.apply(assign_maneuver_score, axis=1)
    df['weather_score'] = df.apply(assign_weather_score, axis=1)
    df['lighting_score'] = df.apply(assign_lighting_score, axis=1)

    # Compute total score
    df['total_score'] = df['actor_score'] + df['maneuver_score'] + df['weather_score'] + df['lighting_score']

    #print("before sorting")
    #print(df.head(5)["Scenario_Group"])

    # Add index to preserve original order of groups
    df['original_index'] = df.index

    # Sort within each Scenario Group by total_score (Descending), without changing group order
    df = df.sort_values(by=['Scenario_Group', 'total_score'], ascending=[True, False])

    # Restore original group order by sorting by original index
    df = df.sort_values(by=['original_index']).drop(columns=['original_index'])

    #print("after sorting")
    #print(df.head(5)["Scenario_Group"])

    # Step 2: Assign priority across all groups with continuous ranking
    current_priority = 0
    priorities = []

    for group_name, group in df.groupby('Scenario_Group', sort=False):
        # Rank within group and add offset
        group_priority = group['total_score'].rank(method='dense', ascending=False).astype(int)
        group_priority += current_priority  # Add offset from previous groups
        current_priority = group_priority.max()  # Update offset for the next group

        priorities.extend(group_priority)

    df['priority'] = priorities

    # Step 3: Sort by priority for better readability in Excel
    df = df.sort_values(by='priority', ascending=True)

    # Save the sorted data with priority to a new Excel file
    output_file = 'selected_scenarios_us.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Testing scenarios are selected, see file {output_file}")

    # Display the relevant columns (optional)
    #print(df[['Scenario_Group', 'total_score', 'priority']])
    #return df

# #######
# # import tkinter as tk
# # from tkinter import ttk
# # import pandas as pd
# #
# # # Function to display selected columns from the dataframe in a form (Tkinter Table)
# # def display_scenario_data(df):
# #     # Select only the relevant columns to display
# #     selected_columns = ['Scenario ID_Unnamed: 1_level_1', 'Description_Unnamed: 3_level_1', 'Scenario ID_Unnamed: 1_level_1', 'image']  # Replace with your actual column names
# #     df_filtered = df[selected_columns]
# #
# #     # Create a new window
# #     window = tk.Toplevel()  # Creates a new window
# #     window.title("Scenario Details")
# #
# #     # Create a Treeview to display data in table format
# #     tree = ttk.Treeview(window, columns=list(df_filtered.columns), show="headings", height=10)
# #
# #     # Define columns in the treeview
# #     for col in df_filtered.columns:
# #         tree.heading(col, text=col)
# #         tree.column(col, anchor=tk.W, width=150)  # Adjust width if needed
# #
# #     # Insert rows into the treeview
# #     for index, row in df_filtered.iterrows():
# #         tree.insert("", "end", values=list(row))
# #
# #     # Add a scrollbar to the Treeview
# #     scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
# #     tree.configure(yscroll=scrollbar.set)
# #
# #     tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# #     scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
# #
# #
# # # Function to run the EU-based scenario selector (already handled)
# # def run_eu_based_scenario_selector():
# #     file_path = 'selected_scenarios_eu.xlsx'  # Your file path
# #     df = pd.read_excel(file_path)
# #
# #     # Save the sorted data with priority to a new Excel file
# #     output_file = 'selected_scenarios_eu.xlsx'
# #     df.to_excel(output_file, index=False)
# #
# #     # Show the data in a form using Tkinter
# #     display_scenario_data(df)
# #
# #
# # # Function to run the US-based scenario selector (already handled)
# # def run_us_based_scenario_selector():
# #     file_path = 'selected_scenarios_us.xlsx'  # Your file path
# #     df = pd.read_excel(file_path)
# #
# #     # Save the sorted data with priority to a new Excel file
# #     output_file = 'selected_scenarios_us.xlsx'
# #     df.to_excel(output_file, index=False)
# #
# #     # Show the data in a form using Tkinter
# #     display_scenario_data(df)
# #
# #
# # # Trigger function to show the correct region file
# # def on_scenario_selector(region):
# #     # Based on region, select the appropriate function to display data
# #     if region == "EU":
# #         run_eu_based_scenario_selector()
# #     elif region == "US":
# #         run_us_based_scenario_selector()
# #
# #
# # # Main Tkinter window (this part is just for demonstration purposes to call the region directly)
# # def create_main_window(region="EU"):
# #     window = tk.Tk()
# #     window.title("Scenario Selector")
# #
# #     # Since the region is already handled externally, no dropdown is required
# #     # Directly call the function for selected region
# #     if region == "EU":
# #         run_eu_based_scenario_selector()
# #     elif region == "US":
# #         run_us_based_scenario_selector()
# #
# #     window.mainloop()
# #
# #
# # # Run the Tkinter main window (assuming EU is selected for the demonstration)
# # # You can replace "EU" with "US" based on your flow
# # create_main_window(region="EU")
#
# import tkinter as tk
# from tkinter import ttk
# import pandas as pd
#
# # Function to display selected columns from the dataframe in a form (Tkinter Table)
# def display_scenario_data(df):
#     # Rename the columns for display
#     df = df.rename(columns={
#         'Scenario ID_Unnamed: 1_level_1': 'Scenario ID',
#         'Description_Unnamed: 3_level_1': 'Scenario Description',
#         'image': 'Image'  # Rename the 'image' column if needed
#     })
#
#     # Select only the relevant columns to display
#     selected_columns = ['Scenario ID', 'Scenario Description', 'Image']  # Renamed column names
#     df_filtered = df[selected_columns]
#
#     # Create a new window to display data
#     window = tk.Toplevel()  # Creates a new window
#     window.title("Scenario Details")
#
#     # Create a Treeview to display data in table format
#     tree = ttk.Treeview(window, columns=list(df_filtered.columns), show="headings", height=10)
#
#     # Define columns in the treeview
#     for col in df_filtered.columns:
#         tree.heading(col, text=col)
#         tree.column(col, anchor=tk.W, width=150)  # Adjust width if needed
#
#     # Insert rows into the treeview
#     for index, row in df_filtered.iterrows():
#         # Convert the image path to an actual image using PIL
#         image_path = row['Image']
#         image = load_image(image_path)  # Load the image
#
#         # If the image is None (e.g., path is invalid), use a placeholder
#         if image is not None:
#             tree.insert("", "end", values=(row['Scenario ID'], row['Scenario Description'], image))
#         else:
#             tree.insert("", "end", values=(row['Scenario ID'], row['Scenario Description'], "No Image"))
#
#     # Add a scrollbar to the Treeview
#     scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
#     tree.configure(yscroll=scrollbar.set)
#
#     tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#     scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#
#
# # Function to load an image from the file path
# def load_image(image_path):
#     try:
#         # Open the image file
#         img = Image.open(image_path)
#         img = img.resize((50, 50))  # Resize image to fit in the table, adjust size as needed
#         return ImageTk.PhotoImage(img)
#     except Exception as e:
#         print(f"Error loading image: {e}")
#         return None
#
#
# # Function to run the EU-based scenario selector (already handled)
# def run_eu_based_scenario_selector():
#     file_path = 'selected_scenarios_eu.xlsx'  # Your file path
#     df = pd.read_excel(file_path)
#
#     # Show the data in a form using Tkinter
#     display_scenario_data(df)
#
#
# # Function to run the US-based scenario selector (already handled)
# def run_us_based_scenario_selector():
#     file_path = 'selected_scenarios_us.xlsx'  # Your file path
#     df = pd.read_excel(file_path)
#
#     # Show the data in a form using Tkinter
#     display_scenario_data(df)
#
#
# # Trigger function to show the correct region file
# def on_scenario_selector(region):
#     # Based on region, select the appropriate function to display data
#     if region == "EU":
#         run_eu_based_scenario_selector()
#     elif region == "US":
#         run_us_based_scenario_selector()
#
#
# # Main Tkinter window (this part is just for demonstration purposes to call the region directly)
# def create_main_window(region="EU"):
#     window = tk.Tk()
#     window.withdraw()  # Hide the main window as we do not need it
#
#     # Directly call the function for selected region
#     if region == "EU":
#         run_eu_based_scenario_selector()
#     elif region == "US":
#         run_us_based_scenario_selector()
#
#     window.mainloop()
#
#
# # Run the Tkinter main window (assuming EU is selected for the demonstration)
# # You can replace "EU" with "US" based on your flow
# create_main_window(region="EU")
#
#
#
#
#
#
