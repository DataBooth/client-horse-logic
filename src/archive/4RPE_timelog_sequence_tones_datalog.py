import time
import sys
import pygame
from datetime import datetime
from pathlib import Path

try:
    from PiicoDev_CAP1203 import PiicoDev_CAP1203
    from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
except ImportError:
    RPI_MODE = False
    print("\n**** Running in non-RPi mode for testing only ****\n")

from experiment_helper import (
    create_output_filenames,
    set_directory,
    log_event,
    set_subject_number,
    confirm_experiment_details,
    choose_experiment_type,
    load_validate_experimental_parameters,
    log_trial_parameters,
)

tones = {
    "start": "Start_tone_600.wav",
    "correct": "Correct_tone_1000.wav",
    "end": "End_tone_1200.wav",
}

# Specify the paths for the data directory and the tones directory.

DATA_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/data"  # CH: Hard-coded example only
TONE_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/src/tones"  # CH: example only


def initialise_touch_sensor(sensitivity):
    """
    Initialises the touch sensor based on the given sensitivity level.

    Args:
        sensitivity (int): The sensitivity level of the touch sensor.

    Returns:
        PiicoDev_CAP1203: The initialised touch sensor object.
    """
    touch_sensor = PiicoDev_CAP1203(touchmode="single", sensitivity=sensitivity)
    return touch_sensor


def initialise_servo(servo_channel):
    """
    Initialises a servo motor.

    Args:
        servo_channel (int, optional): The channel number of the servo motor. Default is SERVO_CHANNEL.

    Returns:
        PiicoDev_Servo: The initialised servo motor object.
    """
    servo_driver = PiicoDev_Servo_Driver()
    servo = PiicoDev_Servo(servo_driver, servo_channel)
    return servo


def initialise_sensors(sensitivity, servo_channel, Rpi=False):
    """
    Initialises the sensors based on the given parameters.

    Args:
        sensitivity (int, optional): The sensitivity level of the touch sensor. Default is 4.
        Rpi (bool, optional): A boolean flag indicating whether the code is running on a Raspberry Pi. Default is False.

    Returns:
        tuple: A tuple containing the initialised touch sensor and servo objects.

    Example:
        touch_sensor, servo = initialise_sensors(sensitivity=4, Rpi=True)

    """
    if Rpi:
        touch_sensor = initialise_touch_sensor(sensitivity)
        servo = initialise_servo(servo_channel)
        return touch_sensor, servo
    else:
        return None, None


def play_wav_file(tone_name, duration_sec, tone_dir):
    """
    Play a WAV file with a specified tone name, duration, and tone directory.

    Args:
        tone_name (str): The name of the tone to be played. See the `tones` dictionary for the available tones.
        duration_sec (float): The duration of the tone in seconds.
        tone_dir (str): The directory where the WAV files are located.

    Raises:
        FileNotFoundError: If the specified tone directory does not exist.

    Returns:
        None. The function does not return any value.
    """
    if not Path(tone_dir).exists():
        # print error and exit
        raise FileNotFoundError(f"The specified tone directory {tone_dir} does not exist.")
    sound = pygame.mixer.Sound(f"{tone_dir}/{tones[tone_name]}")
    sound.play()
    time.sleep(duration_sec)  # wait for the specified duration (s)
    sound.stop()


def initialise_directories():
    """
    Initialises the data and tone directories.

    Returns:
    - data_dir: The initialized data directory.
    - tone_dir: The initialized tone directory.
    """
    data_dir = set_directory(DATA_DIR)
    tone_dir = set_directory(TONE_DIR)
    return data_dir, tone_dir


def initialise_experiment(subject_name, initial_delay, experiment_type):
    """
    Initialises the experiment by generating output filenames, and logging important information.

    Args:
        subject_number (int): The number of the subject for which the experiment is being initialised.
        initial_delay (int, optional): The initial delay in seconds before the experiment starts. Default is 10 seconds.

    Returns:
        tuple: A tuple containing the following elements:
            - log_file (str): The name of the log file.
            - measurement_file (str): The name of the measurement file.
            - initial_delay (int): The initial delay in seconds before the experiment starts.
    """
    log_file, measurement_file = create_output_filenames(subject_name, session_number, experiment_type)
    log_event(f"Data directory: {data_dir}", data_dir, log_file)
    log_event(f"Log file: {log_file}", data_dir, log_file)
    log_event(f"Measurement file: {measurement_file}", data_dir, log_file)
    return log_file, measurement_file, initial_delay


