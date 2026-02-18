
import os
import time
import subprocess
import threading
import signal
import multiprocessing as mp
import queue as pyqueue

from PyQt5.QtCore import Qt, pyqtSignal
from Scenario_Execution_Module.simulation_control import run_scenario_runner, stop_autoware, stop_carla
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
import threading
import json

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
    QTableWidget, QTableWidgetItem, QFileDialog,QGroupBox
)
from openpyxl import load_workbook
from xml.etree.ElementTree import Element, SubElement, ElementTree
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


# --- brute-force cleanup (use your existing stop_autoware/stop_carla if you have them) ---
def brute_cleanup():
    # Autoware + related
    subprocess.run(["pkill", "-TERM", "-f", "roslaunch autoware_mini start_carla.launch"], check=False)
    subprocess.run(["pkill", "-TERM", "-f", "scenario_runner"], check=False)
    subprocess.run(["pkill", "-TERM", "-f", "run_set_goal.sh"], check=False)
    subprocess.run(["pkill", "-TERM", "-f", "terminator"], check=False)
    time.sleep(2)
    subprocess.run(["pkill", "-KILL", "-f", "roslaunch autoware_mini start_carla.launch"], check=False)
    subprocess.run(["pkill", "-KILL", "-f", "scenario_runner"], check=False)
    subprocess.run(["pkill", "-KILL", "-f", "run_set_goal.sh"], check=False)
    subprocess.run(["pkill", "-KILL", "-f", "terminator"], check=False)

    # CARLA
    subprocess.run(["pkill", "-TERM", "-f", "CarlaUE4"], check=False)
    subprocess.run(["pkill", "-TERM", "-f", "CarlaUnreal"], check=False)
    time.sleep(2)
    subprocess.run(["pkill", "-KILL", "-f", "CarlaUE4"], check=False)
    subprocess.run(["pkill", "-KILL", "-f", "CarlaUnreal"], check=False)
    subprocess.run(["bash", "-lc", "fuser -k 2000/tcp >/dev/null 2>&1 || true"], check=False)

def _run_once_child(q, params, sid, excel_filename, scenario_row, map_name, tag_data, global_light_condition):
    """
    Child process entry. Creates its own window object just to reuse your existing run_once_locked logic.
    (Minimal change: no refactor of run_once_locked.)
    """
    try:
        # Import here so child can start cleanly
        from PyQt5.QtWidgets import QApplication
        # Create a dummy Qt app if none exists (child process)
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Create instance and inject required state
        w = ViewInformationWindow(excel_filename=excel_filename, scenario_row=scenario_row)
        w.tag_data = tag_data
        w.global_light_condition = global_light_condition
        w.map_dropdown.setCurrentText(map_name)

        res = w.run_once_locked(params, sid)
        q.put(res)
    except Exception as e:
        q.put({"loss": 1e6, "min_ttc": None, "collision": 0, "error": str(e)})

