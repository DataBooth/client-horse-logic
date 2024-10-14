import hashlib
import os
import socket
from time import sleep

import contextlib

with contextlib.redirect_stdout(None):
    import pygame  # supress pygame version info / welcome message

from gtts import gTTS


def play_sound_with_pygame(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait for audio to finish playing
        pygame.time.Clock().tick(10)


class TextToSpeechGoogle:
    """
    Note that this requires an internet connection to use the Google TTS package.
    Although it does cache sound files (to the gtts_cache subdirectory) and can re-use them if in offline mode.
    """
    def __init__(self, lang="en", cache_dir="gtts_cache"):
        self.lang = lang
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def is_connected(self):
        try:
            socket.create_connection(("www.google.com", 80), timeout=5)
            return True
        except OSError:
            return False

    def get_cache_filename(self, text):
        # Create a hash of the text to generate a unique filename
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{text_hash}.mp3")

    def speak(self, text):
        cache_filename = self.get_cache_filename(text)
        # Check if the audio file already exists in the cache
        if not os.path.exists(cache_filename):
            if not self.is_connected():
                print("No internet connection available and no cached file.")
                return
            print("Generating new audio file...")
            tts = gTTS(text=text, lang=self.lang, slow=False)
            tts.save(cache_filename)
        else:
            print("Using cached audio file.")

        print(text)  # Echo the text to the screen
        play_sound_with_pygame(cache_filename)

    def speak_trial_info(
        self, day_number, trial_number, reward_given=False, reward_amount=None, trainer=1
    ):
        reward_text = "no reward"
        if reward_given and reward_amount in [70, 30]:
            reward_text = f"reward of {reward_amount}"

        text = f"Day {day_number}, trial {trial_number}, {reward_text}, trainer {trainer}"
        self.speak(text)


if __name__ == "__main__":
    # Example use #1

    tts_google = TextToSpeechGoogle()
    if tts_google.is_connected():
        tts_google.speak("Hello, this is a test.")

        # Example use #2

        tts_google.speak(
            "This is another test - looping through trials, trainers and rewards. It is not the final format."
        )

        for day in range(1, 3):  # Loop over days 1 to 6
            for trial in range(1, 11):  # Loop over trials 1 to 10
                # Example conditionals for demonstration
                reward_given = trial % 2 == 0  # Reward given on even trials
                reward_amount = 70 if day % 2 == 0 else 30  # 70 on even days, 30 on odd
                trainer = 1 if day < 4 else 2  # Trainer 1 for days 1-3, Trainer 2 for days 4-6
                tts_google.speak_trial_info(day, trial, reward_given, reward_amount, trainer)
                sleep(0.5)
    else:
        print("\nInternet connection not available. Exiting.")


# Usage:
#
# Run text-to-speech tests by running:
#
# python text_to_speech.py
