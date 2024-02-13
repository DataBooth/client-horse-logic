import sys
import time
from datetime import datetime, timedelta

import experiment_sounds as wav
from experiment_helper import (
    Servo_grain,
    Servo_pellets,
    elapsed_seconds,
    initialise_GPIO_buttons,
    log_event,
    log_quantity,
    play_WAV,
    setup_experiment,
)


## Local functions


def listenForPause(red_button, logTouches, blue_button, touchSensor):
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

        play_WAV(wav.trialPaused, 1)
        while True:
            if red_button.is_pressed():
                # print(f"Process resumed at: {datetime.now()}, Session resumed")
                log_event("Process resumed", data_dir, log_file)
                play_WAV(wav.trialRestarted, 1)
                return timedelta(0, elapsed_seconds(pauseTime))
    if logTouches:
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
def pausable_sleep(duration_seconds, logTouches, red_button, blue_button, touchSensor):
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
        listenForPause(red_button, logTouches, blue_button, touchSensor)
        elapsed = elapsed_seconds(start_time)
    return timedelta(0, elapsed)


#### Start of experiment ####

(
    subject_name,
    session_number,
    session_type,
    p,
    touchSensor,
    servo,
    data_dir,
    log_file,
    quantity_file,
) = setup_experiment()


# Session settings [these should be defined in the parameters workbook - provided a couple of examples below]
trialLimit = p["TRIAL_LIMIT"]  # all session types
criterionLimit = 3  # check for session type-may differ between session types
criterion_seconds = 20  # max duration in seconds for either a go or no-go response depending on session type
responseTimeout = p["RESPONSE_TIMEOUT"]  # used for RPE-H only- maximum time to respond to a start tone
trialSleepTime = p["TRIAL_SLEEP_TIME"]

# Define mode of operation - test or live
mode = p["MODE"]

if mode == "test":
    trialLimit = 5
    criterion_seconds = 10
    trialSleepTime = 5  # sleep time period to allow feed consumption after a dispense
    responseTimeout = 10

# servo mode - change depending on which feed type is used
servo_mode = p["SERVO_MODE"]

# Create instances of Servo objects
feeder_grain = Servo_grain(servo)
feeder_pellets = Servo_pellets(servo)


# Initialise GPIO and create button instances
gpio, green_button, blue_button, red_button = initialise_GPIO_buttons()


# Initialize variables
trial_count = 0
touch_count = 0
last_touch_time = time.time()
is_touch_active = True
green_button_press_count = 0
blue_button_press_count = 0
last_green_press_time = time.time()  # MJB: currently unused
last_blue_press_time = time.time()

start_tone_played = False

if touchSensor is None:  # MJB testing mode
    # Test use of quantity_file
    for trial_number in range(1, 4):
        log_quantity(
            "test_quantity", 1.0, subject_name, session_number, session_type, trial_number, data_dir, quantity_file
        )
    sys.exit("Exiting test mode - not running on Raspberry Pi\n")

