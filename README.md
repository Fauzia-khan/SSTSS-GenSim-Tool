



# SafeBound Tool
SafeBound is a modular end-to-end pipeline for scenario-based safety testing of Automated Driving Systems (ADS).
It streamlines the entire workflow, from scenario selection and implementation to configuration, simulation, data collection, safety evaluation, and the generation of visualization and simulation summary reports.

---

## GUI for the Scenario Selection Module

<p align="center">
  <img src="SSTSS_GenSim_v1/scenario_selection.png" alt="Main Window" width="600">  
  
</p>

## Workflow 
 **Launch the Tool** – Run the main Python script.
 
**1. Scenario Selection Module:** – Prioritizes and selects the test sceanrio based on the SSTSS process. It takes four inputs:

i. **Select Catalog** – Choose the dataset region (US, Singapore, Other). 
         
ii. **Select ODD** – Narrow down scenarios based on operational design domain, i.e, (Dynamic, Environmental, Scenery ).

iii. **Select Dataset** – Choose the dataset US, Europe, or Singapore.

iv. **Select Simulator** – Choose the simulator.(Currently, you can select CARLA)

_Output._ --> Final list of Test Scenarios.xlsx

**2. **Scenario Implementation Module:** Reads the scenario group tag of the selected scenario, maps it to an appropriate template provided by the ScenarioRunner framework, and converts it into an executable format compliant with the ASAM OpenSCENARIO standard. <br>
_Output_ --> (<scenarioname.py>)

**3. Scenario Configuration Module:** Configures the simulation environment and applies the selected input parameters in <scenario_name.py>. <br>
_Output_ --> (<scenarioname.xml>) 

**4. ** Simulator and ADS Integration Module:** Sets up the simulation environment, including CARLA, Scenario Runner, and Autoware Mini. <br>
_Output_ --> (simulation setup is ready)

**5. Scenario Execution Module:** Runs the configured scenario in CARLA using the integrated simulation setup. <br>
_Output_ --> (<scenarioname.log>)  and _Output_ --> (<scenarioname.json>)

**6. ** Data Collection Module:** Captures all relevant simulation outputs, including timestamps, positions, and speeds of all actors involved.<br>
_Output_ --> (<scenarioname_data.csv>)

**7. ** Safety Metrics Evaluation Module:** Calculates the safety metrics for evaluating ADS performance.  <br>
_Output_ --> (<scenarioname_metrices.py>)

**8. Data Visualization and Report Module:** Generates plots and summary reports based on the collected data.<br>
_Output_ --> (<scenario_name_metrice.png>)  and _Output_ --> (<scenarioname_summary.txt>)


## Requirements
The SSTSS-GenSim Tool requires a Linux-based environment with ROS and a supported simulator. The recommended Supported Operating System is Ubuntu 20.04 LTS (recommended).
Windows is not supported because key components (Autoware_mini) do not run natively on Windows.


## Installation
### 1. Install and Configure CARLA (for Simulation Execution)

Download CARLA 0.9.13
https://carla.org/

Extract CARLA to your preferred location
Add CARLA PythonAPI to PYTHONPATH:
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/CARLA_0.9.13/PythonAPI/carla/dist/carla-0.9.13-py3.8-linux-x86_64.egg
export PYTHONPATH=$PYTHONPATH:/path/to/CARLA_0.9.13/PythonAPI/carla

```
(Replace paths with your system locations.)
### 2. Autoware_mini Installation 
Clone the repository into your ROS workspace:
```bash
cd ~/catkin_ws/src
git clone https://github.com/UT-ADL/autoware_mini.git
```
Install dependencies:
```bash
rosdep install --from-paths . --ignore-src -r -y
```
Build:
```bash
bash
cd ~/catkin_ws
catkin_make
```
Source the workspace:
```bash
bash
source ~/catkin_ws/devel/setup.bash
```
For complete instructions, refer to:
https://github.com/UT-ADL/autoware_mini

### 3. ScenarioRunner Installation

Download ScenarioRunner (compatible with CARLA 0.9.13):
```bash
git clone https://github.com/carla-simulator/scenario_runner.git

```
Set the root path inside config.py:
```bash
SCENARIO_RUNNER_ROOT = "/home/user/scenario_runner"

```
5. Configure SafeBound Tool Paths

Edit config.py inside the tool:
```bash
TOOL_ROOT = "/path/to/SSTSS_GenSim_Modules"
CARLA_ROOT = "/path/to/CARLA_0.9.13"
SCENARIO_RUNNER_ROOT = "/path/to/scenario_runner"
RESULTS_DIR = "os.path.join(TOOL_ROOT, "Data_Collection_Module", "raw_data"

```



### 4. SSTSS-GenSim-Tool Installation
### 1. Clone the Repository
```bash

# 1. Clone the repository
git clone https://github.com/<your-username>/SSTSS-GenSim-Tool.git

# 2. Navigate into the project directory
cd SSTSS-GenSim-Tool/SSTSS_GenSim_v1

# 3. Create a Python virtual environment (first time only)
python -m venv venv

# 4. Activate the virtual environment
# Linux
source venv/bin/activate

# 5. Install Python dependencies (Python 3.8+ recommended)
pip install -r requirements.txt

# 6. Run the main tool
python main.py
```


## Demo Video
[Click here to watch the tool demo video](https://drive.google.com/file/d/1XPXzFDNAYXQR10g7PQslKZQKBmrmNhln/view?usp=sharing)

## Authors
Fauzia Khan, Ali Ihsan GÜllÜ, Hina Anwar, Deitmar Pfahl, "SSTSS-GenSim: A Modular Tool Chain for End-to-End Safety Evaluation of Automated Driving Systems".

---
DS.
