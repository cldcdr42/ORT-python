function act {
    Set-Location "C:\Users\User\Desktop\Folder\university\Project\orthoses-no-GUI-forExperiment"
    . .\env\Scripts\Activate.ps1
}

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

function emulate_emg {
    $command = "python ./EEG_emulator.py"

    Invoke-Expression $command
}

function collect {
    param(
        [switch]$t,     # Accepts the -t flag
        [switch]$a,
        [string]$p     # Optional port with default
    )

    $command = "python ./THIS_read_eeg.py"

    if ($t.IsPresent) {
        $command += " -t"
    }

    if ($a.IsPresent) {
        $command += " -a"
    }

    if ($p) {
        $command += " -p $p"
    }

    Invoke-Expression $command
}


function what {
    Write-Output "List of the commands"
    
    Write-Output "`n`n-- Inside powershell --"
    Write-Output "act 					// activate virtual environment"
    Write-Output "plot [-n 0] 				// plot latest data (specify n to plot older data)"
    Write-Output "emulate_eeg 				// emulate EMG signal"
    Write-Output "collect [-p `"COM4`"] [-t] [-a]		// start main program of collecting data and interactring with the mcu
					// -t - use emulated source
					// -a - use verbose output
					// -p `"COM4`" - specify COM-port"

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
