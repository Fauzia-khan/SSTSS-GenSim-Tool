import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


"""

Columns: 'Time (s)', 'Ego Speed (km/h)', 'Lead Speed (km/h)',
       'Smoothed Lead Speed (km/h)', 'Distance Between (m)',
       'Ego Distance Covered (m)', 'Lead Vehicle Distance Covered (m)',
       'Ego X (m)', 'Ego Y (m)', 'Lead X (m)', 'Lead Y (m)'
"""

def calculate_ttc(ego_speed, lead_speed, distance_between):

    ttc = distance_between / (ego_speed - lead_speed + 1e-5)

    min_ttc = np.min(ttc)

    return ttc, min_ttc

def compute_ttc_from_df(df, rel_eps=0.05):
    ego_ms = df['Ego Speed (km/h)'].values / 3.6
    lead_ms = df['Lead Speed (km/h)'].values / 3.6
    dist = df['Distance Between (m)'].values

    v_rel = ego_ms - lead_ms
    valid = (dist > 0) & (v_rel > rel_eps)

    ttc = np.full_like(dist, np.nan, dtype=float)
    ttc[valid] = dist[valid] / v_rel[valid]

    return ttc


stats = {
    "total": 0,
    "no_motion": 0,
    "lane_violation": 0,
    "no_valid_ttc": 0,
    "kept": 0
}

min_ttc_list = []

CRITICAL_TTC = 1.0

found_debug = False


for file in os.listdir('results'):

    stats["total"] += 1

    df = pd.read_csv('results/' + file)

    ## Drop first 40 rows
    df = df.iloc[40:].reset_index(drop=True)

    ego_speed = df['Ego Speed (km/h)'].values
    lead_speed = df['Lead Speed (km/h)'].values

    ego_speed = df['Ego Speed (km/h)'].values
    lead_speed = df['Lead Speed (km/h)'].values

    pose_ego_x = df['Ego X (m)'].values
    pose_ego_y = df['Ego Y (m)'].values

    pose_lead_x = df['Lead X (m)'].values
    pose_lead_y = df['Lead Y (m)'].values

    SPEED_EPS = 0.5

    # Drop the scenario if there is no movement.
    if (np.max(ego_speed) - np.min(ego_speed) < SPEED_EPS and np.max(lead_speed) - np.min(lead_speed) < SPEED_EPS):
        stats["no_motion"] += 1
        continue

    # if there is a movement outside the y range of 130-135, discard the scenario.
    lane_upper_bound = 135
    lane_lower_bound = 130

    lane_violation = np.any((pose_lead_y)> lane_upper_bound) or np.any((pose_lead_y) < lane_lower_bound)
    if lane_violation:
        stats["lane_violation"] += 1
        #continue

    ##  Terminate the scenario
    df = df.iloc[:750].reset_index(drop=True)

    # PREPROCESSING DONE #############

    cols = ['Distance Between (m)', 'Ego Speed (km/h)', 'Lead Speed (km/h)']

    df_ttc = (
        df[['Time (s)',
            'Distance Between (m)',
            'Ego Speed (km/h)',
            'Lead Speed (km/h)',
            'Ego X (m)', 'Ego Y (m)',
            'Lead X (m)', 'Lead Y (m)']]
        .apply(pd.to_numeric, errors='coerce')
        .dropna()
        .iloc[:750]
        .reset_index(drop=True)
    )

    ttc = compute_ttc_from_df(df_ttc)
    min_ttc = np.nanmin(ttc)

    distance_between = df_ttc['Distance Between (m)'].values
    ego_speed = df_ttc['Ego Speed (km/h)'].values
    lead_speed = df_ttc['Lead Speed (km/h)'].values


    if np.isnan(min_ttc) or np.isinf(min_ttc):
        stats["no_valid_ttc"] += 1
        continue

    stats["kept"] += 1

    min_ttc_list.append(min_ttc)

    if (min_ttc < CRITICAL_TTC) and  (not found_debug):
        debug_scenario = file
        debug_df = df_ttc.copy()  # <-- aynı temiz veri
        debug_min_ttc = float(min_ttc)
        found_debug = True


print("Dataset size len(os listdir) ", len(os.listdir('results')))
print(stats)

t = debug_df['Time (s)'].values

ego_ms = debug_df['Ego Speed (km/h)'].values / 3.6
lead_ms = debug_df['Lead Speed (km/h)'].values / 3.6
distance = debug_df['Distance Between (m)'].values

v_rel = ego_ms - lead_ms
valid = (distance > 0) & (v_rel > 0.05)

ttc = np.full_like(distance, np.nan, dtype=float)
ttc[valid] = distance[valid] / v_rel[valid]
TTC_MAX = 7.5  # from the article

min_ttc_arr = np.array(min_ttc_list)

# Clip Meaningless TTC values

min_ttc_arr = min_ttc_arr[
    (min_ttc_arr > 0) &
    (min_ttc_arr <= TTC_MAX)
]
fig, ax = plt.subplots(figsize=(7,4))

# Risk Bands: Shadow Zones
max_x = np.nanmax(min_ttc_arr)
max_x = float(max_x) if np.isfinite(max_x) else 10.0

bands = [
    (0.0, 2.0, "red",    0.5, "Strong risk (0–2s)"),
    (2.0, 4.0, "orange", 0.2, "Medium risk (2–4s)"),
    (4.0, 6.0, "yellow",   0.2, "Low risk (4–6s)"),
    (6.0, max_x, "green", 0.2, "Conservative (6s+)"),
]

for x0, x1, color, a, label in bands:
    if x1 <= x0:
        continue
    ax.axvspan(x0, x1, color=color, alpha=a, lw=0, label=label)

for x in [1, 2, 3, 4, 5, 6]:
    ax.axvline(x, alpha=0.4, linewidth=1)

# Histogram
ax.hist(min_ttc_arr, bins=30, edgecolor="white", linewidth=0.5)

ax.set_xlabel("min TTC (s)")
ax.set_ylabel("Count")
ax.set_title("Histogram of min TTC")
ax.grid(True, alpha=0.3)

handles, labels = ax.get_legend_handles_labels()
seen = set()
uniq_h, uniq_l = [], []
for h, l in zip(handles, labels):
    if l not in seen:
        uniq_h.append(h); uniq_l.append(l); seen.add(l)
ax.legend(uniq_h, uniq_l, loc="upper right", framealpha=0.9)

fig.savefig("safety_histogram_min_ttc.png", dpi=300, bbox_inches="tight")
plt.show()
