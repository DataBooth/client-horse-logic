# Python 3.11.4 (v3.11.4:d2340ef257, Jun  6 2023, 19:15:51) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin

import time

# from time import sleep  May not need this line
from PiicoDev_Switch import PiicoDev_Switch
from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
from PiicoDev_Buzzer import PiicoDev_Buzzer

# from PiicoDev_Unified import sleep_ms May not need this line

# Initialize the button and buzzer and servo
button = PiicoDev_Switch()
buzz = PiicoDev_Buzzer()
servo_driver = PiicoDev_Servo_Driver()

# Initialize the servo on the relay channel
servo_channel = 1  # Replace '1' with the appropriate channel for the servo
servo = PiicoDev_Servo(servo_driver, servo_channel)

# Customised setup - Attach a servo to channel 1 of the controller with the following properties:
#    - min_us: the minimum expected pulse length (microsecconds)
#    - max_us: the maximum expected pulse length (microsecconds)
#    - degrees: the angular range of the servo in degrees
# Uncomment the line below to use customised properties
servo = PiicoDev_Servo(servo_driver, 1, min_us=600, max_us=2400, degrees=270)

# old code that worked
# try:
# while True:
# if button.was_pressed:

# Control the servo motor
# servo.angle = 100  # Open servo 180 degrees
# time.sleep(1)  # Delay for 1 second for operation of servo
# servo.angle = 0  # Close servo

# try:
# while True:
# if button.was_pressed:
# Play the buzzer sound
# buzzer.tone(1000, 500)  # Start the buzzer tone for 500ms
# sleep_ms(500)  # Wait for 500ms before proceeding to next iteration
# else:
# Stop the buzzer if the button is not pressed
# buzzer.noTone()
# sleep_ms(100)  # Wait for 100ms before checking the button again

press_count = 0

while True:
    if button.was_pressed:
        press_count += 1

        if press_count == 1:
            # Trigger the buzzer on the first button press
            buzz.tone(1000, 2000)  # Start the start tone
            time.sleep(2)  # Delay for 2 seconds
            buzz.noTone()  # Stop the start tone
            print("Trial start!")
        # buzzer.play(300) # Adjust frequency as needed

        elif press_count == 2:
            # Trigger the buzzer on the secondf button press-correct response
            buzz.tone(800, 2000)  # Start the correct response tone
            time.sleep(2)  # Delay for 2 seconds
            buzz.noTone()  # Stop the start tone
            print("Correct response!")
        # buzzer.play(300) # Adjust frequency as neede

        elif press_count == 3:
            # Operate the servo motor on the third button press
            # Control the servo motor
            servo.angle = 180  # Open servo 180 degrees
            time.sleep(1)  # Delay for 1 second for operation of servo
            servo.angle = 0  # Close servo
            print("Reward dispensed!")

            # Reset the press count after the third press
            press_count = 0

        # Add a small delay to debounce the button
        time.sleep(0.5)

# except KeyboardInterrupt:
# Stop the buzzer and release the GPIO resources when the program is interrupted
# buzzer.noTone()

# except KeyboardInterrupt:
