# Background information on the experimental design

# Each session (trial?) will be about 10 minutes per horse, 20 horses, x 1 session a day, x probably 7 days total.
# So 20 horses x 10 minutes x 7 days = 1400 minutes = 23.3 hours of data.

# We will want to collect correct responses and the latency between the correct responses.
# Am thinking we will need a "go" signal-probably a noise, then measure the time between that and a correct response.
# Then a set period of time out, then go signal again and commencement of trial.
# So recording the latency between go signal and beginning of time out period, or between go signals.

# Will you also want to record the time between the go signal and the correct response?

# I expect it will be that once the touch sensor is triggered, that will start a time out period where
# no further presses would be registered.
# Then after the time period has elapsed, the next touch would be registered and so on

# There  will be 20 subjects.  All subjects will do the same training.
# We are not sure yet whether we go with a fixed number of trials or trials to criteria.

# Questions:
# 1. How many trials per session? (confirm 1 i.e. session == trial) - may need to change this
# 2. How many sessions per day? (confirm 1)
# 3. How many days do the trials run for? (confirm 7)
# 4. How many subjects? (confirm 20)
# 5. How many sensors? (confirm 1 - touch sensor)
# 6. How many trials per subject? (confirm one per day * # days)
# 7. How many trials in total? (confirm 20 * 7)
# 8. How many observations per trial? (confirm 0 or 1 within the maximum allowed time of 10 minutes)
# 9. Each observation is a touch sensor event (confirm)?
# 10. What is the maximum time allowed for a trial? (confirm 10 minutes)
# 11. So an observation/measurement is either "null" or a time in seconds (i.e. the latency - correct definition)?
# 12. Do you want to record other details of the experiment e.g. temperature, humidity, etc.? time dependent?
# 13. What constitutes a "correct" response? (confirm touch sensor event)
# 14. What constitutes an "missed" response? (confirm no touch sensor event within the maximum allowed time of 10 minutes)
# 15. There will be a noise to signal the start of the trial.  Will this be initiated by the computer or the experimenter?
# 16. Looks like the experiment will "reset" after the time out period and then re-run for the same subject?


from datetime import datetime as dt
from functools import cache
import numpy as np
import simpleaudio as sa
from pathlib import Path
import os


# Define key hardware parameters
TOUCH_SENSITIVITY_LEVEL = 6
SERVO_PIN = 18  # GPIO pin for the servo
SERVO_MIN = 500  # Minimum pulse width for the servo
SERVO_MAX = 2500  # Maximum pulse width for the servo


MAX_N_OBSERVATION = 30
MAX_TIME_TRIAL_SECONDS = 2 * 60.0


def log_event(
    data_dir,
    log_file,
    event_name,
    event_time=None,
    echo_to_console=True,
):
    """Log the event name and time to a file."""
    if event_time is None:
        event_time = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(Path(data_dir) / log_file, "a") as f:
        f.write(f"{event_time}: {event_name}\n")
    if echo_to_console:
        print(f"Logged - {event_time}: {event_name}\n")
    return None


@cache
def calculate_audio(duration, fs):
    frequency = 880  # Our played note will be 440 Hz
    seconds = duration  # Duration in seconds (must be integer)

    # fs: samples per second
    # Generate array with seconds*sample_rate steps, ranging between 0 and seconds
    t = np.linspace(0, seconds, seconds * fs, False)

    # Generate a 440 Hz sine wave
    note = np.sin(frequency * t * 2 * np.pi)

    # Ensure that highest value is in 16-bit range
    audio = note * (2**15 - 1) / np.max(np.abs(note))
    # Convert to 16-bit data
    audio = audio.astype(np.int16)
    return audio


def simulate_beep(duration=1, fs=44100):
    """Play a beep sound for the specified duration in seconds."""
    audio = calculate_audio(duration, fs)

    # Start playback
    play_obj = sa.play_buffer(audio, 1, 2, fs)

    # Wait for playback to finish before exiting
    play_obj.wait_done()


def play_correct_response_tone():
    """Play the correct response tone."""
    log_event("Start playing correct response tone", dt.now())
    play_beep(duration=1)
    log_event("Finished playing correct response tone", dt.now())
    return None


def dispense_feed():
    """Dispense feed."""
    log_event("Dispensing feed", dt.now())
    # code to dispense feed
    return None


def wait_for_period_of_time(event_name, duration_sec):
    """Wait for the specified duration in seconds."""
    log_event(f"{event_name}: Waiting for {duration_sec} seconds", dt.now())
    sleep(duration_sec)
    log_event(f"{event_name}: Finished waiting for {duration_sec} seconds", dt.now())
    return None


def wait_for_start_button_press():
    while True:
        if input("Press [ENTER] to start the trial") == "":
            log_event("Trial ready to start", dt.now())
            break
    return None


def log_trial_parameters(trial_parameters_names, log_file):
    trial_parameters = {key: eval(key) for key in trial_parameters_names}

    """Log the trial parameters to a file."""
    with open(log_file, "a") as f:
        f.write(f"TRIAL PARAMETERS: {trial_parameters}\n")
    print(f"Logged - TRIAL PARAMETERS: {trial_parameters}\n")
    return None


def create_logfile_name(subject_number):
    LOGFILE_PREFIX = "Experiment"
    return f"{LOGFILE_PREFIX}_{dt.now().isoformat()}_Subject_{subject_number}.log"


def initialise_experiment():
    # Start the pigpio daemon
    START_CMD_PI_GPIO_PROCESS = "sudo pigpiod"
    os.system(START_CMD_PI_GPIO_PROCESS)
    # TODO: Does this work without specifying an admin password?

    # Initialise the sensors
    buzzer = PiicoDev_Buzzer()
    touch_sensor = PiicoDev_CAP1203(touchmode="single", sensitivity=TOUCH_SENSITIVITY_LEVEL)

    # Initialise touch sensor variables
    touch_count = 0
    last_touch_time = time.time()
    is_touch_active = True

    # Connect to the local Raspberry Pi GPIO
    rpi = pigpio.pi()

    # create a servo object
    servo = rpi.set_servo_pulsewidth(SERVO_PIN, 0)
    # TODO: Note that the servo variable is not used subsequently

    return (
        rpi,
        buzzer,
        touch_sensor,
        touch_count,
        last_touch_time,
        is_touch_active,
        servo,
    )
