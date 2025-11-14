import os
from config import SCENARIO_RUNNER_ROOT, SCENARIO_TEMPLATE_PATH


def update_follow_leading_vehicle_template(timeout, distance, speed,
                                           template_path=SCENARIO_TEMPLATE_PATH,
                                           output_path=None):
    """
    Update the FollowLeadingVehicle scenario template with new parameters.
    """

    # If output path is not provided, build it from config
    if output_path is None:
        output_path = os.path.join(
            SCENARIO_RUNNER_ROOT,
            "srunner",
            "scenarios",
            "follow_leading_vehicle.py"
        )

    # 1. Load template
    with open(template_path, 'r') as f:
        lines = f.readlines()

    # 2. Replace specific lines
    lines[7] = f'timeout = {timeout}\n'
    lines[8] = f'other_vehicle_distance = {distance}\n'
    lines[9] = f'other_vehicle_speed = {speed}\n'

    # 3. Save updated scenario
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"[✓] Scenario template updated at: {output_path}")
