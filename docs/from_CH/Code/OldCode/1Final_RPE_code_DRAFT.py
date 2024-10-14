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

class Button:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self):
        return GPIO.input(self.pin) == GPIO.LOW

# Create button instances
green_button = Button(butpin_gr)
blue_button = Button(butpin_bl)
red_button = Button(butpin_rd)

#With this setup, you can check the state of the buttons using the is_pressed() method:
#if green_button.is_pressed():
    # Green button is pressed, perform corresponding action
#if blue_button.is_pressed():
    # Blue button is pressed, perform corresponding action
#if red_button.is_pressed():
    # Red button is pressed, perform corresponding action

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
green_buuton_press_count = 0 # NOTE new=use for manual presses of green button
blue_button_press_count = 0 # NOTE new=use for manual presses of red button
last_green_button_press_time = time.time()
last_blue_press_time = time.time()

#Define horse name, session no, session type for ID of data log
horse_name = "Horse = Freckle," #change  name as needed
session_no = "Session no = 1," #change integer as needed
session_type = "= RPE-A" # choose one of RPE-A, RPE-E, RPE-R

try:

    trial_number = 1  # Initialize the trial number

    while True:

        if green_button.is_pressed(): # Check if the button is pressed (input pulled low due to the internal pull-up)
            green_button_press_count += 1
            if green_button_press_count == 1:
                print(f"System is ready for {horse_name} {session_no} Session type {session_type}  at: {datetime.now()}")
                #play_WAV(systemIsReadyWav, 2) #play system is ready1 WAV

                time.sleep(2) #delay before next button press is registered

            elif green_button_press_count == 2:
                print(f"Session started for {horse_name} {session_no} Session type {session_type}  at: {datetime.now()}")
                #play_WAV(sessionStartedWav, 2) #play system is ready1 WAV

                time.sleep(2) #delay before generation of start tone

                while touch_count < 5:  # Adjust the number of touches as needed
                    # Print the current trial number
                    print(f"Current trial: {trial_number}")

                    play_WAV(startToneWav,1) #play start tone tone for n sec
                    print(f"Start tone played at: {datetime.now()}")

                    while True:

                    # Check if butPin_bl is pressed to disable the touch sensor
                        if blue_button.is_pressed():
                            touch_active = False
                            print(f"Manual touch recorded at: {datetime.now()}, Session under manual control")
                            time.sleep(0.1)
                            play_WAV(correctToneWav,1) # play correct tone for 2 s

                            time.sleep(0.5)  # Delay operation of servo

                            #NOTE new: operate servo-comment out for correct feed type
                            feeder_grain.dispense_feed_grain()
                            #feeder_pellets.dispense_feed_pellets()

                            start_time = time.time()
                            time.sleep(2)  # Delay for feed dispense and consumption

                             # Add the following code to handle butPin_bl button presses

                            # You can add a loop here to wait for the next button press
                            while blue_button_press_count < 2:
                                if blue_button.is_pressed():
                                    blue_button_press_count += 1
                                    if blue_button_press_count == 2:
                                        play_WAV(correctToneWav,1) # play correct tone for 2 s
                                        time.sleep(0.5)  # Delay operation of servo
                                        #NOTE new: operate servo-comment out for correct feed type
                                        feeder_grain.dispense_feed_grain()
                                        #feeder_pellets.dispense_feed_pellets()

                            start_time = time.time()
                            time.sleep(5)  # Delay for feed dispense and consumption

        trial_number += 1  # Increment the trial number

        blue_button_press_count += 1
        last_blue_button_time = time.time()

        if blue_button_press_count == 5:  # Change this number as required for the number of trials
            play_WAV(endToneWav,3)#play end of session tone for 3 s
            butpin_bl_press_count = 0  # Reset touch count after the session ends
            print (f"Session ended at: {datetime.now()}")
            # Terminate the script
            sys.exit()

        # Check if sensor is touched
            if is_touch_active:
                status = touchSensor.read()

            if status[1] > 0 or status[2] > 0 or status[3] > 0:
                print(f"Touch-pad status read at: {datetime.now()}")
                time.sleep(0.01)

            if status[1] > 0 or status[2] > 0 or status[3] > 0:
                play_WAV(correctToneWav,1) # play correct tone for 2 s

                time.sleep(0.5)  # Delay operation of servo

                #NOTE new: operate servo-comment out for correct feed type
                feeder_grain.dispense_feed_grain()
                #feeder_pellets.dispense_feed_pellets()

                start_time = time.time()
                time.sleep(5)  # Delay for feed dispense and consumption

                touch_count += 1
                last_touch_time = time.time()

                if touch_count == 5:  # Change this number as required for the number of trials
                    play_WAV(endToneWav,3)#play end of session tone for 3 s
                    #time.sleep(3) #play end of session tone for 3s)
                    touch_count = 0  # Reset touch count after the session ends
                    print (f"Session ended at: {datetime.now()}")
                    # Terminate the script
                    sys.exit()

        break

        trial_number += 1  # Increment the trial number

except KeyboardInterrupt:
    GPIO.cleanup() #clean up GPIO pins
    servo.release()  # Release the servo motor
