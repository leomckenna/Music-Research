import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define file paths
ssd_path = "/Volumes/Extreme SSD/"
control_file = os.path.join(ssd_path, "audio_metrics.csv")
bebop_file = os.path.join(ssd_path, "audio_metrics_non_control.csv")

# Verify files exist before reading
if not os.path.exists(control_file):
    raise FileNotFoundError(f"Control file not found: {control_file}")
if not os.path.exists(bebop_file):
    raise FileNotFoundError(f"Bebop file not found: {bebop_file}")

# Load CSV files
control_df = pd.read_csv(control_file)
bebop_df = pd.read_csv(bebop_file)

# Add a label column to differentiate datasets
control_df["Dataset"] = "Control"
bebop_df["Dataset"] = "Bebop"

# Find the minimum dataset size
min_size = min(len(control_df), len(bebop_df))

# Randomly sample from the larger dataset to match the smaller one
control_sample = control_df.sample(n=min_size, random_state=42)
bebop_sample = bebop_df.sample(n=min_size, random_state=42)

# Combine the balanced datasets
balanced_df = pd.concat([control_sample, bebop_sample])

# List of numerical columns to compare
numerical_columns = [
    "Tempo (BPM)", "Clock Density (Onsets/Sec)", "Beat Density (Beats/Sec)",
    "Onsets per Beat", "Pitch SD", "Pitch Mean", "Pitch Median",
    "Pitch Entropy", "Intervallic Variability"
]

# Convert columns to numeric
for col in numerical_columns:
    balanced_df[col] = pd.to_numeric(balanced_df[col], errors="coerce")

# Plot KDE distributions for balanced dataset
for col in numerical_columns:
    plt.figure(figsize=(6, 4))
    sns.kdeplot(data=balanced_df, x=col, hue="Dataset", fill=True, alpha=0.5, common_norm=False)
    plt.title(f"Balanced Distribution of {col}")
    plt.xlabel(col)
    plt.ylabel("Density")
    plt.legend(title="Dataset")
    plt.show()
