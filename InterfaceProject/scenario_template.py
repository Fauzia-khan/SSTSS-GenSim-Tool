import os

def update_follow_leading_vehicle_template(timeout, distance, speed,
                                           template_path="scenario_files/python_files/template_follow_leading_vehicle.py",
                                           output_path="/home/laima/Documents/scenario_runner-master/srunner/scenarios/follow_leading_vehicle.py"):
    """
    Update the FollowLeadingVehicle scenario template with new parameters.

    Args:
        timeout (str): The timeout value.
        distance (str): Distance of the other vehicle.
        speed (str): Speed of the other vehicle.
        template_path (str): Path to the template file.
        output_path (str): Path where updated scenario is saved.
    """

    # 1. Load template
    with open(template_path, 'r') as f:
        lines = f.readlines()

    # 2. Replace specific lines (line indexes 7, 8, 9)
    lines[7] = f'timeout = {timeout}\n'
    lines[8] = f'other_vehicle_distance = {distance}\n'
    lines[9] = f'other_vehicle_speed = {speed}\n'

    # 3. Save updated scenario
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"[✓] Scenario template updated at: {output_path}")
