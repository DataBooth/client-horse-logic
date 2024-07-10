import sys
import time
from datetime import datetime, timedelta

from text_to_speech import TextToSpeechGoogle

from experiment_helper import (
    elapsed_seconds,
    initialise_GPIO_buttons,
    log_event,
    log_quantity,
    setup_experiment,
)


## Local functions


def listenForPause(red_button, blue_button):
    """
    Check if the red button is pressed. If pressed, log the pause event, play a sound,
    and enter a loop until the red button is pressed again.
    If the blue button or touch sensor is pressed, log the corresponding event and
    wait for a short period of time.
    Return the duration of the pause as a timedelta object.

    Args:
        red_button (object): An object representing the red button.
        logTouches (bool): A boolean indicating whether to log touch events.
        blue_button (object): An object representing the blue button.
        touchSensor (object): An object representing the touch sensor.

    Returns:
        timedelta: A timedelta object representing the duration of the pause.
    """
    if red_button.is_pressed():
        pauseTime = datetime.now()
        # Process pause
        # print(f"Process paused at: {datetime.now()}, Session paused")
        log_event("Process paused", data_dir, log_file)

        while True:
            if red_button.is_pressed():
                # print(f"Process resumed at: {datetime.now()}, Session resumed")
                log_event("Process resumed", data_dir, log_file)
                return timedelta(0, elapsed_seconds(pauseTime))

    if blue_button.is_pressed():
        # print(f"Manual touch recorded during sleep at: {datetime.now()}, Session under manual control")
        log_event("Manual touch recorded - Session under manual control", data_dir, log_file)
        time.sleep(0.5)
    status = touchSensor.read()
    if status[1] > 0 or status[2] > 0 or status[3] > 0:
        # print(f"Touch-pad status read during sleep at: {datetime.now()}")
        log_event("Touch-pad status read during sleep", data_dir, log_file)
        time.sleep(0.5)
    return timedelta(0, 0)


# need a description of what this is and what it does?
def pausable_sleep(duration_seconds, red_button, blue_button):
    """
    Pause and resume a sleep operation.

    Args:
        duration_seconds (float): The duration in seconds for the sleep operation.
        logTouches (bool): A flag indicating whether to log touches during the sleep operation.

    Returns:
        timedelta: The total elapsed time during the sleep operation.
    """
    start_time = datetime.now()
    elapsed = elapsed_seconds(start_time)
    while elapsed < duration_seconds:
        listenForPause(red_button, blue_button)
        elapsed = elapsed_seconds(start_time)
    return timedelta(0, elapsed)


#### Start of experiment ####

(
    subject_name,
    trial_number,
    trainer_number,
    p,
    data_dir,
    log_file,
    quantity_file,
) = setup_experiment()


# Session settings [these should be defined in the parameters workbook - provided a couple of examples below]
trialLimit = p["TRIAL_LIMIT"]  # all session types
responseTimeout = p["RESPONSE_TIMEOUT"]  # used for RPE-H only- maximum time to respond to a start tone
trialSleepTime = p["TRIAL_SLEEP_TIME"]

# Define mode of operation - test or live
mode = p["MODE"]

if mode == "test":
    trialLimit = 5
    responseTimeout = 10


# Initialise GPIO and create button instances
gpio, green_button, blue_button, red_button = initialise_GPIO_buttons()


# Initialize variables
trial_count = 0
touch_count = 0
green_button_press_count = 0
blue_button_press_count = 0
last_green_press_time = time.time()  # MJB: currently unused
last_blue_press_time = time.time()

start_tone_played = False


try:
    trial_number = 0

    while True:
        if green_button.is_pressed():
            log_event("Green button pressed", data_dir, log_file)
            green_button_press_count += 1
            if green_button_press_count == 1:
                # pause to avoid button double-press
                log_event(
                    f"System is ready for {subject_name} {trial_number} Trainer # {trainer_number}",
                    data_dir,
                    log_file,
                )

            elif green_button_press_count == 2:
                log_event("Green button pressed 2nd time", data_dir, log_file)
                # pause to avoid button double-press
                log_event(
                    f"Session started for {subject_name} {trial_number} Trainer # {trainer_number}",
                    data_dir,
                    log_file,
                )

                # Play experiment details?

                while trial_number < trialLimit:
                    # begin next trial
                    trial_number += 1
                    log_event(f"Current trial: {trial_number}", data_dir, log_file)
                    # play sound/details ?
                    start_tone_played = True
                    start_tone_time = datetime.now()
                    log_event("Start tone played", data_dir, log_file)

                    # waiting for either a touch or the blue button
                    while True:
                        start_tone_time = start_tone_time + listenForPause(red_button, blue_button)

                        # elapsed = elapsed_seconds(start_tone_time)
                        # print(f"Trainer # {trainer_number} - elapsed {elapsed}")

                        if blue_button.is_pressed():
                            log_event("Blue button pressed", data_dir, log_file)
                            # manual override
                            log_event(
                                "Manual touch recorded - Session under manual control",
                                data_dir,
                                log_file,
                            )

                            # reset the tone for another touch
                            start_tone_played = False
                            break

                if trial_number == trialLimit:
                    log_event("Session terminated - trial limit reached", data_dir, log_file)
                    # play end sound?
                    sys.exit()

except KeyboardInterrupt:
    log_event("Keyboard interrupt - exiting...", data_dir, log_file)
    gpio.cleanup()
