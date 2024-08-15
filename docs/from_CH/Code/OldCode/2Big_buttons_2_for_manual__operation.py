import time
from datetime import datetime # import the datetime module
from PiicoDev_CAP1203 import PiicoDev_CAP1203
import RPi.GPIO as GPIO # NOTE new import
from PiicoDev_Unified import sleep_ms
import sys
from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
import pygame

# Initialise the sensors
#buzz = PiicoDev_Buzzer()
touchSensor = PiicoDev_CAP1203(touchmode='single', sensitivity=5)

# Initialise the servo driver
servo_driver = PiicoDev_Servo_Driver()

# Initialise the servo
servo = PiicoDev_Servo(servo_driver, 1)  # Replace '1' with the appropriate channel for the servo
from datetime import datetime
import time

#Note NEW-servo objects x 2 for different types of feed.
class Servo_pellets:
    def __init__(self, servo):
        self.servo = servo

    def dispense_feed_pellets(self):
        self.servo.angle = 80  # Open servo 80 degrees
        print(f"Feed dispensed at: {datetime.now()}")
        time.sleep(0.5)  # Delay in seconds for the operation of the servo
        self.servo.angle = 0  # Close servo

class Servo_grain:
    def __init__(self, servo):
        self.servo = servo

    def dispense_feed_grain(self):
        self.servo.angle = 70  # Open servo 70 degrees
        print(f"Feed dispensed at: {datetime.now()}")
        time.sleep(0.5)  # Delay in seconds for the operation of the servo
        self.servo.angle = 0  # Close servo

# NOTE new=Create an instance of Servo_grain and Servo_pellets
feeder_grain = Servo_grain(servo)
feeder_pellets = Servo_pellets(servo)

# Dispense feed using the object
#feeder_grain.dispense_feed_grain()
#feeder_pellets.dispense_feed_pellets()

# NOTE new=Set the GPIO mode and pin
GPIO.setmode(GPIO.BCM)
butpin_gr = 6  # BCM GPIO 6 or D6 on adapter (Green button)
butpin_bl = 7  # BCM GPIO 7 or D7 on adapter (Blue button)
butpin_rd = 12 #BCM GPIO 12 or D12 on adatper (Red button)

# NOTE new=Set up the GPIO pin for input with an internal pull-up resistor
GPIO.setup(butpin_gr, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(butpin_bl, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(butpin_rd, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def play_WAV(file_path, duration):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.play()

    pygame.time.delay(int(duration * 1000))  # Convert seconds to milliseconds

    #wait for the specified duration (s)
    time.sleep(duration)

    # silence the tone
    sound.stop()

#NOTE new=Wav file paths- delete old paths
systemIsReadyWav = "/home/horselogic/Documents/test audio project_data/System_is_ready1.wav"
sessionStartedWav = "/home/horselogic/Documents/test audio project_data/Session_started1.wav"
trialPausedWav = "/home/horselogic/Documents/test audio project_data/Trial paused1.wav"
trialRestartedWav = "/home/horselogic/Documents/test audio project_data/Trial restarted1.wav"
sessionTerminated = "/home/horselogic/Documents/test audio project_data/Session stopped1.wav"
startToneWav = "/home/horselogic/Documents/test audio project_data/Start tone _600.wav"
correctToneWav = "/home/horselogic/Documents/test audio project_data/Correct tone_1000.wav"
endToneWav = "/home/horselogic/Documents/test audio project_data/End tone_1200.wav"

# Variables
trial_count = 0  # Initialize the trial count
touch_count = 0
last_touch_time = time.time()
is_touch_active = True
butpin_gr_press_count = 0 # NOTE new=use for manual presses of green button
butpin_rd_press_count = 0 # NOTE new=use for manual presses of red button

#Define horse name, session no, session type for ID of data log
horse_name = "Horse = Freckle," #change  name as needed
session_no = "Session no = 1," #change integer as needed
session_type = "= RPE-A" # choose one of RPE-A, RPE-E, RPE-R

try:

    trial_number = 1  # Initialize the trial number

    while True:

        if GPIO.input(butpin_gr) == GPIO.LOW: # Check if the button is pressed (input pulled low due to the internal pull-up)
            #if not paused:
            butpin_gr_press_count += 1
            if butpin_gr_press_count == 1:
                print(f"System is ready for {horse_name} {session_no} Session type {session_type}  at: {datetime.now()}")
                #play_WAV(systemIsReadyWav, 2) #play system is ready1 WAV
                time.sleep(0.5)

            elif butpin_gr_press_count == 2:
                print(f"Session started for {horse_name} {session_no} Session type {session_type}  at: {datetime.now()}")
                #play_WAV(sessionStartedWav, 2) #play system is ready1 WAV

                time.sleep(2) #delay before generation of start tone

                # Check if butPin_bl is pressed to disable the touch sensor
                if GPIO.input(butpin_bl) == GPIO.LOW:
                    touch_active = False
                    print("Touch sensor disabled, trial manually controlled")

except KeyboardInterrupt:
    GPIO.cleanup() #clean up GPIO pins
    servo.release()  # Release the servo motor
