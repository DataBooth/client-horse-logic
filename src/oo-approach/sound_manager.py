# sound_manager.py
import pygame
import toml
from pathlib import Path


class SoundManager:
    def __init__(self, sounds_config_path):
        pygame.mixer.init()
        self.sounds_config_path = sounds_config_path
        self.sound_files = self._load_sound_config()
        self.sounds_cache = {}
        self._validate_sound_files()
        self._cache_sounds()

    def _load_sound_config(self):
        if not Path(self.sounds_config_path).is_file():
            raise FileNotFoundError(
                f"The sound configuration file {self.sounds_config_path} does not exist."
            )
        with open(self.sounds_config_path, "r") as config_file:
            sound_config = toml.load(config_file)
        return sound_config

    def _validate_sound_files(self):
        for sound_name, file_path in self.sound_files.items():
            if not Path(file_path).is_file():
                raise FileNotFoundError(f"The sound file {file_path} for '{sound_name}' does not exist.")

    def _cache_sounds(self):
        for sound_name, file_path in self.sound_files.items():
            self.sounds_cache[sound_name] = pygame.mixer.Sound(file_path)

    def play_sound(self, sound_name):
        if sound_name not in self.sounds_cache:
            raise ValueError(f"Sound '{sound_name}' is not recognized or cached.")
        self.sounds_cache[sound_name].play()


# Example usage:
sounds_config_path = "experiment_sounds.toml"
sound_manager = SoundManager(sounds_config_path)
sound_manager.play_sound("system_ready")
