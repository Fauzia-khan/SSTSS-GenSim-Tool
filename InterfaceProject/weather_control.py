import os
import re


def adjust_weather_condition(light_condition,
                             xml_path="/home/laima/Documents/scenario_runner-master/srunner/examples/FollowLeadingVehicle.xml"):
    """
    Updates the weather settings in the scenario XML based on the light condition.

    Args:
        light_condition (str): "Day" or "Night"
        xml_path (str): Path to the scenario XML file.
    """

    if light_condition.lower() == "day":
        sun_altitude_angle = 90
    else:
        sun_altitude_angle = -10

    if not os.path.exists(xml_path):
        print(f"[ERROR] XML path does not exist: {xml_path}")
        return

    # Read the XML file
    with open(xml_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if "<weather" in line:
            # Replace cloudiness
            line = re.sub(r'cloudiness="[^"]+"', 'cloudiness="0"', line)
            # Replace precipitation
            line = re.sub(r'precipitation="[^"]+"', 'precipitation="0"', line)
            # Replace daylight
            line = re.sub(r'sun_altitude_angle="[^"]+"',
                          f'sun_altitude_angle="{sun_altitude_angle}"',
                          line)

            print(f"[INFO] Light condition set to {light_condition}, sun altitude {sun_altitude_angle}")

        new_lines.append(line)

    # Write the updated XML
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("[✓] Weather conditions updated successfully!")