#### Start of experiment ####

pygame.mixer.init()  # Initialise the mixer module for playing WAV files
data_dir, tone_dir = initialise_directories()
# experiment_type -- todo put in choice function

p = load_validate_experimental_parameters(data_dir)

touch_sensor, servo = initialise_sensors(p["SENSITIVITY"], p["SERVO_CHANNEL"], Rpi=RPI_MODE)
subject_name, session_number = set_subject_number(p["N_TRIAL"], data_dir)
experiment_type = choose_experiment_type()
if not confirm_experiment_details(subject_name, session_number, experiment_type, p["N_TRIAL"]):
    sys.exit()
log_file, measurement_file, initial_delay = initialise_experiment(subject_name, p["INITIAL_DELAY"], experiment_type)
log_event(f"Subject {subject_name} - Session {session_number} started...", data_dir, log_file)
log_trial_parameters(p, data_dir, log_file)



# Initialise key tracking variables

sequence_count = 0
touch_count = 0
last_touch_time = time.time()
is_touch_active = True

# Example of logging a measurement quantity

log_event(
    f"Last touch time: {last_touch_time}",
    data_dir,
    log_file,
    log_as_measurement=True,
    echo_to_console=False,
)

log_event(
    f"Waiting for {initial_delay} seconds before starting the first sequence...",
    data_dir,
    log_file,
)

# Wait for button press to start the experiment

# TODO: Check if button is pressed - something like this:
# while not button.is_pressed():
#    pass


time.sleep(initial_delay)  # Add the initial delay

# Main loop

try:
    sequence_number = 1  # Initialise the sequence number
    is_button_pressed = False

    while touch_count < N_TOUCH and not is_button_pressed:  # Adjust the number of touches as needed
        # Print the current sequence number
        log_event(f"Current sequence: {sequence_number}", data_dir, log_file)
        play_wav_file("start", duration_sec=2, tone_dir=tone_dir)
        log_event("Start tone played", data_dir, log_file)

        while True:
            if not RPI_MODE:
                print("\n**** Exiting non-RPi mode (testing only) ****\n")
                sys.exit()

            # Check if sensor is touched
            if is_touch_active:
                status = touch_sensor.read()

                if status[1] > 0 or status[2] > 0 or status[3] > 0:
                    log_event("Touch-pad status read", data_dir, log_file)
                    time.sleep(TOUCH_PAD_DELAY)
                    play_wav_file("correct", duration_sec=2, tone_dir=tone_dir)
                    time.sleep(SERVO_DELAY)

                    # Control the servo motor
                    servo.angle = SERVO_OPEN
                    log_event("Feed dispensed", data_dir, log_file)
                    time.sleep(SERVO_DELAY_AFTER_FEED)  # Delay operation of servo
                    servo.angle = SERVO_CLOSE

                    start_time = time.time()
                    time.sleep(FEED_DISPENSE)

                    touch_count += 1
                    last_touch_time = time.time()

                    log_event(
                        f"{last_touch_time}",
                        data_dir,
                        log_file,
                        log_as_measurement=True,
                        echo_to_console=False,
                    )

                    # TODO: Check if button is pressed - something like this:
                    # is_button_pressed = button.is_pressed()

                    if (
                        touch_count == N_TRIAL
                    ):  # CH: Change this number as required for the number of trials ## CHECK THIS number? Should this be N_TOUCH?
                        # Make a different sound after n registered touches
                        play_wav_file("end", duration_sec=3, tone_dir=tone_dir)
                        touch_count = 0  # CH: Reset touch count after the session ends -- probs not needed - reset each time at start of loop
                        log_event("Session ended", data_dir, log_file)
                        sys.exit()  # Terminate the script
                    break

        sequence_number += 1  # Increment the sequence number ## CHECK: Get sequence/trial language consistent

except KeyboardInterrupt:
    log_event("Keyboard interrupt - exiting...", data_dir, log_file)
    if RPI_MODE:
        servo.release()
