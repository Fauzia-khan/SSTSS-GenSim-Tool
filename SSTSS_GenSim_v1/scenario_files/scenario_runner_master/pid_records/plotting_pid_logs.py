import os
import sys
import subprocess
import time
import shutil

pid_dir = os.getcwd()  # burası pid_records
base_dir = os.path.abspath(os.path.join(pid_dir, ".."))  # scenario_runner-master

metric_script = os.path.join(pid_dir, "velocity_and_distance_metric.py")
log_file_rel = os.path.join("pid_records", "FollowLeadingVehicle_1.log")  # relative path
manager_path = os.path.join(base_dir, "metrics_manager.py")

# Yol kontrolleri
if not os.path.exists(os.path.join(base_dir, log_file_rel)):
    raise FileNotFoundError(f"Log bulunamadı: {os.path.join(base_dir, log_file_rel)}")
if not os.path.exists(manager_path):
    raise FileNotFoundError(f"{manager_path} bulunamadı")
if not os.path.exists(metric_script):
    raise FileNotFoundError(f"{metric_script} bulunamadı")

# Kısa isim (ör: e10)
main_folder = os.path.basename(base_dir)
parts = main_folder.split(",")
e_val = next((p.replace("ego", "") for p in parts if "ego" in p), "x")
short_prefix = f"e{e_val}"

print(f"▶ Çalıştırılıyor: {os.path.join(base_dir, log_file_rel)}")

# Önceki dosyalar
before_run = set(os.listdir(pid_dir))

# Komut
cmd = [
    sys.executable,
    manager_path,
    "--metric", metric_script,
    "--log", log_file_rel
]

# Çalıştırma (cwd=base_dir → srunner import çalışır)
result = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True)

# Komut çıktısı
print("— Komut:", " ".join(cmd))
print("— returncode:", result.returncode)
if result.stdout:
    print("— STDOUT —\n", result.stdout)
if result.stderr:
    print("— STDERR —\n", result.stderr)

# Sonuç kontrolü
if result.returncode != 0:
    print("❌ Metric script hata ile döndü.")
else:
    print("✅ Metric run başarılı, ego speed dosyaları işleniyor...")
    time.sleep(0.5)

    after_run = set(os.listdir(pid_dir))
    new_files = after_run - before_run

    if not new_files:
        print("⚠️ Yeni dosya üretilmedi.")
    else:
        for fname in new_files:
            if not fname.endswith((".csv", ".png", ".pdf")):
                continue
            if "_ego_speed" not in fname:
                continue  # sadece ego speed al

            src_path = os.path.join(pid_dir, fname)
            new_fname = f"{short_prefix}_ego_speed{os.path.splitext(fname)[1]}"
            dst_path = os.path.join(pid_dir, new_fname)
            shutil.move(src_path, dst_path)
            print(f"  → {fname}  ⇒  {new_fname}")
