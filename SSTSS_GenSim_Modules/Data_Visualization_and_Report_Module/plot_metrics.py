import pandas as pd
import matplotlib.pyplot as plt
import os

import matplotlib.pyplot as plt

# ==========================
#  UNIVERSAL FONT SETTINGS
# ==========================
TITLE_FONT = {"fontsize": 20, "fontfamily": "Times New Roman"}
AXIS_FONT = {"fontsize": 16, "fontfamily": "Times New Roman"}
TICK_FONT = {"size": 14, "family": "Times New Roman"}
LEGEND_FONT = {"size": 16, "family": "Times New Roman"}
LINE_WIDTH = 2


def plot_speed_and_distance(df, output_path):
    fig, ax1 = plt.subplots(figsize=(12, 5))

    time = df["Time (s)"]

    # Select correct distance column
    if "Distance Between (m)" in df.columns:
        dist_col = "Distance Between (m)"
    elif "Distance (m)" in df.columns:
        dist_col = "Distance (m)"
    else:
        dist_col = None

    # --- Speed Plots ---
    ax1.plot(time, df["Ego Speed (km/h)"], label="Ego Speed", linewidth=LINE_WIDTH)
    ax1.plot(time, df["Lead Speed (km/h)"], label="Lead Speed", linewidth=LINE_WIDTH)

    ax1.set_xlabel("Time (s)", **AXIS_FONT)
    ax1.set_ylabel("Speed (km/h)", **AXIS_FONT)
    ax1.grid(True)
    # --- Right Axis: Distance + RSS ---
    ax1b = ax1.twinx()

    if dist_col:
        ax1b.plot(time, df[dist_col], color="red", label="Actual Distance", linewidth=LINE_WIDTH)

    ax1b.plot(
        time,
        df["RSS Distance (m)"],
        linestyle="--",
        color="red",
        label="RSS Safe Distance",
        linewidth=LINE_WIDTH
    )

    ax1b.set_ylabel("Distance (m)", **AXIS_FONT)

    # --- Title ---
    fig.suptitle(
        "Speed of Vehicles, RSS, and Actual Distance Between Both Vehicles",
        **TITLE_FONT
    )

    # --- Legend styling ---
    ax1.legend(loc="upper left", prop=LEGEND_FONT)
    ax1b.legend(loc="upper right", prop=LEGEND_FONT)

    # --- Tick labels ---
    ax1.tick_params(axis='both', labelsize=TICK_FONT["size"])
    ax1b.tick_params(axis='both', labelsize=TICK_FONT["size"])

    for label in ax1.get_xticklabels() + ax1.get_yticklabels():
        label.set_fontname("Times New Roman")
    for label in ax1b.get_yticklabels():
        label.set_fontname("Times New Roman")

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_jerk(df, output_path):
    fig, ax = plt.subplots(figsize=(12, 5))

    time = df["Time (s)"]
    jerk_col = "Jerk (m/s³) (1 Hz)"

    jerk_df = df[df[jerk_col].notna()]

    ax.plot(
        jerk_df["Time (s)"],
        jerk_df[jerk_col],
        marker="o",
        markersize=6,
        linewidth=LINE_WIDTH,
        label="Ego Vehicle Jerk"
    )

    # Axis labels
    ax.set_xlabel("Time (s)", **AXIS_FONT)
    ax.set_ylabel("Jerk (m/s³)", **AXIS_FONT)

    # Title
    ax.set_title("Ego Vehicle Jerk Over Time", **TITLE_FONT)

    ax.grid(True)

    # Tick styling
    ax.tick_params(axis='both', labelsize=TICK_FONT["size"])
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname("Times New Roman")

    # Legend
    ax.legend(prop=LEGEND_FONT)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path
