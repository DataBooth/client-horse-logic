import time
from datetime import datetime, timedelta
from PiicoDev_CAP1203 import PiicoDev_CAP1203
import RPi.GPIO as GPIO
import sys
from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
import pygame

# NOTE new=Wav file paths- delete old paths
systemIsReadyWav = "/home/horselogic/Documents/test audio project_data/System_is_ready1.wav"
sessionStartedWav = "/home/horselogic/Documents/test audio project_data/Session_started1.wav"
trialPausedWav = "/home/horselogic/Documents/test audio project_data/Trial paused1.wav"
trialRestartedWav = "/home/horselogic/Documents/test audio project_data/Trial restarted1.wav"
sessionTerminated = "/home/horselogic/Documents/test audio project_data/End tone_1200_sess_completed.wav"
startToneWav = "/home/horselogic/Documents/test audio project_data/Start tone _600.wav"
correctToneWav = "/home/horselogic/Documents/test audio project_data/Correct tone_1000.wav"
incorrectToneWav = "/home/horselogic/Documents/test audio project_data/IncorrectTone.wav"
endToneWav = "/home/horselogic/Documents/test audio project_data/End tone_1200.wav"
criterionAchievedWav = "//home/horselogic/Code/2Final_RPE_code_DRAFT.pyhome/horselogic/Documents/test audio project_data/Criterion_reached.wav"
criterionNotReachedWav = "/home/horselogic/Documents/test audio project_data/Criterion_ not_reached.wav"
acquisitionSessionStartedWav = "/home/horselogic/Documents/test audio project_data/Acquistion_Session_Started.wav"
habitSessionStartedWav = "/home/horselogic/Documents/test audio project_data/Habit_session_started.wav"
extinctionSessionStartedWav = "/home/horselogic/Documents/test audio project_data/Extinction_session_started.wav"
reinstatementSessionStartedWav = "/home/horselogic/Documents/test audio project_data/Reinstatement_session_started.wav"

# RP-A= acquisition of response
# trialLimit = 20 per session, multiple sessions until acquisition criterion
# unlimited time between start tone and touch (or button)
# criterion = n touches in a row that occur under 20 sec from start tone
# no responseTimeout
# RP-H= habit formation
# trialLimit 20 fixed trials per session, 3 sesions
# reponseTimeout 45s
# RP-E= extinction of response
# trialLimit  = 20, multiple session until extinction criterion
# number of responses in a row
# criterion_seconds = 20s
# RP-R= reinstatement of response
# trialLimit = 20 per session, multiple sessions unil acquisition criterion
# no responseTimeout

# At beginning of each session for each horse- check and change session type to one of:
# RP-A = acquisition,
# RP-H = habit formation,
# RP-E= extinction,
# RP-R = reinstatement
session_type = "RP-E"

# session settings
trialLimit = 20  # all session types
criterionLimit = 3  # check for session type-may differ between sesison types
criterion_seconds = 20  # max duration in seconds for either a go or no-go response depending on session type
responseTimeout = 45  # used for RP-H only- maximum time to respond to a start tone

# Define mode of operation - test or live
trialSleepTime = 5
mode = "test"
if mode == "test":
    trialLimit = 5
    criterion_seconds = 10
    trialSleepTime = 5  # sleep time period to allow feed consumption after a dispense
    responseTimeout = 10

# servo mode- change depending on which feed type is used.
servo_mode = "pellets"
# servo_mode = 'grain'

# Initialize the sensors
touchSensor = PiicoDev_CAP1203(touchmode="single", sensitivity=5)

# Initialize the servo driver
servo_driver = PiicoDev_Servo_Driver()

# Initialize the servo
servo = PiicoDev_Servo(servo_driver, 1)


# Define Servo objects for different types of feed. Can adjust the angles and times if needed
class Servo_pellets:
    def __init__(self, servo):
        self.servo = servo

    def dispense_feed_pellets(self):
        self.servo.angle = 80
        print(f"Feed dispensed at: {datetime.now()}")
        time.sleep(0.5)
        self.servo.angle = 0


