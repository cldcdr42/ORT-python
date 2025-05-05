# See list of custom powershell commands
# notepad $PROFILE

# activate virtual environment
function act {
    Set-Location "C:\Users\your\project\folder"
    . .\env\Scripts\Activate.ps1
}

# plot data from latest experiment. Replace value of n flag if needed as follows:
# latest experiment:
#   plot -n 0
# second to last experoment
#   plot -n 1
# ...
function plot {
    param(
        [int]$n
    )

    $command = "python ./THIS_plot_data.py"

    if ($PSBoundParameters.ContainsKey('n')) {
        $command += " -n $n"
    }

    Invoke-Expression $command
}

# start emulating EMG signal
function emulate_emg {
    $command = "python ./EEG_emulator.py"

    Invoke-Expression $command
}

# start collecting data and sending commands to MCU
function collect {
    $command = "python ./THIS_read_eeg.py"

    Invoke-Expression $command
}

function what {
    Write-Output "List of the commands"
    
    Write-Output "`n`n-- Inside powershell --"
    Write-Output "act 			// activate virtual environment"
    Write-Output "plot [-n 0] 		// plot latest data (specify n to plot older data)"
    Write-Output "emulate_eeg 		// emulate EMG signal"
    Write-Output "collect 		// start main program of collecting data and interactring with the mcu"

    Write-Output "`n`n-- Inside main program - commands to mcu --"
    Write-Output "? 		- get list of possible commands"
    Write-Output "A40.5 		- specify max angle deviation from current position"
    Write-Output "D0.05 		- specify max torque"
    Write-Output "Z30.7 		- specify angle to turn for"
    Write-Output "V 		- set current angle as new holding angle"

    Write-Output "`nME0 		- disable motor"
    Write-Output "ME1 		- enable motor"

    Write-Output "`nMLV5		- limit motor voltage"
    Write-Output "M0.02		- set target (torque value - from 0 to 1)"

    Write-Output "`nMMG0		- get target value"
    Write-Output "MMG6		- get angle value"

    Write-Output "`n@2		- user-friendly verbose output (only for commands starting with M)"
    Write-Output "@0		- no verbose output"
}
