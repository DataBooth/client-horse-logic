import time
from datetime import datetime
from PiicoDev_CAP1203 import PiicoDev_CAP1203
import RPi.GPIO as GPIO
import sys
from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
import pygame

# Initialize the sensors
touchSensor = PiicoDev_CAP1203(touchmode='single', sensitivity=5)

# Initialize the servo driver
servo_driver = PiicoDev_Servo_Driver()

# Initialize the servo
servo = PiicoDev_Servo(servo_driver, 1)

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

green_button_press_count = 0
blue_button_press_count = 0

while True:
    if green_button.is_pressed():
        green_button_press_count += 1
        if green_button_press_count == 1:
            print(f"System is ready")
            time.sleep(2)

        elif green_button_press_count == 2:
            print(f"Session started ")
            time.sleep(2)
