import pygame
import random

import pyfirmata
import time

contents = []
contents.append(["Trial", "\tSide", "\tCorrect", "\tCorrections", "\tLatency"])

board = pyfirmata.Arduino("/dev/ttyACM0")
led = board.get_pin("d:10:o")
pin = board.get_pin("a:1:i")


def set_up_sensor():
    iterator = pyfirmata.util.Iterator(board)
    iterator.start()

    pin.mode = pyfirmata.INPUT
    pin.enable_reporting()


def switch_arduino_on():  # turns on the red LED on Arduino board for 1 second
    led.write(1)
    time.sleep(1)
    led.write(0)


WIDTH = 1850
HEIGHT = 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # ,  pygame.FULLSCREEN
pygame.display.set_caption("Cognitive Test - Two Choice Discrimination Task")

WHITE = (255, 255, 255)

FPS = 60

correct_image = pygame.image.load("correct.jpg")
correct_image_scaled = pygame.transform.scale(correct_image, (875, 650))

wrong_image = pygame.image.load("wrong.jpg")
wrong_image_scaled = pygame.transform.scale(wrong_image, (875, 650))


def draw_window(left_image, right_image):
    WIN.fill(WHITE)
    WIN.blit(left_image, (30, 150))
    WIN.blit(right_image, (950, 150))
    pygame.display.update()


def generate_stimuli():
    # cross reference with the trail number so it knows which part of the array to check - display correct image on the left if stimuli_left[trial] == 1
    rm = [
        [1, 1, 0, 1, 1, 0, 0, 1, 0, 0],
        [1, 0, 1, 0, 1, 1, 0, 0, 1, 0],
        [1, 0, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 0, 1, 0, 1, 1, 0, 0, 1, 1],
        [0, 0, 1, 1, 0, 1, 0, 1, 1, 0],
        [0, 1, 1, 0, 0, 1, 0, 1, 1, 0],
        [0, 1, 0, 1, 1, 0, 0, 1, 0, 1],
        [0, 1, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 1, 0, 1, 0, 1, 0],
        [1, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    ]

    stimuli_left = random.choice(rm)
    return stimuli_left


def main():
    set_up_sensor()

    # reading when object is detected = { 0.1574, 0.1584  }
    # reading when object undetected = 0.2 - 03

    object_undetected = True
    while object_undetected:
        value = pin.read()
        if value == 0.1574 or value == 0.1584:
            object_undetected = False
            latency_start_time = time.time()
        time.sleep(0.1)

    trial = 0
    corrections = 0
    stimuli = generate_stimuli()
    print(stimuli)
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        if stimuli[trial] == 1:  # display correct image on left side
            draw_window(correct_image_scaled, wrong_image_scaled)
        else:  # display wrong image on left side
            draw_window(wrong_image_scaled, correct_image_scaled)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if ((x >= 32) and (x <= 905)) and ((y >= 155) and (y <= 800)):
                    # left image clicked
                    if stimuli[trial] == 1:  # image on the left is correct => CORRECT CHOICE
                        current_time = time.time()
                        latency_time = current_time - latency_start_time
                        contents.append(
                            [str(trial + 1), "\tLeft", "\tYes", "\t" + str(corrections), "\t\t" + str(latency_time)]
                        )
                        trial += 1
                        corrections = 0
                        switch_arduino_on()
                    else:  # image on the left is wrong => INCORRECT CHOICE
                        current_time = time.time()
                        latency_time = current_time - latency_start_time
                        contents.append(
                            [str(trial + 1), "\tLeft", "\tNo", "\t" + str(corrections), "\t\t" + str(latency_time)]
                        )
                        if corrections < 7:
                            corrections += 1
                        else:
                            trial += 1
                            corrections = 0
                elif ((x >= 952) and (x <= 1825)) and ((y >= 155) and (y <= 800)):
                    # right image clicked
                    if stimuli[trial] == 0:  # image on the right is correct => CORRECT CHOICE
                        current_time = time.time()
                        latency_time = current_time - latency_start_time
                        contents.append(
                            [str(trial + 1), "\tRight", "\tYes", "\t" + str(corrections), "\t\t" + str(latency_time)]
                        )
                        trial += 1
                        corrections = 0
                        switch_arduino_on()
                    else:  # image on the right is wrong => INCORRECT CHOICE
                        current_time = time.time()
                        latency_time = current_time - latency_start_time
                        contents.append(
                            [str(trial + 1), "\tRight", "\tNo", "\t" + str(corrections), "\t\t" + str(latency_time)]
                        )
                        if corrections < 7:
                            corrections += 1
                        else:
                            trial += 1
                            corrections = 0
        if trial == 10:
            run = False

    pygame.quit()

    with open("two_choice_correction.txt", "w") as f:
        for content in contents:
            f.writelines(content)
            f.write("\n")


if __name__ == "__main__":
    main()
