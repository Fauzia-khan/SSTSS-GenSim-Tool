
import os
import time
import subprocess
import threading
import signal
from Scenario_Execution_Module.simulation_control import run_scenario_runner, stop_autoware
from Scenario_Implementation_Module.scenario_template import update_follow_leading_vehicle_template
from Simulator_ADS_Module.carla_control import launch_carla
from Simulator_ADS_Module.autoware_control import launch_autoware
from Data_Collection_Module.metrics_control import run_metrics
from Data_Visualization_and_Report_Module.results_utils import (
    find_latest_result_timestamp,
    get_result_files,
    read_summary_log,
    zip_results
)
from Data_Visualization_and_Report_Module.results_backup import backup_simulation_outputs
from Scenario_Configuration_Module.weather_control import (
    update_weather_and_light,
    get_weather_type
)
from Scenario_Configuration_Module.excel_parser import parse_scenario_tags
from Data_Visualization_and_Report_Module.plot_metrics import (
    plot_speed_and_distance,
    plot_jerk,
)

from Safety_Evaluation_Module.safety_metrices import process_latest_raw_file

from config import RESULTS_DIR


from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFormLayout,
    QMessageBox, QDialog, QScrollArea, QCheckBox, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QFileDialog
)
from openpyxl import load_workbook
from xml.etree.ElementTree import Element, SubElement, ElementTree
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


