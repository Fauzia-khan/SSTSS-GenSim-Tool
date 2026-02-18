import os
import subprocess
import glob
import shutil

# === Paths ===
base_folder = "/home/fauzia/Documents/scenario_runner/results/oldsimulation/ego50,lead40,distance10-40"
metric_script = "srunner/metrics/examples/velocity_and_distance_metric.py"
metrics_runner = "metrics_manager.py"
root_dir = "/home/fauzia/Documents/scenario_runner"
result_dir = os.path.join(root_dir, "results/test")

# Loop through each subfolder like dist_10, dist_15...
for folder_name in os.listdir(base_folder):
    folder_path = os.path.join(base_folder, folder_name)

    if not os.path.isdir(folder_path) or not folder_name.startswith("dist_"):
        continue

    # Find .log file in subfolder
    log_files = glob.glob(os.path.join(folder_path, "*.log"))
    if not log_files:
        print(f"❌ No .log file found in {folder_path}")
        continue

    log_file = log_files[0]  # Assuming only one .log file
    log_file_relative = os.path.relpath(log_file, start=root_dir)  # Convert to relative path

    print(f"🚀 Processing: {log_file_relative}")

    # Run the metrics command
    cmd = f'python {metrics_runner} --metric "{metric_script}" --log "{log_file_relative}"'
    subprocess.run(cmd, shell=True, cwd=root_dir)

    # Extract distance (e.g., 10 from dist_10)
    dist_value = folder_name.split("_")[1]

    # Get the most recent output CSV and PNG
    csv_files = sorted(glob.glob(os.path.join(result_dir, "*_metrics.csv")), key=os.path.getmtime, reverse=True)
    png_files = sorted(glob.glob(os.path.join(result_dir, "*_speed_distance*.png")), key=os.path.getmtime, reverse=True)

    if csv_files:
        new_csv = os.path.join(result_dir, f"{dist_value}.csv")
        shutil.move(csv_files[0], new_csv)
        print(f"✅ Saved: {new_csv}")

        # Rename PNG to match CSV base name
        if png_files:
            base_csv_name = os.path.splitext(os.path.basename(new_csv))[0]
            new_png = os.path.join(result_dir, f"{base_csv_name}.png")
            shutil.move(png_files[0], new_png)
            print(f"✅ Saved: {new_png}")
        else:
            print("⚠️ No PNG file found.")
    else:
        print("⚠️ No CSV file generated.")