try:
    trial_number = 0

    while True:
        if green_button.is_pressed():
            log_event("Green button pressed", data_dir, log_file)
            green_button_press_count += 1
            if green_button_press_count == 1:
                # pause to avoid button double-press
                log_event(
                    f"System is ready for {subject_name} {session_number} Session type {session_type}",
                    data_dir,
                    log_file,
                )
                play_WAV(wav.systemIsReady, p["SYSTEM_READY_SOUND_DURATION"])

            elif green_button_press_count == 2:
                log_event("Green button pressed 2nd time", data_dir, log_file)
                # pause to avoid button double-press
                criterion_count = 0
                # print(f"Session started for {subject_name} {session_number} Session type {session_type} at: {datetime.now()}")
                log_event(
                    f"Session started for {subject_name} {session_number} Session type {session_type}",
                    data_dir,
                    log_file,
                )
                if session_type == "RPE-A":
                    play_WAV(wav.acquisitionSessionStarted, p["SESSION_STARTED_SOUND_DURATION"])
                elif session_type == "RPE-H":
                    play_WAV(wav.habitSessionStarted, p["SESSION_STARTED_SOUND_DURATION"])
                elif session_type == "RPE-E":
                    play_WAV(wav.extinctionSessionStarted, p["SESSION_STARTED_SOUND_DURATION"])
                elif session_type == "RPE-R":
                    play_WAV(wav.reinstatementSessionStarted, p["SESSION_STARTED_SOUND_DURATION"])
                else:
                    play_WAV(wav.sessionTerminated, p["SESSION_TERMINATED_SOUND_DURATION"])
                pausable_sleep(0.5, False, red_button, blue_button, touchSensor)

                while trial_number < trialLimit:
                    if session_type == "RPE-E":
                        if criterion_count == criterionLimit:
                            play_WAV(wav.criterionAchieved, 3)
                            # print(f"Criterion reached at: {datetime.now()}")
                            log_event("Criterion reached", data_dir, log_file)
                            sys.exit()

                    # begin next trial
                    trial_number += 1
                    # print(f"Current trial: {trial_number}")
                    log_event(f"Current trial: {trial_number}", data_dir, log_file)
                    play_WAV(wav.startTone, 1)
                    start_tone_played = True
                    start_tone_time = datetime.now()
                    # print(f"Start tone played at: {start_tone_time}")
                    log_event("Start tone played", data_dir, log_file)

                    # waiting for either a touch or the blue button
                    while True:
                        start_tone_time = start_tone_time + listenForPause(red_button, False, blue_button, touchSensor)

                        # elapsed = elapsed_seconds(start_tone_time)
                        # print(f"Session type {session_type} - elapsed {elapsed}")

                        # assess timeout
                        if session_type == "RPE-H":
                            if elapsed_seconds(start_tone_time) > responseTimeout:
                                # print(f"Habit formation incorrect response at {datetime.now()}")
                                log_event("Habit formation incorrect response", data_dir, log_file)
                                play_WAV(wav.incorrectTone, 1)
                                start_tone_time = start_tone_time + pausable_sleep(
                                    1, False, red_button, blue_button, touchSensor
                                )
                                break
                        elif session_type == "RPE-E":
                            if elapsed_seconds(start_tone_time) > criterion_seconds:
                                criterion_count += 1
                                # print(f"Criterion count {criterion_count}")
                                log_event(f"Criterion count {criterion_count}", data_dir, log_file)
                                break

                        if blue_button.is_pressed():
                            log_event("Blue button pressed", data_dir, log_file)
                            # manual override
                            if start_tone_played:
                                is_touch_active = False
                                last_touch_time = datetime.now()
                                touch_count += 1
                                # print(f"Manual touch recorded at: {last_touch_time}, Session under manual control")
                                log_event("Manual touch recorded - Session under manual control", data_dir, log_file)

                                # assess goal
                                if session_type == "RPE-A" or session_type == "RPE-R":
                                    if elapsed_seconds(start_tone_time) < criterion_seconds:
                                        criterion_count += 1
                                        # print(f"Criterion count {criterion_count}")
                                        log_event(f"Criterion count {criterion_count}", data_dir, log_file)
                                    else:
                                        criterion_count = 0
                                        # print("Criterion restart")
                                        log_event("Criterion restart", data_dir, log_file)
                                elif session_type == "RPE-E":
                                    criterion_count = 0
                                    # print("Criterion restart")
                                    log_event("Criterion restart", data_dir, log_file)
                                    start_tone_time = start_tone_time + pausable_sleep(
                                        trialSleepTime, True, red_button, blue_button, touchSensor
                                    )
                                    break

                                time.sleep(0.1)
                                play_WAV(wav.correctTone, 1)
                                time.sleep(0.5)
                                if servo_mode == "pellets":
                                    log_event("Dispensing pellets", data_dir, log_file)
                                    feeder_pellets.dispense_feed_pellets()
                                else:
                                    log_event("Dispensing grain", data_dir, log_file)
                                    feeder_grain.dispense_feed_grain()

                                if criterion_count == criterionLimit:
                                    play_WAV(wav.criterionAchieved, 3)
                                    # print(f"Criterion reached at: {datetime.now()}")
                                    log_event("Criterion reached", data_dir, log_file)
                                    sys.exit()

                                if touch_count == trialLimit:
                                    play_WAV(wav.sessionTerminated, 3.5)
                                    # print(f"Session ended at: {datetime.now()}")
                                    log_event("Session ended", data_dir, log_file)
                                    sys.exit()

                                start_tone_time = start_tone_time + pausable_sleep(
                                    trialSleepTime, False, red_button, blue_button, touchSensor
                                )

                            # reset the tone for another touch
                            start_tone_played = False
                            break

                        # do this if the blue button has never been pressed
                        elif is_touch_active:
                            # touch-mode
                            status = touchSensor.read()
                            if status[1] > 0 or status[2] > 0 or status[3] > 0:
                                last_touch_time = datetime.now()
                                touch_count += 1
                                # print(f"Touch-pad status read at: {last_touch_time}")
                                log_event("Touch-pad status read", data_dir, log_file)
                                time.sleep(0.01)

                                if session_type == "RPE-A" or session_type == "RPE-R":
                                    if elapsed_seconds(start_tone_time) < criterion_seconds:
                                        criterion_count += 1
                                        # print(f"Criterion count {criterion_count}")
                                        log_event(f"Criterion count {criterion_count}", data_dir, log_file)
                                    else:
                                        criterion_count = 0
                                        # print("Criterion restart")
                                        log_event("Criterion restart", data_dir, log_file)
                                elif session_type == "RPE-E":
                                    criterion_count = 0
                                    # print("Criterion restart")
                                    log_event("Criterion restart", data_dir, log_file)
                                    start_tone_time = start_tone_time + pausable_sleep(
                                        trialSleepTime, True, red_button, blue_button, touchSensor
                                    )
                                    break

                                play_WAV(wav.correctTone, 1)
                                time.sleep(0.5)
                                if servo_mode == "pellets":
                                    log_event("Dispensing pellets", data_dir, log_file)
                                    feeder_pellets.dispense_feed_pellets()
                                else:
                                    log_event("Dispensing grain", data_dir, log_file)
                                    feeder_grain.dispense_feed_grain()

                                if criterion_count == criterionLimit:
                                    play_WAV(wav.criterionAchieved, 3)
                                    # print(f"Criterion achieved at: {datetime.now()}")
                                    log_event("Criterion achieved", data_dir, log_file)
                                    sys.exit()

                                if touch_count == trialLimit:
                                    play_WAV(wav.sessionTerminated, 3.5)
                                    # print(f"Session ended at: {datetime.now()}")
                                    log_event("Session ended", data_dir, log_file)
                                    sys.exit()

                                start_tone_time = start_tone_time + pausable_sleep(
                                    trialSleepTime, False, red_button, blue_button, touchSensor
                                )
                                break

                if trial_number == trialLimit:
                    log_event("Session terminated - trial limit reached", data_dir, log_file)
                    play_WAV(wav.sessionTerminated, 3.5)
                    sys.exit()

except KeyboardInterrupt:
    log_event("Keyboard interrupt - exiting...", data_dir, log_file)
    gpio.cleanup()