class ViewInformationWindow(QDialog):
    def __init__(self, excel_filename=None, scenario_row=None):
        super().__init__()

        scenario_row += 1  # skip header row

        self.setWindowTitle('Scenario Parameter Configuration')
        self.setGeometry(300, 200, 500, 300)
        self.global_light_condition = None
        wb = load_workbook(excel_filename)
        ws = wb.active
        self.setStyleSheet("background-color: #e9f0fa;")   # Azure-like blue

        # Main layout
        main_layout = QHBoxLayout()

        # Left side: tags
        tag_layout = QFormLayout()
        tag_layout.addRow(QLabel("<b>Tags</b>"), QLabel(""))

        tag_data = {}

        # Column ranges
        actor_column_start, actor_column_end = 5, 10
        weather_column_start, weather_column_end = 11, 14
        light_column_start, light_column_end = 15, 17
        behaviour_column_start, behaviour_column_end = 18, 32
        road_topology_column_start, road_topology_column_end = 33, 35
        scenario_group_column = 38

        self.tag_data, self.global_light_condition = parse_scenario_tags(excel_filename, scenario_row)

        for category, items in self.tag_data.items():
            tag_layout.addRow(QLabel(f"<b>{category}</b>"), QLabel(""))
            for item in items:
                tag_layout.addRow(QLabel(f"    {item}"), QLabel(""))

        # Right side: controls
        files_layout = QFormLayout()
        files_layout.addRow(QLabel("<b>Files</b>"), QLabel(""))

        # Inputs
        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Enter ego vehicle speed")
        self.other_actor_speed_input = QLineEdit()
        self.other_actor_speed_input.setPlaceholderText("Enter other actor speed")
        self.other_actor_distance_input = QLineEdit()
        self.other_actor_distance_input.setPlaceholderText("Enter other actor distance")
        self.timeout_input = QLineEdit()
        self.timeout_input.setPlaceholderText("Enter simulation duration")

        # Ego vehicle dropdown
        self.ego_vehicle_dropdown = QComboBox()
        vehicle_options = ["Nissan.patrol","Tesla Model3", "Tesla Cybertruck", "Audi A2", "BMW X5", "Mercedes C-Class"]
        self.ego_vehicle_dropdown.addItems(vehicle_options)
        files_layout.addRow(QLabel("Select Model for other vehicle"), self.ego_vehicle_dropdown)

        # Map dropdown
        self.map_dropdown = QComboBox()
        map_options = ["Town01", "Town02", "Town03", "Town04", "Town05", "Town06", "Town07"]
        self.map_dropdown.addItems(map_options)
        files_layout.addRow(QLabel("Select Map"), self.map_dropdown)

        # Buttons
        execute_sim_button = QPushButton("Execute Simulation")
        execute_sim_button.setFixedSize(150, 25)
        execute_sim_button.clicked.connect(self.execute_simulation)

        self.show_results_button = QPushButton("Show Results")
        self.show_results_button.setFixedSize(150, 25)
        self.show_results_button.setEnabled(False)
        self.show_results_button.clicked.connect(self.show_results)

        # Add inputs
        files_layout.addRow(QLabel("Select Speed for Ego vehicle"), self.speed_input)
        files_layout.addRow(QLabel("Enter Speed of Other Actor"), self.other_actor_speed_input)
        files_layout.addRow(QLabel("Enter Distance of Other Actor"), self.other_actor_distance_input)
        files_layout.addRow(QLabel("Enter Simulation Duration"), self.timeout_input)
        files_layout.addRow(execute_sim_button)
        files_layout.addRow(self.show_results_button)

        # Add layouts to main
        main_layout.addLayout(tag_layout)
        main_layout.addLayout(files_layout)
        self.setLayout(main_layout)

    # ------------------- Simulation Control -------------------

    def execute_simulation(self):
        print("In: Execute Simulation")
        ego_vehicle_speed = self.speed_input.text()
        other_vehicle_distance = self.other_actor_distance_input.text()
        other_vehicle_speed = self.other_actor_speed_input.text()
        timeout = self.timeout_input.text()

        update_follow_leading_vehicle_template(
            timeout=timeout,
            distance=other_vehicle_distance,
            speed=other_vehicle_speed
        )

        # ------------------------------------------
        # 1) WEATHER + LIGHT UPDATE FROM EXCEL
        # ------------------------------------------
        from Scenario_Configuration_Module.weather_control import (
            update_weather_and_light,
            get_weather_type
        )

        # tag_data was created earlier in __init__, so use it from self
        weather_type = get_weather_type(self.tag_data)
        # FIX LIGHT CONDITION
        raw_light = self.global_light_condition[0].strip().lower()
        if raw_light in ["d", "day", "sunny", "light"]:
            light = "Day"
        else:
            light = "Night"

        print(f"[SIM] Applying Environment -> Weather: {weather_type}, Light: {light}")
        update_weather_and_light(weather_type, light)
        # ------------------------------------------

        # Start CARLA
        launch_carla()

        # Start Autoware
        launch_autoware()

        # Run ScenarioRunner
        results_dir = "/home/laima/Documents/scenario_runner-master/results/test"
        os.makedirs(results_dir, exist_ok=True)
        summary_log = os.path.join(results_dir, "scenario_summary.log")

        runner_thread = threading.Thread(
            target=run_scenario_runner,
            args=(summary_log,)
        )
        runner_thread.start()

        # Run set_goal
        os.system('gnome-terminal -- bash -c "./run_set_goal.sh; exec bash"')

        # Wait for ScenarioRunner
        runner_thread.join()

        # Stop Autoware
        stop_autoware()

        # Run Metrics
        success = run_metrics()
        if success:
            self.show_results_button.setEnabled(True)
        else:
            QMessageBox.warning(self, "Metrics Error",
                                "Failed to compute metrics. See console for details.")
            return

    # ------------------- Results Display -------------------

    def show_results(self):
        from PyQt5.QtWidgets import (
            QDialog, QVBoxLayout, QLabel, QScrollArea,
            QWidget, QPushButton, QFileDialog, QMessageBox
        )
        from PyQt5.QtGui import QPixmap, QFont
        from PyQt5.QtCore import Qt

        # ---- IMPORT VISUALIZATION CONTROLLER ----
        try:
            from Data_Visualization_and_Report_Module.visualization_controller \
                import process_visualization, create_zip_for_download
        except Exception as e:
            QMessageBox.warning(self, "Import Error", f"Cannot load visualization module:\n{e}")
            return

        # ---- RUN VISUALIZATION ----
        result = process_visualization()

        if not result:
            QMessageBox.warning(self, "No Results", "No visualization data found.")
            return

        # Get returned files from controller
        speed_plot = result["plot_speed"]
        jerk_plot = result["plot_jerk"]
        summary_text = result["summary_text"]
        summary_path = result["summary_path"]
        all_files = result["all_files"]
        timestamp = result["timestamp"]

        # ---- GUI WINDOW ----
        dialog = QDialog(self)
        dialog.setWindowTitle("Simulation Report")
        dialog.resize(1000, 800)

        layout = QVBoxLayout()
        container = QWidget()
        container_layout = QVBoxLayout(container)

        # ---- DISPLAY SPEED PLOT ----
        if os.path.exists(speed_plot):
            pix = QPixmap(speed_plot)
            lbl = QLabel()
            lbl.setPixmap(pix.scaledToWidth(900, Qt.SmoothTransformation))
            lbl.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(lbl)

        # ---- DISPLAY JERK PLOT ----
        if os.path.exists(jerk_plot):
            pix2 = QPixmap(jerk_plot)
            lbl2 = QLabel()
            lbl2.setPixmap(pix2.scaledToWidth(900, Qt.SmoothTransformation))
            lbl2.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(lbl2)

        # ---- SUMMARY TEXT ----
        if summary_text:
            summary_label = QLabel(summary_text)
            summary_label.setFont(QFont("Courier", 10))
            summary_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            summary_label.setWordWrap(True)
            container_layout.addWidget(QLabel("---- Scenario Summary ----"))
            container_layout.addWidget(summary_label)

        # ---- DOWNLOAD BUTTON ----
        def download_all():
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Results As",
                f"simulation_results_{timestamp}.zip",
                "Zip Files (*.zip)"
            )
            if save_path:
                create_zip_for_download(save_path, all_files, summary_path)
                QMessageBox.information(self, "Saved", f"Files saved to:\n{save_path}")

        btn = QPushButton("Download All Files")
        btn.clicked.connect(download_all)
        container_layout.addWidget(btn, alignment=Qt.AlignCenter)

        # ---- SCROLL AREA ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        dialog.setLayout(layout)
        dialog.exec_()


