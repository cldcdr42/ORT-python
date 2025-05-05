List of the commands


-- Inside powershell --
act                                     // activate virtual environment
plot [-n 0]                             // plot latest data (specify n to plot older data)
emulate_eeg                             // emulate EMG signal
collect [-p "COM4"] [-t] [-a]           // start main program of collecting data and interactring with the mcu
                                        // -t - use emulated source
                                        // -a - use verbose output
                                        // -p "COM4" - specify COM-port


-- Inside main program - commands to mcu --
?               - get list of possible commands
A40.5           - specify max angle deviation from current position
D0.05           - specify max torque
Z30.7           - specify angle to turn for
V               - set current angle as new holding angle

ME0             - disable motor
ME1             - enable motor

MLV5            - limit motor voltage
M0.02           - set target (torque value - from 0 to 1)

MMG0            - get target value
MMG6            - get angle value

@2              - user-friendly verbose output (only for commands starting with M)
@0              - no verbose output
