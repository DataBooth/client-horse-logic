import sys
import time
from datetime import datetime, timedelta

import cb_experiment_sounds as wav
from cb_helper import (
    Servo_pellets,
    elapsed_seconds,
    initialise_GPIO_buttons,
    log_event,
    play_WAV,
    setup_experiment,
    load_experiment_design,
    session_main_type,
    criterion_timeout,
)

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
    measurement_file,
    steps,
) = setup_experiment()


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
    sys.exit("Exiting test mode - not running on Raspberry Pi\n")

try:
    trial_number = 0

    for ds in steps:
        print(f"{ds.name}")

    # criterion assessment
    positive_criterion_count = 0
    negative_criterion_count = 0

    play_WAV(wav.systemIsReady, p["SYSTEM_READY_SOUND_DURATION"])

    while True:
        if green_button.is_pressed():
            log_event("Green button pressed - system ready", data_dir, log_file)
            # pause to avoid button double-press
            log_event(
                f"System is ready for {subject_name} {session_number} Session type {session_type}",
                data_dir,
                log_file,
            )

            # alert team to confirm session type
            if session_type == "Training - fixed":
                play_WAV(wav.trainingFixed, p["FIRST_TRIAL_DURATION"])
                # criterion - go response within 20s - 8 out of 10 for positive
                # crtierion - nogo response within 20s - 8 out of 10 for negative
            elif session_type == "Training randomised Type 1":
                play_WAV(wav.trainingRandomisedType1, p["FIRST_TRIAL_DURATION"])
                # criterion - go response within 20s - 8 out of 10 for positive
                # crtierion - nogo response within 20s - 8 out of 10 for negative
            elif session_type == "Training randomised Type 2":
                play_WAV(wav.trainingRandomisedType2, p["FIRST_TRIAL_DURATION"])
                # criterion - go response within 20s - 8 out of 10 for positive
                # crtierion - nogo response within 20s - 8 out of 10 for negative
            elif session_type == "Test Type 1":
                play_WAV(wav.testType1, p["FIRST_TRIAL_DURATION"])
                # no criterion for tests
                # 30s rather than 20s
                # just log what happens
            elif session_type == "Test Type 2":
                play_WAV(wav.testType2, p["FIRST_TRIAL_DURATION"])
                # no criterion for tests
                # 30s rather than 20s
                # just log what happens
            elif session_type == "Test Type 3":
                play_WAV(wav.testType3, p["FIRST_TRIAL_DURATION"])
                # no criterion for tests
                # 30s rather than 20s
                # just log what happens
            break

    for ds in steps:
        if ds.step_type == "positive":
            play_WAV(wav.positive, p["TRIAL_SOUND_DURATION"])
        elif ds.step_type == "negative":
            play_WAV(wav.negative, p["TRIAL_SOUND_DURATION"])
        elif ds.step_type == "median":
            play_WAV(wav.median, p["TRIAL_SOUND_DURATION"])
        elif ds.step_type == "near negative":
            play_WAV(wav.nearNegative, p["TRIAL_SOUND_DURATION"])
        elif ds.step_type == "near positive":
            play_WAV(wav.nearPositive, p["TRIAL_SOUND_DURATION"])
        else:
            break

        # log trial
        log_event(f"Current Trial {ds.name} - {ds.step_type}", data_dir, log_file)

        while True:
            if green_button.is_pressed():
                trial_start_time = datetime.now()
                print("Green button pressed - horse released")
                log_event("Green button pressed - horse released", data_dir, log_file)
                play_WAV(wav.horseReleased, p["TRIAL_SOUND_DURATION"])
                break

        # print(f"Session type = {session_main_type(session_type)}")

        while True:
            # evaluate elapsed time
            response = elapsed_seconds(trial_start_time)

            if ds.step_type == "positive":
                if (
                    session_main_type(session_type) == "training"
                    and response > p["POSITIVE_RESPONSE_TIMEOUT"]
                ) or (session_main_type(session_type) == "test" and response > p["TEST_TIMEOUT"]):
                    print(f"NOGO for {ds.name} - {ds.step_type}")
                    log_event(f"NOGO for {ds.name} - {ds.step_type}", data_dir, log_file)
                    play_WAV(wav.noGoResponse, p["TRIAL_SLEEP_TIME"])
                    break

                # horse has 60 s until green button
                elif green_button.is_pressed():
                    if response < criterion_timeout(
                        session_type, p["CRITERION_TIMEOUT_TRAINING"], p["TEST_TIMEOUT"]
                    ):
                        positive_criterion_count += 1
                        print(
                            f"GO for {ds.name} - {ds.step_type} - response time {response} - positive criterion count {positive_criterion_count}"
                        )
                        log_event(
                            f"GO for {ds.name} - {ds.step_type} - response time {response} - positive criterion count {positive_criterion_count}",
                            data_dir,
                            log_file,
                        )
                        play_WAV(wav.goResponseCriterion, p["TRIAL_SLEEP_TIME"])
                        break
                    else:
                        print(f"GO for {ds.name} - {ds.step_type} - response time {response}")
                        log_event(
                            f"GO for {ds.name} - {ds.step_type} - response time {response}",
                            data_dir,
                            log_file,
                        )
                        play_WAV(wav.goResponse, p["TRIAL_SLEEP_TIME"])
                        break

            elif ds.step_type == "negative":
                if (
                    session_main_type(session_type) == "training"
                    and response > p["NEGATIVE_RESPONSE_TIMEOUT"]
                ) or (session_main_type(session_type) == "test" and response > p["TEST_TIMEOUT"]):
                    negative_criterion_count += 1
                    print(
                        f"NOGO for {ds.name} - {ds.step_type} - criterion count {negative_criterion_count}"
                    )
                    log_event(
                        f"NOGO for {ds.name} - {ds.step_type} - negative criterion count {negative_criterion_count}",
                        data_dir,
                        log_file,
                    )
                    play_WAV(wav.noGoResponseCriterion, p["TRIAL_SLEEP_TIME"])
                    break

                elif red_button.is_pressed():
                    print(f"GO for {ds.name} - {ds.step_type} - response time {response}")
                    log_event(
                        f"GO for {ds.name} - {ds.step_type} - response time {response}",
                        data_dir,
                        log_file,
                    )
                    play_WAV(wav.goResponse, p["TRIAL_SLEEP_TIME"])
                    break

            elif (
                ds.step_type == "median"
                or ds.step_type == "near positive"
                or ds.step_type == "near negative"
            ):
                if response > p["TEST_TIMEOUT"]:
                    print(f"NOGO for {ds.name} - {ds.step_type} - response time {response}")
                    log_event(
                        f"NOGO for {ds.name} - {ds.step_type} - response time {response}",
                        data_dir,
                        log_file,
                    )
                    play_WAV(wav.noGoResponse, p["TRIAL_SLEEP_TIME"])
                    break

                elif blue_button.is_pressed():
                    print(f"GO for {ds.name} - {ds.step_type}")
                    log_event(f"GO for {ds.name} - {ds.step_type}", data_dir, log_file)
                    play_WAV(wav.goResponse, p["TRIAL_SLEEP_TIME"])
                    break

    # trials complete
    log_event("Session terminated - session complete", data_dir, log_file)
    play_WAV(wav.sessionTerminated, 3.5)

    # assess positive criterion
    if positive_criterion_count > 7:
        print(f"Positive criterion reached - {positive_criterion_count}")
        log_event(f"Positive criterion reached - {positive_criterion_count}", data_dir, log_file)
        play_WAV(wav.positiveCriterionReached, p["TRIAL_SOUND_DURATION"])

    # assess negative criterion
    if negative_criterion_count > 7:
        print(f"Negative criterion reached - {negative_criterion_count}")
        log_event(f"Negative criterion reached - {negative_criterion_count}", data_dir, log_file)
        play_WAV(wav.negativeCriterionReached, p["TRIAL_SOUND_DURATION"])

    sys.exit()

except KeyboardInterrupt:
    log_event("Keyboard interrupt - exiting...", data_dir, log_file)
    gpio.cleanup()