class Servo_grain:
    def __init__(self, servo):
        self.servo = servo

    def dispense_feed_grain(self):
        self.servo.angle = 70
        print(f"Feed dispensed at: {datetime.now()}")
        time.sleep(0.5)
        self.servo.angle = 0


# Create instances of Servo objects
feeder_grain = Servo_grain(servo)
feeder_pellets = Servo_pellets(servo)

# Set up GPIO pins for buttons
GPIO.setmode(GPIO.BCM)
butpin_green = 6  # Green button
butpin_blue = 7  # Blue button
butpin_red = 12  # Red button

# Set up GPIO pins for input with an internal pull-up resistor
GPIO.setup(butpin_green, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(butpin_blue, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(butpin_red, GPIO.IN, pull_up_down=GPIO.PUD_UP)


class Button:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self):
        return GPIO.input(self.pin) == GPIO.LOW


# Create button instances
green_button = Button(butpin_green)
blue_button = Button(butpin_blue)
red_button = Button(butpin_red)


# Function to play WAV file for a specified duration
def play_WAV(file_path, duration):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.play()
    pygame.time.delay(int(duration * 1000))
    time.sleep(duration)
    sound.stop()


# need a description of what this is?
def elapsed_seconds(start_time):
    delta_since_start = datetime.now() - start_time
    duration_since_start = delta_since_start.total_seconds()
    return duration_since_start


def listenForPause(logTouches):
    if red_button.is_pressed():
        pauseTime = datetime.now()
        # Process pause
        print(f"Process paused at: {datetime.now()}, Session paused")
        play_WAV(trialPausedWav, 1)
        while True:
            if red_button.is_pressed():
                print(f"Process resumed at: {datetime.now()}, Session resumed")
                play_WAV(trialRestartedWav, 1)
                return timedelta(0, elapsed_seconds(pauseTime))

    if logTouches == True:
        if blue_button.is_pressed():
            print(f"Manual touch recorded during sleep at: {datetime.now()}, Session under manual control")
            time.sleep(0.5)

        status = touchSensor.read()
        if status[1] > 0 or status[2] > 0 or status[3] > 0:
            print(f"Touch-pad status read during sleep at: {datetime.now()}")
            time.sleep(0.5)

    return timedelta(0, 0)


# need a description of what this is and what it does?
def pausable_sleep(duration_seconds, logTouches):
    start_time = datetime.now()
    elapsed = elapsed_seconds(start_time)
    while elapsed < duration_seconds:
        listenForPause(logTouches)
        elapsed = elapsed_seconds(start_time)
    return timedelta(0, elapsed)


# Initialize variables
trial_count = 0
touch_count = 0
last_touch_time = time.time()
is_touch_active = True
green_button_press_count = 0
blue_button_press_count = 0
last_green_button_press_time = time.time()
last_blue_press_time = time.time()

# Define horse name, session no, session type for data log- change for each horse/session
horse_name = "Horse = Freckle,"
session_no = "Session no = 1,"
start_tone_played = False

try:
    trial_number = 0

    while True:
        if green_button.is_pressed():
            green_button_press_count += 1
            if green_button_press_count == 1:
                # pause to avoid button double-press
                print(f"System is ready for {horse_name} {session_no} Session type {session_type} at: {datetime.now()}")
                play_WAV(systemIsReadyWav, 1)

            elif green_button_press_count == 2:
                # pause to avoid button double-press
                criterion_count = 0
                print(f"Session started for {horse_name} {session_no} Session type {session_type} at: {datetime.now()}")
                if session_type == "RP-A":
                    play_WAV(acquisitionSessionStartedWav, 1)
                elif session_type == "RP-H":
                    play_WAV(habitSessionStartedWav, 1)
                elif session_type == "RP-E":
                    play_WAV(extinctionSessionStartedWav, 1)
                elif session_type == "RP-R":
                    play_WAV(reinstatementSessionStartedWav, 1)
                else:
                    play_WAV(sessionTerminated, 1)
                pausable_sleep(0.5, False)

                while trial_number < trialLimit:
                    if session_type == "RP-E":
                        if criterion_count == criterionLimit:
                            play_WAV(criterionAchievedWav, 3)
                            print(f"Criterion reached at: {datetime.now()}")
                            sys.exit()

                    # begin next trial
                    trial_number += 1
                    print(f"Current trial: {trial_number}")
                    play_WAV(startToneWav, 1)
                    start_tone_played = True
                    start_tone_time = datetime.now()
                    print(f"Start tone played at: {start_tone_time}")

                    # waiting for either a touch or the blue button
                    while True:
                        start_tone_time = start_tone_time + listenForPause(False)

                        # elapsed = elapsed_seconds(start_tone_time)
                        # print(f"Session type {session_type} - elapsed {elapsed}")

                        # assess timeout
                        if session_type == "RP-H":
                            if elapsed_seconds(start_tone_time) > responseTimeout:
                                print(f"Habit formation incorrect response at {datetime.now()}")
                                play_WAV(incorrectToneWav, 1)
                                start_tone_time = start_tone_time + pausable_sleep(1, False)
                                break
                        elif session_type == "RP-E":
                            if elapsed_seconds(start_tone_time) > criterion_seconds:
                                criterion_count += 1
                                print(f"Criterion count {criterion_count}")
                                break

                        if blue_button.is_pressed():
                            # manual override
                            if start_tone_played == True:
                                is_touch_active = False
                                last_touch_time = datetime.now()
                                touch_count += 1
                                print(f"Manual touch recorded at: {last_touch_time}, Session under manual control")

                                # assess goal
                                if session_type == "RP-A" or session_type == "RP-R":
                                    if elapsed_seconds(start_tone_time) < criterion_seconds:
                                        criterion_count += 1
                                        print(f"Criterion count {criterion_count}")
                                    else:
                                        criterion_count = 0
                                        print("Criterion restart")
                                elif session_type == "RP-E":
                                    criterion_count = 0
                                    print("Criterion restart")
                                    start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, True)
                                    break

                                time.sleep(0.1)
                                play_WAV(correctToneWav, 1)
                                time.sleep(0.5)
                                if servo_mode == "pellets":
                                    feeder_pellets.dispense_feed_pellets()
                                else:
                                    feeder_grain.dispense_feed_grain()

                                if criterion_count == criterionLimit:
                                    play_WAV(criterionAchievedWav, 3)
                                    print(f"Criterion reached at: {datetime.now()}")
                                    sys.exit()

                                if touch_count == trialLimit:
                                    play_WAV(sessionTerminated, 3.5)
                                    print(f"Session ended at: {datetime.now()}")
                                    sys.exit()

                                start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, False)

                            # reset the tone for another touch
                            start_tone_played = False
                            break

                        # do this if the blue button has never been pressed
                        elif is_touch_active == True:
                            # touch-mode
                            status = touchSensor.read()

                            if status[1] > 0 or status[2] > 0 or status[3] > 0:
                                last_touch_time = datetime.now()
                                touch_count += 1
                                print(f"Touch-pad status read at: {last_touch_time}")
                                time.sleep(0.01)

                                if session_type == "RP-A" or session_type == "RP-R":
                                    if elapsed_seconds(start_tone_time) < criterion_seconds:
                                        criterion_count += 1
                                        print(f"Criterion count {criterion_count}")
                                    else:
                                        criterion_count = 0
                                        print("Criterion restart")
                                elif session_type == "RP-E":
                                    criterion_count = 0
                                    print("Criterion restart")
                                    start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, True)
                                    break

                                play_WAV(correctToneWav, 1)
                                time.sleep(0.5)
                                if servo_mode == "pellets":
                                    feeder_pellets.dispense_feed_pellets()
                                else:
                                    feeder_grain.dispense_feed_grain()

                                if criterion_count == criterionLimit:
                                    play_WAV(criterionAchievedWav, 3)
                                    print(f"Criterion achieved at: {datetime.now()}")
                                    sys.exit()

                                if touch_count == trialLimit:
                                    play_WAV(sessionTerminated, 3.5)
                                    print(f"Session ended at: {datetime.now()}")
                                    sys.exit()

                                start_tone_time = start_tone_time + pausable_sleep(trialSleepTime, False)
                                break

                if trial_number == trialLimit:
                    play_WAV(sessionTerminated, 3.5)
                    sys.exit()

except KeyboardInterrupt:
    GPIO.cleanup()
