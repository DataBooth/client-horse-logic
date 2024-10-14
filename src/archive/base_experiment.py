# Key package information for hardware components

## pigpio - PI General Purpose Input Outputs (GPIO)

# https://github.com/joan2937/pigpio
# http://abyz.me.uk/rpi/pigpio/python.html
# http://abyz.me.uk/rpi/pigpio/examples.html#Python%20code

## PiicoDev® Capacitive Touch Sensor CAP1203

# https://github.com/CoreElectronics/CE-PiicoDev-Capacitive-Touch-Sensor-CAP1203
# https://core-electronics.com.au/guides/piicodev-capacitive-touch-sensor-cap1203-raspberry-pi-guide/
# https://raw.githubusercontent.com/CoreElectronics/CE-PiicoDev-CAP1203-MicroPython-Module/main/PiicoDev_CAP1203.py

## PiicoDev® Buzzer

# https://core-electronics.com.au/piicodev-buzzer-module.html
# https://github.com/CoreElectronics/CE-PiicoDev-Buzzer-MicroPython-Module

## PiicoDev® Unified library

# https://github.com/CoreElectronics/CE-PiicoDev-Unified
# https://github.com/CoreElectronics/CE-PiicoDev-PyPI


# ---------------------------------------------------------------------------- #

# TODO: Seems to me that this script should be run for each subject for a chosen number of trials
#       (and this would represent an experiment i.e. one experiment per subject)
#       Consequently as the start of running this script one would confirm the subject #
#       and the parameters for the experiment (e.g. #trial; other potentially varying parameters above)
#       and that all of this info, plus the logging of events from the each experiment / each trial
#       should in a filename like experiment_start_datetime_subject_number.log
#       Any measurements / data can be easily extracted by processing these files (individually or in aggregate)


import os
import sys
import time
from pathlib import Path
from datetime import datetime as dt
from experiment import log_event, create_logfile_name, initialise_experiment, simulate_beep

RUNNING_ON_RASPBERRY_PI = "arm" not in os.uname().machine

if RUNNING_ON_RASPBERRY_PI:
    import pigpio
    from PiicoDev_Buzzer import PiicoDev_Buzzer
    from PiicoDev_CAP1203 import PiicoDev_CAP1203
    from PiicoDev_Unified import sleep_ms
else:
    print("\nWARNING: Not running on Raspberry Pi - using simulated approach")


# Define experiment parameters
N_TRIAL = 5  # Change this number as required for the number of trials
N_SUBJECT = 20  # The total number of subjects in the experiments

# Data directory
DATA_DIR = Path.cwd() / "data"  # TODO: This may need tweak for Raspberry Pi
if not DATA_DIR.exists():
    print(f"\nERROR: Data directory does not exist - {DATA_DIR.as_posix()}")
    exit()


# Initialise the hardware components
if RUNNING_ON_RASPBERRY_PI:
    (
        rpi,
        buzzer,
        touch_sensor,
        touch_count,
        last_touch_time,
        is_touch_active,
        servo,
    ) = initialise_experiment()
else:
    touch_count = 0
    last_touch_time = None
    is_touch_active = True


# Main loop

subject_number = 0
touch_count = 0

# Q. Does touch_count == i_trial?

# Is the try/except block necessary? Purpose?
try:
    print("\nStarting experiment:")
    print("\n  Press Ctrl-C to exit the experiment\n")
    print("  Ensure the subject is settled in the stall:")
    print(f"   - Commencing the experiment with {N_TRIAL} trials...")

    while subject_number < 1 or subject_number > N_SUBJECT:
        try:
            subject_number = int(input(f"\nEnter subject # (between 1 and {N_SUBJECT}): "))
        except ValueError:
            subject_number = 0

    logfile_name = create_logfile_name(subject_number)

    log_event(DATA_DIR, logfile_name, f"Experiment started for subject #{subject_number}\n", echo_to_console=False)

    print("\n----------------------------------------------------------------------------------------------------------")
    print(f"Experiment started for subject #{subject_number} - logging to:\n\n{DATA_DIR.as_posix()}/{logfile_name}\n")
    print("----------------------------------------------------------------------------------------------------------\n")

    while touch_count < N_TRIAL:
        log_event(DATA_DIR, logfile_name, f"Trial {touch_count + 1} started")

        log_event(DATA_DIR, logfile_name, "Playing start tone")

        if RUNNING_ON_RASPBERRY_PI:
            # Play start tone
            buzzer.tone(1000, 2000)  # Start the start tone
            time.sleep(2)  # Delay for 2 seconds
            buzzer.noTone()  # Stop the start tone
        else:
            simulate_beep(2)

        while True:

            # Check if sensor is touched
            if is_touch_active:
                status = touch_sensor.read()
                print(f"Touch Pad Status: {str(status[1])}  {str(status[2])}  {str(status[3])}")
                # TODO: What is in status[0]?
                sleep_ms(100)

                if status[1] > 0 or status[2] > 0 or status[3] > 0:
                    # Make the buzzer sound for a maximum of 2 seconds
                    buzzer.tone(800, 2000)  # Start the buzzer tone
                    time.sleep(3)  # Delay for 3 seconds

                    # Control the servo motor
                    rpi.set_servo_pulsewidth(SERVO_PIN, SERVO_MAX)  # Move servo to 90 degree position
                    time.sleep(1)  # Delay for 1 second for operation of servo
                    rpi.set_servo_pulsewidth(SERVO_PIN, SERVO_MIN)  # Move servo position back to start

                    start_time = time.time()
                    sleep_ms(5000)  # delay for dispense and consumption of feed- adjust after prototyping with horses

                    touch_count += 1
                    last_touch_time = time.time()

                    if touch_count == N_TRIAL:
                        # Make a different sound after N_TRIAL registered touches
                        buzzer.tone(1200, 500)  # Start the different buzzer tone
                        time.sleep(0.5)
                        buzzer.noTone()  # Stop the different buzzer tone
                        touch_count = 0  # Reset touch count after the session ends

                        # Terminate the script
                        sys.exit()

                    break

except KeyboardInterrupt:
    if RUNNING_ON_RASPBERRY_PI:
        buzzer.noTone()  # Stop the buzzer if program is interrupted
        rpi.set_servo_pulsewidth(SERVO_PIN, 0)  # Move the servo to the stop position
        rpi.stop()  # Release the servo motor control  #TODO: Check that this is intended and not servo variable?


# TODO: Maybe you want to stop the pigpiod process at the end of each experiment? (security-wise)
