from PyQt5.QtWidgets import QVBoxLayout, QDialog, QPushButton, QCheckBox, QGroupBox, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
import pandas as pd
from modules.constants import ODD_excel_file_name
from PyQt5.QtCore import Qt
from Scenario_Selection_Module import USER_SELECTED_ODD_PATH

class SelectODDWindow(QDialog):
    odd_saved = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select ODD")
        self.setGeometry(400, 100, 400, 500)
        self.setStyleSheet("background-color: #e9f0fa;")

        layout = QVBoxLayout()

        # Dictionary to store the checkbox states for saving
        self.data = {
            'Dynamic Elements': {
                'Subject Vehicle': {
                    'Speed': {
                        '10 km/h - 30 km/h': 0,
                        '30 km/h - 60 km/h': 0,
                        '60 km/h - 90 km/h': 0,
                    },
                    'Vehicle Type': {
                        'Car': 0,
                        'Truck': 0,
                        'Bus': 0,
                    }
                },
                'Traffic': {
                    'Agents': {
                        'Animal': 0,
                        'Human': {
                            'Pedestrian': 0,
                            'Cyclist': 0,
                            'Motorcyclist': 0,
                        },
                        'Vehicle': 0
                    },
                    'Density of Agents': {
                        'Low': 0,
                        'Medium': 0,
                        'High': 0
                    }
                }
            },

            'Environmental Conditions': {
                'Weather': {
                    'Snow': 0,
                    'Dry': 0,
                    'Fog': 0,
                    'Rain': 0
                },
                'Light': {
                    'Light': 0,
                    'Dark': 0
                }
            },

            'Scenery': {
                'Regions': {
                    'Urban Roads': 0,
                    'Rural Roads': 0,
                    'Suburbs': 0
                },
                'Road Types': {
                    'Radial Roads': 0,
                    'Distributor Roads': 0,
                    'Minor Roads': 0,
                    'Slip Roads': 0,
                    'Parking': 0,
                    'Shared Spaces': 0
                },
                'Junctions': {
                    'Intersections': {
                        'Signalized': 0,
                        'Non-Signalized': 0
                    },
                    'Roundabouts': 0,
                    'Non-Junction': 0
                }
            }
        }

        # Create the dynamic elements section
        # Create the dynamic elements section
        self.dynamic_elements_group = self.create_collapsible_section("Dynamic Elements", [
            ("Subject Vehicle", True, [
                ("Speed", True, [("10 km/h - 30 km/h", False), ("30 km/h - 60 km/h", False), ("60 km/h - 90 km/h", False)]),
                ("Vehicle Type", True, [("Car", False), ("Truck", False), ("Bus", False)])
            ]),
            ("Traffic", True, [
                ("Agents", True, [
                    ("Animal", False),
                    ("Human", True, [
                        ("Pedestrian", False),
                        ("Cyclist", False),
                        ("Motorcyclist", False)
                    ]),
                    ("Vehicle", False)
                ]),
                ("Density of Agents", True, [("Low", False), ("Medium", False), ("High", False)])
            ])
        ], self.data['Dynamic Elements'])

        layout.addWidget(self.dynamic_elements_group)

        # Create the environmental conditions section
        self.environmental_conditions_group = self.create_collapsible_section("Environmental Conditions", [
            ("Weather", True, [("Snow", False), ("Dry", False), ("Fog", False), ("Rain", False)]),
            ("Light", True, [("Light", False), ("Dark", False)])
        ], self.data['Environmental Conditions'])
        layout.addWidget(self.environmental_conditions_group)

        # Create the scenery section
        self.scenery_group = self.create_collapsible_section("Scenery", [
            ("Regions", True, [("Urban Roads", False), ("Rural Roads", False), ("Suburbs", False)]),
            ("Road Types", True, [("Radial Roads", False), ("Distributor Roads", False), ("Minor Roads", False),
                                  ("Slip Roads", False), ("Parking", False), ("Shared Spaces", False)]),
            ("Junctions", True, [
                ("Intersections", True, [("Signalized", False), ("Non-Signalized", False)]),
                ("Roundabouts", False),
                ("Non-Junction", False)
            ])
        ], self.data['Scenery'])
        layout.addWidget(self.scenery_group)

        # Add a save button
        self.save_button = QPushButton("Save ODD")
        self.save_button.clicked.connect(self.save_odd_selection)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def create_collapsible_section(self, title, items, data_section):
        """Creates a collapsible section with a '+' button for expansion."""
        group_box = QGroupBox()
        group_box_layout = QVBoxLayout()
        group_box.setLayout(group_box_layout)

        # Button to expand/collapse
        toggle_button = QPushButton(f"+ {title}")
        toggle_button.setCheckable(True)
        toggle_button.setStyleSheet("text-align: left;")  # Align the button text to the left
        group_box_layout.addWidget(toggle_button)

        # Create a container widget for the checkboxes/options
        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_widget.setLayout(container_layout)
        container_widget.setVisible(False)  # Initially hidden

        # Add the checkboxes or nested items
        self.add_items(container_layout, items, data_section)

        group_box_layout.addWidget(container_widget)

        # Connect button toggle to show/hide the container widget
        toggle_button.toggled.connect(lambda: container_widget.setVisible(toggle_button.isChecked()))

        return group_box

    def add_items(self, layout, items, data_section):
        """Adds items (checkboxes or nested collapsible sections) to the layout."""
        for item in items:
            if isinstance(item, tuple) and len(item) == 3 and isinstance(item[2], list):  # Nested section
                sub_group = self.create_collapsible_section(item[0], item[2], data_section[item[0]])
                layout.addWidget(sub_group)
            else:
                checkbox = QCheckBox(item[0])
                checkbox.stateChanged.connect(lambda state, key=item[0]: self.update_data(state, key, data_section))
                layout.addWidget(checkbox)

    def update_data(self, state, key, data_section):
        """Updates the corresponding data in the dictionary based on the checkbox state."""
        data_section[key] = 1 if state == Qt.Checked else 0

    import pandas as pd

    def save_odd_selection(self):
        """Saves the ODD selection into an Excel file with a multi-level column structure."""
        print("Saving ODD selections to Excel...")

        try:
            # Print debug info
            print("Dynamic Elements:", self.data.get('Dynamic Elements'))
            print("Environmental Conditions:", self.data.get('Environmental Conditions'))
            print("Scenery:", self.data.get('Scenery'))

            # Define the multi-level column structure
            columns = pd.MultiIndex.from_tuples([
                # Dynamic Elements
                ('Dynamic Elements', 'Subject Vehicle', 'Speed', '10 km/h - 30 km/h',''),
                ('Dynamic Elements', 'Subject Vehicle', 'Speed', '30 km/h - 60 km/h',''),
                ('Dynamic Elements', 'Subject Vehicle', 'Speed', '60 km/h - 90 km/h',''),
                ('Dynamic Elements', 'Subject Vehicle', 'Vehicle Type', 'Car',''),
                ('Dynamic Elements', 'Subject Vehicle', 'Vehicle Type', 'Truck',''),
                ('Dynamic Elements', 'Subject Vehicle', 'Vehicle Type', 'Bus',''),
                ('Dynamic Elements', 'Traffic', 'Agents', 'Animal',''),
                ('Dynamic Elements', 'Traffic', 'Agents', 'Human', 'Pedestrian',''),
                ('Dynamic Elements', 'Traffic', 'Agents', 'Human', 'Cyclist',''),
                ('Dynamic Elements', 'Traffic', 'Agents', 'Human', 'Motorcyclist',''),
                ('Dynamic Elements', 'Traffic', 'Agents', 'Vehicle',''),
                ('Dynamic Elements', 'Traffic', 'Density of Agents', 'Low',''),
                ('Dynamic Elements', 'Traffic', 'Density of Agents', 'Medium',''),
                ('Dynamic Elements', 'Traffic', 'Density of Agents', 'High',''),

                # Environmental Conditions
                ('Environmental Conditions', 'Weather', 'Snow', '',''),
                ('Environmental Conditions', 'Weather', 'Rain', '',''),
                ('Environmental Conditions', 'Weather', 'Fog', '',''),
                ('Environmental Conditions', 'Weather', 'Dry', '',''),
                ('Environmental Conditions', 'Light', 'Light', '',''),
                ('Environmental Conditions', 'Light', 'Dark', '',''),

                # Scenery
                ('Scenery', 'Regions', 'Urban Roads', '',''),
                ('Scenery', 'Regions', 'Rural Roads', '',''),
                ('Scenery', 'Regions', 'Suburbs', '',''),
                ('Scenery', 'Road Types', 'Radial Roads', '',''),
                ('Scenery', 'Road Types', 'Distributor Roads', '',''),
                ('Scenery', 'Road Types', 'Minor Roads', '',''),
                ('Scenery', 'Road Types', 'Slip Roads', '',''),
                ('Scenery', 'Road Types', 'Parking', '',''),
                ('Scenery', 'Road Types', 'Shared Spaces', '',''),
                ('Scenery', 'Junctions', 'Roundabouts', '',''),
                ('Scenery', 'Junctions', 'Non-Junction', '',''),
                ('Scenery', 'Junctions', 'Intersections', 'Signalized',''),
                ('Scenery', 'Junctions', 'Intersections', 'Non-Signalized',''),
            ])

            # Populate data row according to the updated data structure
            row = [
                # Dynamic Elements - Subject Vehicle
                self.data['Dynamic Elements']['Subject Vehicle']['Speed']['10 km/h - 30 km/h'],
                self.data['Dynamic Elements']['Subject Vehicle']['Speed']['30 km/h - 60 km/h'],
                self.data['Dynamic Elements']['Subject Vehicle']['Speed']['60 km/h - 90 km/h'],
                self.data['Dynamic Elements']['Subject Vehicle']['Vehicle Type']['Car'],
                self.data['Dynamic Elements']['Subject Vehicle']['Vehicle Type']['Truck'],
                self.data['Dynamic Elements']['Subject Vehicle']['Vehicle Type']['Bus'],

                # Dynamic Elements - Traffic
                self.data['Dynamic Elements']['Traffic']['Agents']['Animal'],
                self.data['Dynamic Elements']['Traffic']['Agents']['Human']['Pedestrian'],
                self.data['Dynamic Elements']['Traffic']['Agents']['Human']['Cyclist'],
                self.data['Dynamic Elements']['Traffic']['Agents']['Human']['Motorcyclist'],
                self.data['Dynamic Elements']['Traffic']['Agents']['Vehicle'],
                self.data['Dynamic Elements']['Traffic']['Density of Agents']['Low'],
                self.data['Dynamic Elements']['Traffic']['Density of Agents']['Medium'],
                self.data['Dynamic Elements']['Traffic']['Density of Agents']['High'],

                # Environmental Conditions
                self.data['Environmental Conditions']['Weather']['Snow'],
                self.data['Environmental Conditions']['Weather']['Rain'],
                self.data['Environmental Conditions']['Weather']['Fog'],
                self.data['Environmental Conditions']['Weather']['Dry'],
                self.data['Environmental Conditions']['Light']['Light'],
                self.data['Environmental Conditions']['Light']['Dark'],

                # Scenery
                self.data['Scenery']['Regions']['Urban Roads'],
                self.data['Scenery']['Regions']['Rural Roads'],
                self.data['Scenery']['Regions']['Suburbs'],
                self.data['Scenery']['Road Types']['Radial Roads'],
                self.data['Scenery']['Road Types']['Distributor Roads'],
                self.data['Scenery']['Road Types']['Minor Roads'],
                self.data['Scenery']['Road Types']['Slip Roads'],
                self.data['Scenery']['Road Types']['Parking'],
                self.data['Scenery']['Road Types']['Shared Spaces'],
                self.data['Scenery']['Junctions']['Roundabouts'],
                self.data['Scenery']['Junctions']['Non-Junction'],
                self.data['Scenery']['Junctions']['Intersections']['Signalized'],
                self.data['Scenery']['Junctions']['Intersections']['Non-Signalized'],
            ]

            # Create DataFrame with the multi-level index and the populated data
            df = pd.DataFrame([row], columns=columns)

            # Save the DataFrame to an Excel file with merged cells for the parent categories
            file_path = USER_SELECTED_ODD_PATH
            df.to_excel(file_path, index=True, merge_cells=True)

            print(f"ODD selections saved successfully to: {file_path}")
            self.odd_saved.emit()
        except Exception as e:
            print(f"Error occurred: {e}")
