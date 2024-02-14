import time
from pathlib import Path

import pandas as pd
from experiment_helper import (
    create_log_quantity_header_file,
    create_output_filenames,
    initialise_data_dir,
    initialise_GPIO_buttons,
    load_validate_experiment_parameters,
    log_event,
    log_trial_parameters,
    read_experiment_schedule,
    set_subject_name,
    update_subjects_xlsx,
)
from hardware_tester import HardwareTester
from text_to_speech import TextToSpeechGoogle
from toml import load as toml_load


class Experiment:
    def __init__(self, config_path, data_dir):
        self.config = self.load_config(config_path)
        self.data_dir = initialise_data_dir(data_dir)
        self.tts = TextToSpeechGoogle()
        self.hardware_tester = HardwareTester()
        self.gpio, self.green_button, self.blue_button, self.red_button = initialise_GPIO_buttons()
        self.trainer_schedule, self.reward_schedule = self.load_and_validate_schedules()
        self.logger = Logger(data_dir=self.data_dir,
                             log_file_name="experiment_log.txt",
                             quantity_file_name="experiment_quantity.csv",
                             tts=self.tts,
                             echo=True,
                             speak=True)

    def load_config(self, config_path):
        return toml_load(config_path)



    def load_and_validate_schedules(self):
        trainer_schedule_df, reward_schedule_df = read_experiment_schedule(data_dir=self.data_dir)
        # Example validation logic
        expected_columns = self.config["validation"]["trainer_schedule_columns"]
        if not all(column in trainer_schedule_df.columns for column in expected_columns):
            raise ValueError("Trainer schedule does not have the expected columns.")
        if len(trainer_schedule_df) != self.config["validation"]["expected_rows"]:
            raise ValueError("Trainer schedule does not have the expected number of rows.")
        # Repeat validation for reward_schedule_df
        return trainer_schedule_df, reward_schedule_df

    def wait_for_green_button(self):
        print("Waiting for green button to start the trial...")
        while not self.green_button.is_pressed():
            time.sleep(0.1)  # Poll every 100ms
        print("Green button pressed. Starting trial...")

    def start_experiment(self):
        # Setup and start the experiment
        pass

    # Additional methods as needed

    def start_day(self):
        # Initialize the system for a new day
        pass


    def start_trial(self, trial_number, trainer, reward):
        self.tts.speak(
            f"Starting trial {trial_number} with trainer {trainer}. Reward: {'Yes' if reward else 'No'}"
        )

    def complete_session(self):
        # Complete the session and log the completion
        pass


    def run_experiment(self):
        self.start_day()
        self.logger.log_event("Experiment started")
        self.logger.log_quantity("Some quantity test", 1.23, self.subject_name, trial_number, trainer_number)

        for trial in range(1, 21):
            trainer, reward = self.determine_trainer_and_reward(trial)
            self.wait_for_green_button()  # Wait for green button to start the trial
            self.start_trial(trial, trainer, reward)
            # Additional logic for handling blue and red buttons during the trial
            if trial == 10:
                self.tts.speak("First half of the session is completed.")
                self.wait_for_green_button()  # Wait for green button to continue
        self.complete_session()
        self.tts.speak("The session is completed.")
