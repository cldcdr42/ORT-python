import os
import glob
import time
import pandas as pd
import matplotlib.pyplot as plt

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
    selected_folder = sorted(all_folders, reverse=True)[0]
else:
    raise FileNotFoundError("No valid folders found in '17_meas'.")

folder_path = os.path.join(base_dir, selected_folder)
print(f"Using data from folder: {selected_folder}")

print("Files found in folder:", os.listdir(folder_path))

# File paths
eeg_file = os.path.join(folder_path, 'EEG.csv')
angle_file = os.path.join(folder_path, 'Angle.csv')
velocity_file = os.path.join(folder_path, 'Velocity.csv')

# Check for required files
if not all(os.path.exists(f) for f in [eeg_file, angle_file, velocity_file]):
    raise FileNotFoundError(f"Missing one or more required CSV files in {folder_path}")

# Load data
eeg_data = pd.read_csv(eeg_file)
angle_data = pd.read_csv(angle_file)
velocit_data = pd.read_csv(velocity_file)

# Plot data
fig, axs = plt.subplots(3, 1, figsize=(12, 10))
fig.suptitle(f'Experiment Data from {selected_folder}', fontsize=14, y=0.98)

axs[0].plot(eeg_data['Timestamp'], eeg_data.iloc[:, 1], color='blue')
axs[0].set_ylabel(eeg_data.columns[1])
axs[0].set_xlabel('Time [sec]')
axs[0].grid(True)

axs[1].plot(angle_data['Timestamp'], angle_data.iloc[:, 1], color='green')
axs[1].set_ylabel(angle_data.columns[1])
axs[1].set_xlabel('Time [sec]')
axs[1].grid(True)

axs[2].plot(velocit_data['Timestamp'], velocit_data.iloc[:, 1], color='red')
axs[2].set_ylabel(velocit_data.columns[1])
axs[2].set_xlabel('Time [sec]')
axs[2].grid(True)

plt.tight_layout()
plt.show()
