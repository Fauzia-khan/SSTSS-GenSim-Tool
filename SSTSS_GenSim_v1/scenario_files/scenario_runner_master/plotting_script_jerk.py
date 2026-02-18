import os
import subprocess
import shutil
import time

# Set base directory to current working directory
base_dir = os.getcwd()

# Folder containing the scenario log files
logs_root = os.path.join(base_dir, "results/withjerk_Scenario_followleadvehicle/Simulation_logfiles/ego10,lead10,distance10-40")

# Metric script path (relative to base_dir)
metric_script = "srunner/metrics/examples/velocity_and_distance_metric.py"

# Output folder where metrics_manager.py saves result files
output_dir = os.path.join(base_dir, "results", "test")

# Extract e10 and l10 from main folder
main_folder = os.path.basename(logs_root)
parts = main_folder.split(",")

e_val = next((p.replace("ego", "") for p in parts if "ego" in p), "x")
l_val = next((p.replace("lead", "") for p in parts if "lead" in p), "x")

# Loop over each subfolder (dist_10, dist_15, etc.)
for folder in sorted(os.listdir(logs_root)):
    subfolder_path = os.path.join(logs_root, folder)

    if os.path.isdir(subfolder_path) and folder.startswith("dist_"):
        # Relative path to the log file (important for metrics_manager.py)
        log_file = os.path.relpath(os.path.join(subfolder_path, "FollowLeadingVehicle_1.log"), base_dir)

        if os.path.exists(log_file):
            print(f"\n▶ Processing: {log_file}")

            # Get list of files before the metric runs
            before_run = set(os.listdir(output_dir))

            # Run the metrics_manager command
            command = f'python metrics_manager.py --metric "{metric_script}" --log "{log_file}"'
            result = subprocess.run(command, cwd=base_dir, shell=True)

            if result.returncode == 0:
                print("✅ Metric run successful, renaming and moving output files...")

                # Short delay to allow filesystem to update
                time.sleep(0.5)

                # List of new files created in output_dir
                after_run = set(os.listdir(output_dir))
                new_files = after_run - before_run

                # Build short name prefix: e10_l10_dist10
                dist_val = folder.replace("dist_", "")
                short_prefix = f"e{e_val}_l{l_val}_dist{dist_val}"

                # Rename and move only .csv/.png/.pdf files
                for fname in new_files:
                    if fname.endswith((".csv", ".png", ".pdf")):
                        src_path = os.path.join(output_dir, fname)

                        # Determine new filename
                        if "_speed_distance" in fname:
                            new_fname = f"{short_prefix}.png"
                        elif "_jerk_plot" in fname or "_accel_jerk" in fname:
                            ext = os.path.splitext(fname)[1]
                            new_fname = f"{short_prefix}_jerk{ext}"
                        elif "_metrics" in fname:
                            new_fname = f"{short_prefix}.csv"
                        else:
                            # Skip or handle other types
                            continue

                        dst_path = os.path.join(subfolder_path, new_fname)
                        shutil.move(src_path, dst_path)
                        print(f"  → Renamed and moved to {new_fname}")
            else:
                print("❌ Metric script failed.")
        else:
            print(f"⚠️ Log file not found in {folder}, skipping.")
