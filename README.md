# SSTSS-GenSim Tool


**SSTSS** -- Simulation-based Safety Testing Scenario Selection process is a scenario selection tool for prioritizing and selecting test scenarios for simulation-based safety testing of ADS.

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

## Screenshot

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

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/[[your-username]]/sstss-tool.git
cd sstss-tool

### 2. Run the Application**
```bash
python main_window.py
