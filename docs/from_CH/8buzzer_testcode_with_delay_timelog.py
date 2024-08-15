import time
from datetime import datetime  # Import the datetime module
from PiicoDev_CAP1203 import PiicoDev_CAP1203
from PiicoDev_Buzzer import PiicoDev_Buzzer
from PiicoDev_Unified import sleep_ms
import sys
from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver

# Initialise the sensors
buzz = PiicoDev_Buzzer()
touchSensor = PiicoDev_CAP1203(touchmode="single", sensitivity=5)

# Initialise the servo driver
servo_driver = PiicoDev_Servo_Driver()

# Initialise the servo
# Replace '1' with the appropriate channel for the servo

# Customised setup - Attach a servo to channel 1 of the controller with the following properties:
#    - min_us: the minimum expected pulse length (microseconds)
#    - max_us: the maximum expected pulse length (microseconds)
#    - degrees: the angular range of the servo in degrees
# Uncomment the line below to use customised properties

servo = PiicoDev_Servo(servo_driver, 1, min_us=600, max_us=2400, degrees=270)

# Variables
sequence_count = 0  # Initialize the sequence count
touch_count = 0
last_touch_time = time.time()
is_touch_active = True

# Initial delay before the first sequence (in seconds)
initial_delay = 10  # Adjust the delay time as needed

print(f"Waiting for {initial_delay} seconds before starting the first sequence...")
time.sleep(initial_delay)  # Add the initial delay


# Main loop
try:
    while sequence_count < 10:
        # Log the start time of the current sequence
        start_time = datetime.now()
        print(f"Sequence {sequence_count + 1} started at: {start_time}")

        # Play start tone
        buzz.tone(1000, 2000)  # Start the start tone
        time.sleep(2)  # Delay for 2 seconds
        buzz.noTone()  # Stop the start tone

        while True:
            # Check if sensor is touched
            if is_touch_active:
                status = touchSensor.read()
                print(f"Touch Pad Status: {status[1]}  {status[2]}  {status[3]}")
                sleep_ms(100)

                # Control the servo motor
                servo.angle = 180  # Open servo 180 degrees
                time.sleep(1)  # Delay for 1 second for operation of servo
                servo.angle = 0  # Close servo

                sleep_ms(42000)  # Delay for feed dispense and consumption

                # Step the servo-instructions from AngularServo_testcode
                # servo.angle = 0
                # sleep_ms(1000)
                # servo.angle = 90
                # sleep_ms(1000)
                # servo.angle = 180
                # sleep_ms(1000)
                # servo.angle = 0
                # sleep_ms(2000)
                start_time = time.time()

                touch_count += 1
                last_touch_time = time.time()

                if touch_count == 10:
                    # Change this number as required for the number of trials
                    # Make a different sound after 5 registered touches
                    buzz.tone(1200, 500)  # Start the different buzzer tone
                    time.sleep(0.5)
                    buzz.noTone()  # Stop the different buzzer tone
                    touch_count = 0  # Reset touch count after the session ends

                    # Log the end time of the current sequence
                    end_time = datetime.now()
                    print(f"Sequence {sequence_count + 1} ended at: {end_time}")

                    sequence_count += 1  # Increment the sequence count

                    if sequence_count == 10:  # If all sequences are done
                        # Exit the loop to end the program naturally
                        break

                    break

except KeyboardInterrupt:
    buzz.noTone()  # Stop the buzzer if program is interrupted
    servo.release()  # Release the servo motor
    sys.exit()
