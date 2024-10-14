import time
import pigpio
from PiicoDev_CAP1203 import PiicoDev_CAP1203
from PiicoDev_Buzzer import PiicoDev_Buzzer
from PiicoDev_Unified import sleep_ms
import sys
import os

# Start the pigpio daemon
os.system("sudo pigpiod")

# Initialise the sensors
buzz = PiicoDev_Buzzer()
touchSensor = PiicoDev_CAP1203(touchmode="single", sensitivity=6)

# Variables
touch_count = 0
last_touch_time = time.time()
is_touch_active = True

# Connect to the local Pi GPIO
pi = pigpio.pi()
# GPIO pin for the servo
servo_pin = 18

# Minimum and maximum pulse widths for servo
servo_min = 500  # Minimum pulse width for the servo
servo_max = 2500  # Maximum pulse width for the servo

# create a servo object
servo = pi.set_servo_pulsewidth(servo_pin, 0)

# Main loop
try:
    while touch_count < 5:
        # Play start tone
        buzz.tone(1000, 2000)  # Start the start tone
        time.sleep(2)  # Delay for 2 seconds
        buzz.noTone()  # Stop the start tone

        while True:
            # Check if sensor is touched
            if is_touch_active:
                status = touchSensor.read()
                print("Touch Pad Status: " + str(status[1]) + "  " + str(status[2]) + "  " + str(status[3]))
                sleep_ms(100)

                if status[1] > 0 or status[2] > 0 or status[3] > 0:
                    # Make the buzzer sound for a maximum of 2 seconds
                    buzz.tone(800, 2000)  # Start the buzzer tone
                    time.sleep(3)  # Delay for 3 seconds

                    # Control the servo motor
                    pi.set_servo_pulsewidth(servo_pin, servo_max)  # Move servo to 90 degree position
                    time.sleep(1)  # Delay for 1 second for operation of servo
                    pi.set_servo_pulsewidth(servo_pin, servo_min)  # Move servo position back to start

                    start_time = time.time()
                    sleep_ms(5000)  # delay for dispense and consumption of feed- adjust after prootyping with horses

                    touch_count += 1
                    last_touch_time = time.time()

                    if touch_count == 5:  # Change this number as required for the number of trials
                        # Make a different sound after 5 registered touches
                        buzz.tone(1200, 500)  # Start the different buzzer tone
                        time.sleep(0.5)
                        buzz.noTone()  # Stop the different buzzer tone
                        touch_count = 0  # Reset touch count after the session ends

                        # Terminate the script
                        sys.exit()

                    break

except KeyboardInterrupt:
    buzz.noTone()  # Stop the buzzer if program is interrupted
    pi.set_servo_pulsewidth(servo_pin, 0)  # Move the servo to the stop position
    pi.stop()  # Release the servo motor control
