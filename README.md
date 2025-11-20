



# SSTSS-GenSim Tool
SSSTSS-GenSim is a modular end-to-end pipeline for scenario-based safety testing of Automated Driving Systems (ADS).
It streamlines the complete workflow from scenario selection, scenario implementation, scenario configuration, simulation, data collection, safety-metric evalaution, and visualization and simulation summary report generation.

---
## Features

- **Scenario Catalog Selection** – Select between catalogs (US, Singapore, Europe, Other). By default, a Singapore catalog is preloaded.
- **Custom Scenario catalog** –  Add your own scenario catalogs directly within the tool

- **Scenario Selection**:
  1. View all available scenarios.
  2. Select Operational Design Domains (ODDs).
  3. Filter scenarios based on ODD selection.
  4. Assign scenarios to scenario groups.
  5. Prioritize scenario groups for testing using the US or EU accident dataset.
  6. Filter scenarios by simulator compatibility (Carla, Gazebo, LGSVL).
  7. Assign a priority to each selected sceanrio within each scenario group using the US or EU dataset. 
- **Excel-based Storage** – Reads and updates scenario datasets stored in `.xlsx` format.
  
- **Modular Design** – Separate scripts for each functional component.

---

## GUI for the Scenario Selection Module

<p align="center">
  <img src="InterfaceProject/images/Main_WIndow.png" alt="Main Window" width="600">
</p>

## Workflow

1. **Launch the Tool** – Run the main Python script.
2. **Select Catalog** – Choose the dataset region (US, Singapore, Europe, Other).
3. **View / Add Scenarios** – Add new scenario or browse existing ones.
4. **Select ODD** – Narrow down scenarios based on operational design domain, i.e, (Dynamic, Environmental, Scenery ).
5. **Assign & Prioritize** – Prioritize the sceanrio groups based on the selected accident dataset.
6. **Filter by Simulator** – Keep only scenarios compatible with a selected simulator.
7. **Assign Prioritize Scenario** – Assign a priority to each sceanrio within each sceanrio group using the selected accident dataset.
8. **Final list of Test Scenarios** – List of test scenarios for testing or simulation.






## Installation

### 1. Clone the Repository
```bash

git clone https://github.com/<your-username>/SSTSS-GenSim.git
cd SSTSS-GenSim
```



### 2. Install Python Dependencies

Install required libraries (Python 3.8+ recommended):

```bash
pip install -r requirements.txt
```

### 3. Install and Configure CARLA (for Simulation Execution)

Download CARLA 0.9.13
https://carla.org/

Extract CARLA to your preferred location
Add CARLA PythonAPI to PYTHONPATH:
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/CARLA_0.9.13/PythonAPI/carla/dist/carla-0.9.13-py3.8-linux-x86_64.egg
export PYTHONPATH=$PYTHONPATH:/path/to/CARLA_0.9.13/PythonAPI/carla

```
(Replace paths with your system locations.)

### 4. ScenarioRunner Installation

Download ScenarioRunner (compatible with CARLA 0.9.13):
```bash
git clone https://github.com/carla-simulator/scenario_runner.git

```
Set the root path inside config.py:
```bash
SCENARIO_RUNNER_ROOT = "/home/user/scenario_runner"

```
5. Configure SSTSS-GenSim Tool Paths

Edit config.py inside the tool:
```bash
TOOL_ROOT = "/path/to/SSTSS_GenSim_Modules"
CARLA_ROOT = "/path/to/CARLA_0.9.13"
SCENARIO_RUNNER_ROOT = "/path/to/scenario_runner"
RESULTS_DIR = "/path/to/scenario_runner/results/test"

```
6. Launch the Tool

Run the main GUI:
```bash
python main.py

```
----
**Authors:**  
Fauzia Khan, Hina Anwar, Deitmar Pfahl


This tool extends the **SSTSS** (Simulation-based Safety Testing Scenario Selection) process by enabling users to run selected scenarios in simulation and evaluate them using standardized safety metrics.


---

