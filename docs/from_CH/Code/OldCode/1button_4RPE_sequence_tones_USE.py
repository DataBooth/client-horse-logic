import time
from datetime import datetime # import the datetime module
from PiicoDev_Unified import sleep_ms
from PiicoDev_Switch import PiicoDev_Switch
#import sys
from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
import pygame

# Initialise the sensors
#touchSensor = PiicoDev_CAP1203(touchmode='single', sensitivity=6)
button = PiicoDev_Switch()

# Initialise the servo driver
servo_driver = PiicoDev_Servo_Driver()

# Initialise the servo
servo = PiicoDev_Servo(servo_driver, 1)  # Replace '1' with the appropriate channel for the servo

def play_WAV(file_path, duration):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.play()

    #wait for the specified duration (s)
    time.sleep(duration)

    # silence the tone
    sound.stop()

if __name__== "__main__":
    tone_paths = [
        "/home/horselogic/Documents/test audio project_data/Start tone _600.wav",
        "/home/horselogic/Documents/test audio project_data/Correct tone_1000.wav",
        "/home/horselogic/Documents/test audio project_data/End tone_1200.wav"
        ]

# Variables
sequence_count = 0  # Initialize the sequence count
press_count = 0 # use for manual button press

#define the number of sequences you want to run
num_sequences = 10

#Print session started at date/time
print(f"Session started at: {datetime.now()}")

#Main loop
while sequence_count <num_sequences:
    if button.was_pressed:
        press_count += 1

        if press_count == 1:
            #print the time the sequence starts
            print(f"Sequence {sequence_count + 1} started at : {datetime.now()}")
             #trigger playing of start tone

        if press_count == 2:
            play_WAV(tone_paths[0], 1)
            print(f"Start tone played at: {datetime.now()}")

        elif press_count == 3:
            #trigger playing of "correct" tone after touch
            play_WAV(tone_paths[1], 1)
            print(f"Correct response at: {datetime.now()}")

        elif press_count == 4:
            #Trigger mnaual playing of "correct tone" after touch
            #play_WAV(tone_paths[2],1) # play correct tone for 2 s
            #time.sleep(0.1)  # Delay operation of servo for 3 seconds
            print(f"Feed dispensed at: {datetime.now()}")

            # Control the servo motor
            servo.angle = 110  # Open servo 180 degrees
            time.sleep(0.5)  # Delay for 1 second for operation of servo
            servo.angle = 0  # Close servo

            # Reset the press count after the third press
            press_count = 0

            #increment the sequence count
            sequence_count += 1

            # Increment the sequence count
            #sequence_count += 1
            #print(f"Next sequence: {sequence_count + 1} at {datetime.now()}")

        # Add a small delay to debounce the button
        time.sleep(0.5)

        # Add a small delay to keep the loop from running too fast
        time.sleep(0.1)


# Play the end-of-session tone after completing the specified number of sequences
play_WAV(tone_paths[2], 3)
print(f"End of session at: {datetime.now()}")

#try:
    #sequence_number = 1  # Initialize the sequence number

    #while touch_count < 10:  # Adjust the number of touches as needed
         # Print the current sequence number
        #print(f"Current sequence: {sequence_number}")



        #play_WAV(tone_paths[0], 1)
        #print(f"Start tone played at: {datetime.now()}")

        #while True:
            # Check if sensor is touched
            #if is_touch_active:
               # status = touchSensor.read()

                #if status[1] > 0 or status[2] > 0 or status[3] > 0:
                   # print(f"Touch-pad status read at: {datetime.now()}")
                   #$ sleep_ms(100)

                #if status[1] > 0 or status[2] > 0 or status[3] > 0:
                    #play_WAV(tone_paths[1],1) # play correct tone for 2 s
                    #time.sleep(2) # play correct tone for 2s
                    #time.sleep(0.1)  # Delay operation of servo for 3 seconds

                    # Control the servo motor
                    #servo.angle = 110  # Open servo 180 degrees
                    #print(f"Feed dispensed at: {datetime.now()}")
                    #time.sleep(0.5)  # Delay for 1 second for operation of servo
                    #servo.angle = 0  # Close servo

                    #start_time = time.time()
                    #sleep_ms(20000)  # Delay for feed dispense and consumption

                    #touch_count += 1
                    #last_touch_time = time.time()

                    #if touch_count == 10:  # Change this number as required for the number of trials
                        #play_WAV(tone_paths[2],3)#play end of session tone for 3 s
                        #time.sleep(3) #play end of session tone for 3s)
                        #touch_count = 0  # Reset touch count after the session ends
                        #print (f"Session ended at: {datetime.now()}")
                        # Terminate the script
                        #sys.exit()

                    #break

        #sequence_number += 1  # Increment the sequence number

#except KeyboardInterrupt:
    #servo.release()  # Release the servo motor
