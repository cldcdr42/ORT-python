import csv
import pandas as pd
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from math import pi

import os

import statistics

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

def send_command(arduino, command: str):
    if arduino and arduino.is_open:
        full_command = f"{command}\n"
        arduino.write(full_command.encode('utf-8'))
        print(f"Sent to Arduino: {full_command.strip()}")

def user_command_interface(arduino, stop_event):
    print("Type commands to send to Arduino (e.g., A-40.5), or 'exit' to stop:")
    while not stop_event.is_set():
        try:
            cmd = input()
            if cmd.lower() == 'exit':
                stop_event.set()
                break
            if cmd:
                send_command(arduino, cmd)
        except EOFError:
            break

def read_ard_data(serial_port, serial_port_buffer, stop_event):
    while not stop_event.is_set():
        try:
            #print(repr(serial_port.readline().decode('utf-8')))
            line = serial_port.readline().decode('utf-8').strip()
            #print(line)
            if line:
                timestamp = local_clock()
                serial_port_buffer.append((timestamp, line))
        except (UnicodeDecodeError, serial.SerialException):
            continue

def convert_buffer_to_dataframe(serial_port_buffer):
    mcu_data = []
    for timestamp, line in serial_port_buffer:
        if not line:
            continue
        #parts = line.split(';')
        try:
            if line.startswith('D'):
                target, velocity, angle = line[1:].split(";")
                mcu_data.append({
                    'Timestamp': timestamp,
                    'Target [norm]': float(target),
                    'Angle [rad]': float(angle),
                    'Velocity [rad/s]': float(velocity),
                })
        except (IndexError, ValueError):
            continue
    return pd.DataFrame(mcu_data)

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

    buffer_for_signal = []
    i = 0
    avr_val = 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        print("Starting data collection...")
        executor.submit(read_eeg_data, inlet, eeg_buffer, stop_event)
        executor.submit(read_ard_data, arduino, serial_port_buffer, stop_event)
        executor.submit(user_command_interface, arduino, stop_event)

        try:
            while True:
                # print(float(inlet.pull_sample()[0][0]))
                time.sleep(0.01)
                ###### WRITE HERE SENDING CONTROL SIGNAL AS A FLOAT
                #buffer_for_signal[i] = float(inlet.pull_sample()[0][0])
                #i = i + 1

                #if i >= 200:
                #    i = 0
                
                #avr_val = statistics.mean(abs(buffer_for_signal))
                #print("AVR VAL", avr_val)

                #if avr_val > 1e-4:
                   # continue
                    #arduino.write(0.05)
                ###### WRTIE HERE SENDING CONTROL SIGNAL AS A FLOAT

                """
                1) Get latest 200 samples?
                2) Calculate absolute average?
                3) If it is more, than the threshold, then send a signal
                """
        except KeyboardInterrupt:
            print("Exiting program gracefully...")
            stop_event.set()

        arduino.close()
        executor.shutdown(wait=True)

        # Process data
        current_time = time.strftime("%Y%m%d_%H%M%S")
        eeg_data = pd.DataFrame(eeg_buffer, columns=["Timestamp", "EMG [V]"])
        mcu_data = convert_buffer_to_dataframe(serial_port_buffer)

        # Align timestamps to a common start time
        all_timestamps = []
        for df in [eeg_data, mcu_data]:
            if not df.empty:
                df["Timestamp"] = pd.to_numeric(df["Timestamp"], errors="coerce")
                all_timestamps.append(df["Timestamp"].min())

        common_start = min(all_timestamps) if all_timestamps else 0

        for df in [mcu_data]:
            if not df.empty:
                df["Timestamp"] -= common_start
        eeg_data["Timestamp"] = eeg_data["Timestamp"] - eeg_data["Timestamp"].iloc[0]
        # Save data

        save_folder_name = "./17_meas/" + current_time
        os.mkdir(save_folder_name)

        #print(angle_data)

        mcu_data["Angle [rad]"] = mcu_data["Angle [rad]"] * 180 / pi        
        mcu_data["Velocity [rad/s]"] = mcu_data["Velocity [rad/s]"] * 180 / pi

        # df = df[['Timestamp', 'Target [norm]', 'Angle [deg]', 'Velocity [deg/s]']]
        mcu_data = mcu_data[['Timestamp', 'Angle [rad]', 'Velocity [rad/s]', 'Target [norm]']]
        mcu_data.columns = ['Timestamp', 'Angle [deg]', 'Velocity [deg/s]', 'Target [norm]']
        
        eeg_data.to_csv(f"{save_folder_name}/EMG.csv", index=False)
        mcu_data.to_csv(f"{save_folder_name}/mcu.csv", index=False)
        print("Data saved successfully.")

if __name__ == "__main__":
    main()


