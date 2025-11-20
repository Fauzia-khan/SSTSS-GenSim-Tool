import os
import re
from config import SCENARIO_XML


# ------------------------------------------------------------
# 1) Extract weather type from tag_data
# ------------------------------------------------------------

def get_weather_type(tag_data):
    """
    Reads weather columns from tag_data and returns:
    'Dry', 'Rainy', 'Foggy', or default 'Dry'
    """
    if "Weather" not in tag_data:
        return "Dry"

    weather_tags = tag_data["Weather"]

    # These names must match Excel column labels exactly
    if "Rainy" in weather_tags:
        return "Rainy"
    if "Snowy" in weather_tags:
        return "Snowy"
    if "Foggy" in weather_tags:
        return "Foggy"

    return "Dry"   # default


# ------------------------------------------------------------
# 2) XML edit function for weather + light
# ------------------------------------------------------------

def update_weather_and_light(weather_type, light_condition, xml_path=SCENARIO_XML):
    """
    Update both weather and light in the scenario XML file.
    """

    print("\n================ WEATHER DEBUG ================")
    print("[DEBUG] update_weather_and_light() CALLED")
    print("[DEBUG]   weather_type      =", weather_type)
    print("[DEBUG]   light_condition   =", light_condition)
    print("[DEBUG]   xml_path          =", xml_path)
    print("================================================")

    # Light mapping
    if light_condition.lower() == "day":
        sun_altitude_angle = 90
    else:
        sun_altitude_angle = -10

    # Weather mapping
    if weather_type == "Dry":
        cloud = "0"
        precipitation = "0"
        fog = "0"
    elif weather_type == "Rainy":
        cloud = "80"
        precipitation = "60"
        fog = "0"
    elif weather_type == "Foggy":
        cloud = "20"
        precipitation = "0"
        fog = "70"
    elif weather_type == "Snowy":
        cloud = "60"
        precipitation = "40"
        fog = "30"
    else:
        cloud = precipitation = fog = "0"

    if not os.path.exists(xml_path):
        print(f"[ERROR] XML path does not exist: {xml_path}")
        print("================================================\n")
        return

    # -------- READ XML --------
    print("[DEBUG] Reading XML...")
    with open(xml_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if "<weather" in line:
            print("\n[DEBUG] Found <weather> line:")
            print(" BEFORE:", line.strip())

            # Replace cloudiness
            line = re.sub(r'cloudiness="[^"]+"', f'cloudiness="{cloud}"', line)
            # Replace precipitation
            line = re.sub(r'precipitation="[^"]+"', f'precipitation="{precipitation}"', line)
            # Replace fog
            line = re.sub(r'precipitation_deposits="[^"]+"', f'precipitation_deposits="{fog}"', line)
            # Replace sun
            line = re.sub(
                r'sun_altitude_angle="[^"]+"',
                f'sun_altitude_angle="{sun_altitude_angle}"',
                line
            )

            print(" AFTER :", line.strip(), "\n")

        new_lines.append(line)

    # -------- WRITE XML --------
    print("[DEBUG] Writing updated XML values:")
    print("  cloudiness           =", cloud)
    print("  precipitation        =", precipitation)
    print("  precipitation_deposits =", fog)
    print("  sun_altitude_angle   =", sun_altitude_angle)
    print("------------------------------------------------")
    print("[DEBUG] Saving changes to:", xml_path)

    with open(xml_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print("[✓] Weather + Light updated successfully!")
    print("================================================\n")
