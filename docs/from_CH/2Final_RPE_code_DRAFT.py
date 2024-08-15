import time
from datetime import datetime
from PiicoDev_CAP1203 import PiicoDev_CAP1203
import RPi.GPIO as GPIO
import sys
from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
import pygame

# Initialize the sensors
touchSensor = PiicoDev_CAP1203(touchmode="single", sensitivity=5)

# Initialize the servo driver
servo_driver = PiicoDev_Servo_Driver()

# Initialize the servo
servo = PiicoDev_Servo(servo_driver, 1)

# Define mode of operation - test or live
trialLimit = 5  # change number of trials as needed
trialSleepTime = 5  # feed dispense
mode = "test"
if mode == "test":  # replace 'test' with alternative text for using without the short trial limits
    trialLimit = 3
    trialSleepTime = 1

servo_mode = "pellets"  # comment out option that isn't needed depending on the feed being used
# servo_mode = 'grain'


# Define Servo objects for different types of feed
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


# NOTE new=Wav file paths- delete old paths
systemIsReadyWav = "/home/horselogic/Documents/test audio project_data/System_is_ready1.wav"
sessionStartedWav = "/home/horselogic/Documents/test audio project_data/Session_started1.wav"
trialPausedWav = "/home/horselogic/Documents/test audio project_data/Trial paused1.wav"
trialResumedWav = "/home/horselogic/Documents/test audio project_data/Trial restarted1.wav"
sessionTerminated = "/home/horselogic/Documents/test audio project_data/Session stopped1.wav"
startToneWav = "/home/horselogic/Documents/test audio project_data/Start tone _600.wav"
correctToneWav = "/home/horselogic/Documents/test audio project_data/Correct tone_1000.wav"
endToneWav = "/home/horselogic/Documents/test audio project_data/End tone_1200.wav"

# Initialize variables
trial_count = 0
touch_count = 0
last_touch_time = time.time()
is_touch_active = True
green_button_press_count = 0
blue_button_press_count = 0
last_green_button_press_time = time.time()
last_blue_press_time = time.time()

# Define horse name, session no, session type for data log
horse_name = "Horse = Freckle,"
session_no = "Session no = 1,"
session_type = "= RPE-A"
start_tone_played = False

try:
    trial_number = 1
    print(f"started Current trial: {trial_number}")

    while True:
        if green_button.is_pressed():
            green_button_press_count += 1
            if green_button_press_count == 1:
                print(f"System is ready for {horse_name} {session_no} Session type {session_type} at: {datetime.now()}")
                play_WAV(systemIsReadyWav, 2)  # play system is ready1 WAV
                time.sleep(2)

            elif green_button_press_count == 2:
                print(f"Session started for {horse_name} {session_no} Session type {session_type} at: {datetime.now()}")
                play_WAV(sessionStartedWav, 2)  # play session started WAV
                time.sleep(2)

                while touch_count < trialLimit:
                    print(f"Current trial: {trial_number}")
                    play_WAV(startToneWav, 1)
                    start_tone_played = True
                    print(f"Start tone played at: {datetime.now()}")

                    # waiting for either a touch or the blue button
                    while True:
                        if red_button.is_pressed():
                            # Pause trial
                            print(f"Trial paused at: {datetime.now()}, Session paused")
                            play_WAV(trialPausedWav, 2)  # play trial paused WAV
                            time.sleep(0.5)
                            while True:
                                if red_button.is_pressed():
                                    print(f"Trial resumed at: {datetime.now()}, Session resumed")
                                    play_WAV(trialResumedWav)  # play trial resumed WAV
                                    time.sleep(0.5)
                                    break

                        if blue_button.is_pressed():
                            # manual override
                            if start_tone_played == True:
                                is_touch_active = False
                                print(f"Manual touch recorded at: {datetime.now()}, Session under manual control")
                                last_touch_time = time.time()
                                touch_count += 1

                                time.sleep(0.1)
                                play_WAV(correctToneWav, 1)
                                time.sleep(0.5)
                                if servo_mode == "pellets":
                                    feeder_pellets.dispense_feed_pellets()
                                else:
                                    feeder_grain.dispense_feed_grain()

                                if touch_count == trialLimit:
                                    play_WAV(endToneWav, 3)
                                    print(f"Session ended at: {datetime.now()}")
                                    sys.exit()

                                time.sleep()

                                # pause until manual start
                                while True:
                                    if blue_button.is_pressed():
                                        break

                            # reset the tone for another touch
                            start_tone_played = False
                            break

                        # do this if the blue button has never been pressed
                        elif is_touch_active == True:
                            # touch-mode
                            status = touchSensor.read()

                            if status[1] > 0 or status[2] > 0 or status[3] > 0:
                                last_touch_time = time.time()
                                touch_count += 1

                                print(f"Touch-pad status read at: {datetime.now()}")
                                time.sleep(0.01)

                                play_WAV(correctToneWav, 1)
                                time.sleep(0.5)
                                if servo_mode == "pellets":
                                    feeder_pellets.dispense_feed_pellets()
                                else:
                                    feeder_grain.dispense_feed_grain()

                                if touch_count == trialLimit:
                                    play_WAV(endToneWav, 3)
                                    print(f"Session ended at: {datetime.now()}")
                                    sys.exit()

                                time.sleep(trialSleepTime)
                                break

                    trial_number += 1

except KeyboardInterrupt:
    GPIO.cleanup()
    servo.release()
