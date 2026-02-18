import shutil
from PyQt5.QtWidgets import QMessageBox
from Scenario_Selection_Module import (
    FORMULATED_SCENARIO_GROUPS_PATH,
    DUPLICATE_SCENARIO_REMOVAL_PATH
)

def remove_duplicate_scenarios(
    input_file=FORMULATED_SCENARIO_GROUPS_PATH,
    output_file=DUPLICATE_SCENARIO_REMOVAL_PATH
):
    """
    TEMP VERSION:
    Makes an EXACT copy of the input XLSX file.
    No duplicate removal is performed.
    """

    print("COPY INPUT :", input_file)
    print("COPY OUTPUT:", output_file)

    try:
        shutil.copyfile(input_file, output_file)

        QMessageBox.information(
            None,
            "Duplicate Removal (Placeholder)",
            f"No duplicates removed yet.\nFile copied to:\n{output_file}"
        )

    except Exception as e:
        QMessageBox.critical(
            None,
            "Error",
            f"Error copying file:\n{str(e)}"
        )