class ViewInformationWindow(QDialog):
    run_finished = pyqtSignal(dict)  # result dict
    param_sampled = pyqtSignal(dict)  # params dict

    def __init__(self, excel_filename=None, scenario_row=None):
        super().__init__()

        self.CARLA_CALLED_FLAG = False

        self._sim_lock = threading.Lock()

        scenario_row += 1  # skip header row
        self.excel_filename = excel_filename
        self.scenario_row = scenario_row

        self.setWindowTitle('Scenario Parameter Configuration')
        self.setGeometry(300, 200, 500, 300)
        self.global_light_condition = None
        wb = load_workbook(excel_filename)
        ws = wb.active
        self.setStyleSheet("background-color: #e9f0fa;")   # Azure-like blue


        self.run_finished.connect(self._on_run_finished)
        self.param_sampled.connect(self._on_param_sampled)

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

        # Search Based Button
        opt_button = QPushButton("Run Optimization")
        opt_button.setFixedSize(150, 25)
        opt_button.clicked.connect(self.start_optimization)

        files_layout.addRow(opt_button)

        files_layout.addRow(QLabel("<b>Optimizer Param Bounds</b>"), QLabel(""))

        self.DEFAULT_PARAM_BOUNDS = {
            "ego_speed": (10.0, 50.0),
            "other_speed": (10.0, 50.0),
            "other_distance": (2.0, 20.0),
        }

        self.bounds_table = QTableWidget(0, 3)
        self.bounds_table.setHorizontalHeaderLabels(["param", "min", "max"])
        self.bounds_table.verticalHeader().setVisible(False)
        self.bounds_table.setEditTriggers(QTableWidget.AllEditTriggers)

        # default'ları bas
        for k, (mn, mx) in self.DEFAULT_PARAM_BOUNDS.items():
            r = self.bounds_table.rowCount()
            self.bounds_table.insertRow(r)

            item_k = QTableWidgetItem(str(k))
            item_k.setFlags(item_k.flags() & ~Qt.ItemIsEditable)  # param adı sabit kalsın
            self.bounds_table.setItem(r, 0, item_k)

            self.bounds_table.setItem(r, 1, QTableWidgetItem(str(mn)))
            self.bounds_table.setItem(r, 2, QTableWidgetItem(str(mx)))

        self.bounds_table.resizeColumnsToContents()
        files_layout.addRow(self.bounds_table)

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

        self.param_table = QTableWidget(0, 6)
        self.param_table.setHorizontalHeaderLabels(
            ["sid", "ego_speed", "other_speed", "other_distance", "timeout", "loss"]
        )
        files_layout.addRow(QLabel("<b>OSG Samples</b>"), QLabel(""))
        files_layout.addRow(self.param_table)

        # Add layouts to main
        main_layout.addLayout(tag_layout)
        main_layout.addLayout(files_layout)
        self.setLayout(main_layout)

    def _finish(self, res: dict) -> dict:
        self.run_finished.emit(res)
        return res

    def _on_run_finished(self, result: dict):
        self.show_results_button.setEnabled(True)

    def _on_param_sampled(self, row: dict):
        r = self.param_table.rowCount()
        self.param_table.insertRow(r)

        cols = ["sid", "ego_speed", "other_speed", "other_distance", "timeout", "loss"]
        for c, k in enumerate(cols):
            v = row.get(k, "")
            item = QTableWidgetItem(str(v))
            self.param_table.setItem(r, c, item)

        self.param_table.scrollToBottom()

    # ------------------- Simulation Control -------------------

    def _get_param_bounds_from_gui(self) -> dict:
        """
        bounds_table'dan param -> (min,max) okur ve validate eder.
        """
        bounds = {}
        for r in range(self.bounds_table.rowCount()):
            key = self.bounds_table.item(r, 0).text().strip()
            mn_txt = self.bounds_table.item(r, 1).text().strip()
            mx_txt = self.bounds_table.item(r, 2).text().strip()

            try:
                mn = float(mn_txt)
                mx = float(mx_txt)
            except ValueError:
                raise ValueError(f"Bounds numeric olmalı: {key} için min/max geçersiz.")

            if mn >= mx:
                raise ValueError(f"Bounds hatalı: {key} için min < max olmalı. (min={mn}, max={mx})")

            bounds[key] = (mn, mx)

        # en az şu üç param bekleniyor
        for req in ["ego_speed", "other_speed", "other_distance"]:
            if req not in bounds:
                raise ValueError(f"Bounds eksik: '{req}' bulunamadı.")

        return bounds


    def start_optimization(self):
        """
        self.show_results_button.setEnabled(False)
        t = threading.Thread(target=self._optimization_worker, daemon=True)
        t.start()"""
        self.show_results_button.setEnabled(False)

        # GUI bounds validate et
        try:
            _ = self._get_param_bounds_from_gui()
        except Exception as e:
            QMessageBox.warning(self, "Bounds Error", str(e))
            return

        t = threading.Thread(target=self._optimization_worker, daemon=True)
        t.start()

    def _optimization_worker(self):
        from Scenario_Configuration_Module.spso import SPSO
        import random

        import csv
        from pathlib import Path

        out_dir = Path(str(RESULTS_DIR)) / "osg_runs"
        out_dir.mkdir(parents=True, exist_ok=True)
        summary_path = out_dir / "summary.csv"
        samples_path = out_dir / "samples.csv"

        """PARAM_BOUNDS = {
            "ego_speed": (10.0, 50.0),
            "other_speed": (10.0, 50.0),
            "other_distance": (2.0, 20.0),
        }
        """
        # GUI'dan bounds al
        try:
            PARAM_BOUNDS = self._get_param_bounds_from_gui()
            bounds_json = json.dumps(PARAM_BOUNDS, ensure_ascii=False)

        except Exception as e:
            # worker thread içindeyiz -> GUI warning için signal/popup yerine print + fail safe
            print("[OSG][ERROR] Invalid bounds:", e)
            return

        keys = list(PARAM_BOUNDS.keys())
        lb = [PARAM_BOUNDS[k][0] for k in keys]
        ub = [PARAM_BOUNDS[k][1] for k in keys]

        FIELDNAMES = ["sid", "ego_speed", "other_speed", "other_distance", "timeout",
                      "loss", "min_ttc", "collision", "summary_log"]
        def append_summary(row: dict):
            file_exists = summary_path.exists()
            with open(summary_path, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=FIELDNAMES)
                if not file_exists:
                    w.writeheader()
                w.writerow({k: row.get(k, "") for k in FIELDNAMES})

        SAMPLE_FIELDS = [
            "sid",
            "ego_speed",
            "other_speed",
            "other_distance",
            "timeout",
            "min_ttc",
            "collision",
            "loss",
        ]

        def append_sample(row: dict):
            file_exists = samples_path.exists()
            with open(samples_path, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=SAMPLE_FIELDS)
                if not file_exists:
                    w.writeheader()
                w.writerow({k: row.get(k, "") for k in SAMPLE_FIELDS})

        def evaluate(x):

            sid = f"{time.time():.3f}-{random.randint(0, 9999)}"
            params = {k: float(v) for k, v in zip(keys, x)}
            params["timeout"] = 90.0  # co

            if params["other_speed"] > params["ego_speed"]:
                res = {"loss": 1e6, "min_ttc": None, "collision": 0, "summary_log": ""}
                row = {"sid": sid, **params, "loss": res["loss"]}
                self.param_sampled.emit(row)
                append_summary({"sid": sid, **params, **res})
                print(f"[OSG][SKIP] {sid} {params}")
                return (res["loss"],)

            try:
                res = self.run_once(params, sid=sid)

                row = {
                    "sid": sid,
                    **params,
                    "loss": res["loss"],
                }
                self.param_sampled.emit(row)

            except Exception as e:
                res = {"loss": 1e6, "min_ttc": None, "collision": 0}

            append_summary({
                "sid": sid,
                **params,
                "loss": res["loss"],
                "min_ttc": res.get("min_ttc", None),
                "collision": res.get("collision", 0),
            })

            append_sample({
                "sid": sid,
                **params,
                "loss": res.get("loss", None),
                "min_ttc": res.get("min_ttc", None),
                "collision": res.get("collision", 0),
            })


            print(f"[OSG] {sid} params={params} -> {res}")

            return (res["loss"],)

        spso = SPSO(
            func=evaluate,
            dim=len(keys),
            pop=3, #3
            max_iter= 350, # 350
            lb=lb,
            ub=ub,
            w=0.8,
            c1=0.5,
            c2=0.5,
            output_path=str(out_dir),
        )
        spso.run()

        print("[OSG] Done.")


    def execute_simulation(self):
        print("In: Execute Simulation")

        try:
            params = {
                "ego_speed": float(self.speed_input.text()),
                "other_speed": float(self.other_actor_speed_input.text()),
                "other_distance": float(self.other_actor_distance_input.text()),
                "timeout": float(self.timeout_input.text()),
            }
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values.")
            return

        if params["other_speed"] > params["ego_speed"]:
            QMessageBox.information(
                self,
                "Skipped",
                "NPC speed is greater than ego speed, so Autoware will not be launched and the run is skipped."
            )
            return

        result = self.run_once(params)

        self._on_run_finished(result)


    def run_once_locked(self, params, sid):
        if sid is None:
            sid = f"{time.time():.3f}"

        if float(params["other_speed"]) > float(params["ego_speed"]):
            print(f"[RUN][SKIP] other_speed({params['other_speed']}) > ego_speed({params['ego_speed']})")
            # Choose whatever "skip" loss you want:
            res = {"loss": 1e6, "min_ttc": None, "collision": 0}
            self.run_finished.emit(res)
            return res

            # 1) template update
        update_follow_leading_vehicle_template(
            timeout=str(params["timeout"]),
            distance=str(params["other_distance"]),
            speed=str(params["other_speed"])
        )

        # 2) weather/light
        weather_type = get_weather_type(self.tag_data)
        raw_light = self.global_light_condition[0].strip().lower()
        light = "Day" if raw_light in ["d", "day", "sunny", "light"] else "Night"
        update_weather_and_light(weather_type, light)

        # 3) start stack

        """if self.CARLA_CALLED_FLAG == False:
            launch_carla()
            self.CARLA_CALLED_FLAG = True
        """

        try:
            stop_carla()
        except Exception as e:
            print("[WARN] stop_carla failed:", e)

        time.sleep(5)
        launch_carla()
        time.sleep(5)

        try:
            launch_autoware(map_name=self.map_dropdown.currentText(),
                            speed_limit=int(round(params["ego_speed"])))

            time.sleep(7)

            # 4) run scenario runner
            results_dir = "/home/fauzia/Documents/scenario_runner/results/test"
            os.makedirs(results_dir, exist_ok=True)
            summary_log = os.path.join(results_dir, f"scenario_summary_{sid}.log")

            runner_thread = threading.Thread(target=run_scenario_runner, args=(summary_log,))
            runner_thread.start()

            #os.system('gnome-terminal -- bash -c "./run_set_goal.sh; exec bash"')
            subprocess.run(["bash", "-lc", "source ~/.bashrc && ./run_set_goal.sh"], check=False)

            runner_thread.join(timeout=90)
            if runner_thread.is_alive():
                print("[WATCHDOG] ScenarioRunner stuck skipping.")
                stop_autoware()
                return {"loss": 1e6, "min_ttc": None, "collision": 0}

            # runner done -> log hazır
            try:
                osg_log_dir = os.path.join(str(RESULTS_DIR), "osg_runs", "runner_logs")
                os.makedirs(osg_log_dir, exist_ok=True)
                dst = os.path.join(osg_log_dir, os.path.basename(summary_log))
                subprocess.run(["cp", summary_log, dst], check=False)
            except Exception as e:
                print("[WARN] log copy failed:", e)

        finally:
            # 5) stop autoware
            stop_autoware()

            time.sleep(5)

        time.sleep(4)

        # 6) metrics
        ok = run_metrics()

        time.sleep(2)

        if not ok:
            # sim/metrics fail => penalize
            return {"loss": 1e6, "min_ttc": None, "collision": 0}

        # 7) safety metrics
        safety = process_latest_raw_file()  # bunun output’una göre uyarlanacak
        if not isinstance(safety, dict):
            print("[OSG][WARN] process_latest_raw_file() returned None / non-dict. Penalizing run.")
            return {"loss": 1e6, "min_ttc": None, "collision": 0}

        min_ttc = safety.get("min_ttc", None)
        collision = int(safety.get("collision", 0))

        # collision varsa direkt en iyi/özel durum
        if collision:
            return {"loss": -50.0, "min_ttc": 0.0, "collision": 1}

        # min_ttc güvenli dönüşüm
        try:
            min_ttc_val = float(min_ttc) if min_ttc is not None else None
        except Exception:
            min_ttc_val = None

        # NaN/inf/negatif gibi durumları penalize et (sessiz hatayı engeller)
        if (min_ttc_val is None) or (not (min_ttc_val > 0.0)) or (min_ttc_val == float("inf")):
            return {"loss": 1e6, "min_ttc": None, "collision": 0, "error": "invalid_min_ttc"}

        loss = min_ttc_val
        res = {"loss": loss, "min_ttc": min_ttc_val, "collision": 0}

        try:
            osg_log_dir = os.path.join(str(RESULTS_DIR), "osg_runs", "runner_logs")
            os.makedirs(osg_log_dir, exist_ok=True)
            subprocess.run(["cp", summary_log, os.path.join(osg_log_dir, os.path.basename(summary_log))], check=False)
        except Exception as e:
            print("[WARN] log copy failed:", e)

        res['summary_log'] = summary_log
        self.run_finished.emit(res)

        return res

    """def run_once(self, params: dict, sid: str = None) -> dict:
        with self._sim_lock:
            return self.run_once_locked(params, sid)"""

    def   run_once(self, params: dict, sid: str = None) -> dict:
        if sid is None:
            sid = f"{time.time():.3f}"

        # Grab the state the child needs
        excel_filename = getattr(self, "excel_filename", None)  # if you have it stored; otherwise set it in __init__
        scenario_row = getattr(self, "scenario_row", None)      # same comment
        map_name = self.map_dropdown.currentText()
        tag_data = self.tag_data
        global_light_condition = self.global_light_condition

        q = mp.Queue()
        p = mp.Process(
            target=_run_once_child,
            args=(q, params, sid, excel_filename, scenario_row, map_name, tag_data, global_light_condition),
            daemon=True
        )
        p.start()
        p.join(timeout=180)  # 3 minutes

        if p.is_alive():
            print("[WATCHDOG] Run exceeded 3 minutes. Killing and restarting stack.")
            try:
                p.kill()
            except Exception:
                pass
            p.join(timeout=5)
            brute_cleanup()
            return {"loss": 1e6, "min_ttc": None, "collision": 0, "timeout": 1}

        try:
            return q.get_nowait()
        except pyqueue.Empty:
            brute_cleanup()
            return {"loss": 1e6, "min_ttc": None, "collision": 0, "error": "no_result"}



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


