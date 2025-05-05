import csv
import pandas as pd
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from pylsl import StreamInlet, resolve_streams, local_clock
import serial

def initialize_csv(file_path, data_type, headers):
    data_file = f"{file_path}{time.strftime('%Y%m%d-%H%M%S')}_{data_type}.csv"
    with open(data_file, 'w', newline='', encoding='UTF-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
    return data_file

def write_to_csv(file_path, data):
    with open(file_path, 'a', newline='', encoding='UTF-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def find_eeg_source(use_test_source=False):
    streams = resolve_streams()
    return StreamInlet(streams[0])

def find_ard_port(com_port, baud_rate=9600):
    try:
        arduino = serial.Serial(
            com_port,
            baud_rate,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1  # Non-blocking read with slight timeout
        )
        arduino.reset_input_buffer()
        return arduino
    except serial.SerialException as e:
        print(f"Error opening COM port {com_port}: {e}")
        return None

def read_eeg_data(inlet, eeg_buffer, stop_event):
    while not stop_event.is_set():
        sample, timestamp = inlet.pull_sample()
        eeg_buffer.append((timestamp, sample[0]))

def read_ard_data(serial_port, serial_port_buffer, stop_event):
    while not stop_event.is_set():
        try:
            line = serial_port.readline().decode('utf-8').strip()
            if line:
                timestamp = local_clock()
                serial_port_buffer.append((timestamp, line))
        except (UnicodeDecodeError, serial.SerialException):
            continue

def convert_buffer_to_dataframe(serial_port_buffer):
    w_data, x_data = [], []
    for timestamp, line in serial_port_buffer:
        if not line:
            continue
        parts = line.split(';')
        try:
            if line.startswith('W'):
                w_data.append({
                    'Timestamp': timestamp,
                    'weigh [kg]': float(parts[2])
                })
            elif line.startswith('X'):
                x_data.append({
                    'Timestamp': timestamp,
                    'acc_x': int(parts[2]),
                    'acc_y': int(parts[3]),
                    'acc_z': int(parts[4])
                })
        except (IndexError, ValueError):
            continue
    return pd.DataFrame(w_data), pd.DataFrame(x_data)

def main():
    stop_event = threading.Event()

    with open("config", "r") as file:
        com_port = file.readline().strip()
        baud_rate = int(file.readline().strip())

    arduino = find_ard_port(com_port, baud_rate)
    if not arduino:
        return
    
    #           USE TEST SOURCE
    # ===========================================
    #
    use_test_source = True
    #
    # ==========================================
    #           USE TEST SOURCE

    inlet = find_eeg_source(use_test_source)

    eeg_buffer = []
    serial_port_buffer = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        print("Starting data collection...")
        executor.submit(read_eeg_data, inlet, eeg_buffer, stop_event)
        executor.submit(read_ard_data, arduino, serial_port_buffer, stop_event)

        try:
            while True:
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("Exiting program gracefully...")
            stop_event.set()

        arduino.close()
        executor.shutdown(wait=True)

        # Process data
        current_time = time.strftime("%Y%m%d_%H%M%S")
        eeg_data = pd.DataFrame(eeg_buffer, columns=["Timestamp", "EMG [V]"])
        w_data, x_data = convert_buffer_to_dataframe(serial_port_buffer)

        # Align timestamps to a common start time
        all_timestamps = []
        for df in [eeg_data, w_data, x_data]:
            if not df.empty:
                df["Timestamp"] = pd.to_numeric(df["Timestamp"], errors="coerce")
                all_timestamps.append(df["Timestamp"].min())

        common_start = min(all_timestamps) if all_timestamps else 0

        for df in [w_data, x_data]:
            if not df.empty:
                df["Timestamp"] -= common_start
        eeg_data["Timestamp"] = eeg_data["Timestamp"] - eeg_data["Timestamp"].iloc[0]
        # Save data
        eeg_data.to_csv(f"measurements/{current_time}_EEG.csv", index=False)
        w_data.to_csv(f"measurements/{current_time}_W.csv", index=False)
        x_data.to_csv(f"measurements/{current_time}_X.csv", index=False)
        print("Data saved successfully.")

if __name__ == "__main__":
    main()


