# created by chatGPT from Cath (see docs/from_cath/ChatGPT advice-code for squence.docx)

# HARDWARE

# ## Question:

# List all components required to connect raspberry pi 4, PIEZO BUZZER, PIICODEV CAPACITIVE TOUCH SENSOR,
# DF METAL GEARED 15KG STANDARD SERVO 270° at the same time

# ## Answer

# To connect the Raspberry Pi 4 with the listed components (Piezo Buzzer, PiiCodev Capacitive Touch Sensor,
# DF Metal Geared 15KG Standard Servo 270°) simultaneously, you will need the following components:

# 1. Raspberry Pi 4 (any model)
# 2. Piezo Buzzer
# 3. PiiCodev Capacitive Touch Sensor
# 4. DF Metal Geared 15KG Standard Servo 270°
# 5. Jumper wires (Male-to-Female, Male-to-Male) for connecting the components
# 6. Breadboard (optional, for easy prototyping and connecting the components)

# Here's a high-level overview of how you can connect these components to the Raspberry Pi 4:

# 1. Connect the Piezo Buzzer:
# - Connect one leg of the buzzer to a GPIO pin on the Raspberry Pi (e.g., GPIO pin 17).
# - Connect the other leg of the buzzer to a ground (GND) pin on the Raspberry Pi.

# 2. Connect the PiiCodev Capacitive Touch Sensor:
# - Connect the VCC pin of the touch sensor to a 3.3V power pin on the Raspberry Pi.
# - Connect the GND pin of the touch sensor to a ground (GND) pin on the Raspberry Pi.
# - Connect the SIG pin of the touch sensor to a GPIO pin on the Raspberry Pi (e.g., GPIO pin 27).

# 3. Connect the DF Metal Geared 15KG Standard Servo 270°:
# - Connect the power (VCC) wire of the servo motor to a 5V power pin on the Raspberry Pi.
# - Connect the ground (GND) wire of the servo motor to a ground (GND) pin on the Raspberry Pi.
# - Connect the signal (SIG) wire of the servo motor to a GPIO pin on the Raspberry Pi (e.g., GPIO pin 18).

# Make sure to refer to the datasheets or documentation of each component for the specific pinouts
# and electrical requirements. Additionally, exercise caution when connecting
# and powering the components to avoid damaging them or the Raspberry Pi.

# SOFTWARE

# ## Question:

# How to program this sequence in Python:

# - Event 1: Start tone PEIZO BUZZER tone 1 - (1 sec duration)
# - Event 2: Activation of PIICODEV CAPACITIVE TOUCH SENSOR (nose press on panel)
# - Event 3: Correct response tone PEIZO BUZZER tone 2 (different from start tone) - 0.5 sec duration
# - Event 4: Wait period-2-3 sec
# - Event 5: Activation of DF GEARED 15KG STANDARD SERVO 270°-dispense feed (50gm per trial)
# - Event 6: Time out (set period 10-15s for feed consumption)
# - TODO: No Event 7? (number doesn't match in the answer below)
# - Event 8: Reset for new trial using the listed components: raspberry pi 4, PIEZO BUZZER, PIICODEV CAPACITIVE TOUCH SENSOR, DF METAL GEARED 15KG STANDARD SERVO 270°

# ## Answer

# To program the sequence using the listed components in Python, you can utilize the RPi.GPIO library for
# Raspberry Pi GPIO control and the pigpio library for controlling the servo motor.
# Here's an example code that implements the sequence you described:


import time

import pigpio
import RPi.GPIO as GPIO

# Pin numbers for the components

START_TONE_PIN = 17  # GPIO pin for the start tone (buzzer)
TOUCH_SENSOR_PIN = 27  # GPIO pin for the touch sensor
RESPONSE_TONE_PIN = 22  # GPIO pin for the response tone (buzzer)
SERVO_PIN = 18  # GPIO pin for the servo motor

# Setup GPIO mode and pin configurations

GPIO.setmode(GPIO.BCM)
GPIO.setup(START_TONE_PIN, GPIO.OUT)
GPIO.setup(TOUCH_SENSOR_PIN, GPIO.IN)
GPIO.setup(RESPONSE_TONE_PIN, GPIO.OUT)

# Create pigpio instance for controlling the servo motor

pi = pigpio.pi()

SERVO_PWM_PIN = 12  # Servo control pin
SERVO_PWM_FREQUENCY = 50  # PWM frequency for the servo motor

pi.set_PWM_frequency(SERVO_PWM_PIN, SERVO_PWM_FREQUENCY)

# Event 1: Start tone - 1 sec duration

GPIO.output(START_TONE_PIN, GPIO.HIGH)
time.sleep(1)
GPIO.output(START_TONE_PIN, GPIO.LOW)

# Event 2: Activation of touch sensor (nose press on panel)

while GPIO.input(TOUCH_SENSOR_PIN) == GPIO.LOW:
    time.sleep(0.1)

# Event 3: Correct response tone - 0.5 sec duration

GPIO.output(RESPONSE_TONE_PIN, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(RESPONSE_TONE_PIN, GPIO.LOW)

# Event 5: Wait period - 2-3 sec

time.sleep(2)

# Event 6: Activation of servo motor - dispense feed (50gm per trial)

SERVO_PWM_DUTY_CYCLE = 1500  # Adjust the duty cycle for desired servo position
pi.set_servo_pulsewidth(SERVO_PWM_PIN, SERVO_PWM_DUTY_CYCLE)
time.sleep(1)  # Adjust the time for the servo motor to reach the desired position

# Event 7: Time out - set period 10-15s for feed consumption

time.sleep(10)  # Adjust the time as needed for the desired feed consumption duration

# Event 8: Reset for new trial

pi.set_servo_pulsewidth(SERVO_PWM_PIN, 0)  # Stop the servo motor
GPIO.cleanup()  # Clean up GPIO pins
pi.stop()  # Release pigpio resources


# Make sure to connect the components to the correct GPIO pins on the Raspberry Pi board.
# Adjust the pin numbers if necessary.
# The code sets up the GPIO mode, configures the pins, and then executes the sequence by controlling
# the GPIO outputs and waiting for inputs or delays.

# Note: This code assumes that you have the necessary libraries installed, such as `RPi.GPIO` and `pigpio`.
# You can install them using `pip install RPi.GPIO pigpio`.ll them using `pip install RPi.GPIO pigpio`.
