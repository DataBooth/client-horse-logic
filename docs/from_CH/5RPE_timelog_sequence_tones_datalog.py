import sys
import time
import pygame

from datetime import datetime

from PiicoDev_Buzzer import PiicoDev_Buzzer
from PiicoDev_CAP1203 import PiicoDev_CAP1203
from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
from PiicoDev_Unified import sleep_ms

# initialise the name of the log file
log_file_name = "/home/horselogic/Documents/test_data_log"

# Open the log file in append mode
with open(log_file_name, "a") as log:
    event_description1 = "Sequence started"
    timestamp1 = datetime.now()
    log_entry1 = f"{event_description1} at {timestamp1}\n"
    log.write(log_entry1)

    event_description2 = "Start tone played"
    timestamp2 = datetime.now()
    log_entry2 = f"{event_description2} at {timestamp2}\n"
    log.write(log_entry2)

    event_description3 = "Correct response"
    timestamp3 = datetime.now()
    log_entry3 = f"{event_description3} at {timestamp3}\n"
    log.write(log_entry3)

    event_description4 = "Feed dispensed"
    timestamp4 = datetime.now()
    log_entry4 = f"{event_description3} at {timestamp3}\n"
    log.write(log_entry4)


# Initialise the sensors
# buzz = PiicoDev_Buzzer()
touchSensor = PiicoDev_CAP1203(touchmode="single", sensitivity=1)

# Initialise the servo driver
servo_driver = PiicoDev_Servo_Driver()

# Initialise the servo
servo = PiicoDev_Servo(servo_driver, 1)  # Replace '1' with the appropriate channel for the servo

# servo = PiicoDev_Servo(servo_driver, 1, min_us=600, max_us=2400, degrees=270)


def play_WAV(file_path, duration):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.play()

    # wait for the specified duration (s)
    time.sleep(duration)

    # silence the tone
    sound.stop()


if __name__ == "__main__":
    tone_paths = [
        "/home/horselogic/Documents/test audio project_data/Start tone _600.wav",
        "/home/horselogic/Documents/test audio project_data/Correct tone_1000.wav",
        "/home/horselogic/Documents/test audio project_data/End tone_1200.wav",
    ]

# Variables
sequence_count = 0  # Initialize the sequence count
touch_count = 0
last_touch_time = time.time()
is_touch_active = True

# Print session started at date/time
print(f"Session started at: {datetime.now()}")

# Initial delay before the first sequence (in seconds)
initial_delay = 2  # Adjust the delay time as needed in seconds

print(f"Waiting for {initial_delay} seconds before starting the first sequence...")
time.sleep(initial_delay)  # Add the initial delay

# Main loop

try:
    sequence_number = 1  # Initialize the sequence number

    while touch_count < 3:  # Adjust the number of touches as needed
        # Print the current sequence number
        print(f"Current sequence: {sequence_number}")

        # play start tone for 2 s
        play_WAV(tone_paths[0], 2)
        print(f"Start tone played at: {datetime.now()}")

        # Log the event description and timestamp for the start of the sequence
        event_description1 = "Start tone played"
        timestamp1 = datetime.now()
        log_entry1 = f"{event_description1} at {timestamp1}\n"
        log.write(log_entry1)

        while True:
            # Check if sensor is touched
            if is_touch_active:
                status = touchSensor.read()

                if status[1] > 0 or status[2] > 0 or status[3] > 0:
                    print(f"Touch-pad status read at: {datetime.now()}")
                    sleep_ms(100)

                    # Log the event description and timestamp for the touch event
                    event_description2 = "Correct response"
                    timestamp2 = datetime.now()
                    log_entry2 = f"{event_description2} at {timestamp2}\n"
                    log.write(log_entry2)

                if status[1] > 0 or status[2] > 0 or status[3] > 0:
                    # Make the buzzer sound for a maximum of 2 seconds
                    # buzz.tone(800, 2000)  # Start the buzzer tone
                    play_WAV(tone_paths[1], 2)  # play correct tone for 2 s
                    # time.sleep(2) # play correct tone for 2s
                    time.sleep(2)  # Delay operation of servo for 3 seconds

                    # Control the servo motor
                    servo.angle = 180  # Open servo 180 degrees
                    print(f"rReward dispensed at: {datetime.now()}")
                    time.sleep(0.7)  # Delay for 1 second for operation of servo
                    servo.angle = 0  # Close servo

                    event_description3 = "Reward dispensed"
                    timestamp3 = datetime.now()
                    log_entry3 = f"{event_description3} at {timestamp3}\n"
                    log.write(log_entry3)

                    start_time = time.time()
                    sleep_ms(2000)  # Delay for feed dispense and consumption

                    touch_count += 1
                    last_touch_time = time.time()

                    if touch_count == 3:  # Change this number as required for the number of trials
                        # Make a different sound after n registered touches
                        # buzz.tone(1200, 500)  # Start the different buzzer tone
                        # time.sleep(0.5)
                        # buzz.noTone()  # Stop the different buzzer tone
                        play_WAV(tone_paths[2], 3)  # play end of session tone for 3 s
                        # time.sleep(3) #play end of session tone for 3s)
                        touch_count = 0  # Reset touch count after the session ends
                        print(f"Session ended at: {datetime.now()}")
                        # Terminate the script

                        # Log the event description and timestamp for the end of the session
                        event_description4 = "Session ended"
                        timestamp4 = datetime.now()
                        log_entry4 = f"{event_description4} at {timestamp4}\n"
                        log.write(log_entry4)
                        sys.exit()

                    break

        sequence_number += 1  # Increment the sequence number

except KeyboardInterrupt:
    log.close()
    buzz.noTone()  # Stop the buzzer if the program is interrupted
    servo.release()  # Release the servo motor

# Close the log file when the program finished
log.close()
