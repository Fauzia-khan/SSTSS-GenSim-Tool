import pandas as pd
from PyQt5.QtWidgets import QMessageBox

def remove_duplicate_scenarios(input_file="formulated_scenario_groups.xlsx", output_file="duplicate_removal.xlsx"):
    """
    Removes duplicate scenarios from the formulated_scenario_groups.xlsx file.

    Parameters:
        input_file: path to the formulated scenario groups Excel file
        output_file: path where the cleaned version will be saved
    """

    try:
        # Load Excel file into pandas DataFrame
        df = pd.read_excel(input_file)

        # Remove exact duplicate rows
        df_cleaned = df.drop_duplicates()

        # Optionally, remove duplicates based on only certain columns
        # For example, if scenario_id is the unique identifier:
        # df_cleaned = df.drop_duplicates(subset=['Scenario_ID'])

        # Save cleaned data
        df_cleaned.to_excel(output_file, index=False)

        QMessageBox.information(None, "Duplicates Removed",
                                f"Duplicates removed successfully!\nCleaned file saved as:\n{output_file}")

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error removing duplicates:\n{str(e)}")
