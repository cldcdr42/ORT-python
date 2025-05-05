import os
import glob
import time
import pandas as pd
import matplotlib.pyplot as plt

import argparse

# --- Parsing flags ---
parser = argparse.ArgumentParser()

parser.add_argument("-n", type=int, help="Which experiment to plot, from 0 (latest), 1 (second latest)...", default=0)
#parser.add_argument("--verbose", type=bool, help="Enable verbose mode")

args = parser.parse_args()
# ---------------------

# --- Configuration ---
base_dir = './17_meas'
specified_folder = None  # Replace with a timestamp string like "20240505_143210" to choose a specific one
#specified_folder = "20250505_121851"
# ----------------------

# Get all folders matching timestamp format
all_folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f)) and len(f) == 15]

# Use latest folder or the one specified
if specified_folder and specified_folder in all_folders:
    selected_folder = specified_folder
elif all_folders:
    selected_folder = sorted(all_folders, reverse=True)[args.n]
else:
    raise FileNotFoundError("No valid folders found in '17_meas'.")

folder_path = os.path.join(base_dir, selected_folder)
print(f"Using data from folder: {selected_folder}")

print("Files found in folder:", os.listdir(folder_path))

# File paths
emg_file = os.path.join(folder_path, 'EMG.csv')
mcu_file = os.path.join(folder_path, 'mcu.csv')


# Check for required files
if not all(os.path.exists(f) for f in [emg_file, mcu_file]):
    raise FileNotFoundError(f"Missing one or more required CSV files in {folder_path}")

# Load data
emg_data = pd.read_csv(emg_file)
mcu_data = pd.read_csv(mcu_file)

# Plot data
fig, axs = plt.subplots(4, 1, figsize=(12, 10))
fig.suptitle(f'Experiment Data from {selected_folder}', fontsize=14, y=0.98)

axs[0].plot(emg_data['Timestamp'], emg_data.iloc[:, 1], color='blue')
axs[0].set_ylabel(emg_data.columns[1])
axs[0].set_xlabel('Time [sec]')
axs[0].grid(True)

axs[1].plot(mcu_data['Timestamp'], mcu_data['Angle [deg]'], color='green')
axs[1].set_ylabel(mcu_data.columns[1])
axs[1].set_xlabel('Time [sec]')
axs[1].grid(True)

axs[2].plot(mcu_data['Timestamp'], mcu_data['Velocity [deg/s]'], color='red')
axs[2].set_ylabel(mcu_data.columns[2])
axs[2].set_xlabel('Time [sec]')
axs[2].grid(True)

axs[3].plot(mcu_data['Timestamp'], mcu_data['Target [norm]'], color='orange')
axs[3].set_ylabel(mcu_data.columns[3])
axs[3].set_xlabel('Time [sec]')
axs[3].grid(True)

plt.tight_layout()
plt.show()
