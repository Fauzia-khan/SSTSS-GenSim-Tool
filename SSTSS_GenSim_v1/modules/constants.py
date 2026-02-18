
#scenarios_excel_file_name = 'user_selected_scenarios_from_catalog.xlsx'
#SCENARIO_RUNNER_ROOT = "/home/laima/Desktop/SSTSS Tool 1st september/SSTSS_GenSim_Tool"
import os
SCENARIO_RUNNER_ROOT = os.getcwd()

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # points to modules/
SCENARIO_SELECTION_DIR = os.path.join(BASE_DIR, "..", "Scenario_Selection_Module")

scenarios_excel_file_name1 = os.path.join(SCENARIO_SELECTION_DIR, "catalog_scenarios.xlsx")

scenarios_excel_file_name = 'formulated_scenario_groups.xlsx'

ODD_excel_file_name = "odd_selection_nested_structure.xlsx"

selected_scenarios_based_on_ODD_file_name = 'ODD_selected_scenarios.xlsx'

catalog_code_map = {
    "US": "SC1",
    "Singapore": "SC2",
    "Europe": "SC3",
    "Other": "SC4"
}

ODD_format = {
    "Dynamic Elements": {
        "Subject Vehicle": {
            "Speed": [
                "10 km/h - 30 km/h",
                "30 km/h - 60 km/h",
                "60 km/h - 90 km/h"
            ],
            "Vehicle Type": ["Car", "Truck", "Bus", "Animal"]
        },
        "Traffic": {
            "Agents": {
                "Human": ["Pedestrian", "Cyclist", "Motorcyclist"],
                "Vehicle": ["Car", "Truck", "Bus"]
            },
            "Density of Agents": ["Low", "Medium", "High"]
        }
    },
    "Environmental Conditions": {
        "Weather": ["Snow", "Rain", "Fog", "Dry"],
        "Light": ["Light", "Dark"],
        "Regions": ["Urban Road", "Rural Road", "Suburbs"]
    },
    "Scenery": {
        "Road Types": [
            "Radial Road", "Distributor Road", "Minor Road",
            "Slip Roads", "Parking", "Shared Space", "Roundabout"
        ],
        "Junctions": {
            "Intersections": ["Signalized", "Non-Signalized"]
        }
    }
}

print(ODD_format)
