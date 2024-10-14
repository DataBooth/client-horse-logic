# experiment.py
import sys
from datetime import datetime
from experiment_helper import Button, Servo, TouchSensor
from data_manager import DataManager
from sound_manager import SoundManager
from pathlib import Path


class Experiment:
    def __init__(self, config, data_manager, sound_manager, hardware):
        self.config = config
        self.data_manager = data_manager
        self.sound_manager = sound_manager
        self.hardware = hardware
        self.trial_number = 0
        self.session_active = False
        self.session_type = self.config["SESSION_TYPE"]
        # ... other initializations ...

    def run(self):
        try:
            self._start_experiment()
            while self.trial_number < self.config["TRIAL_LIMIT"]:
                self._run_trial()
                self.trial_number += 1
            self._end_experiment()
        except KeyboardInterrupt:
            self.data_manager.log_event("Keyboard interrupt - exiting...")
            self.hardware.cleanup()

    def setup(self):
        self.subject_name = self._get_subject_name()
        self.session_number = self._get_next_session_number(self.subject_name)
        self.session_type = self._choose_session_type()
        self.data_manager.set_log_files(self.subject_name, self.session_number, self.session_type)
        self.config.update(self.data_manager.load_parameters())

    def _get_subject_name(self):
        subjects_df = self.data_manager.load_subjects()
        subject_names = subjects_df["subject_name"].str.lower().str.replace(" ", "").unique()
        subject_name = ""
        while not subject_name:
            subject_name_input = input("Enter subject name: ").lower().replace(" ", "")
            if subject_name_input in subject_names:
                subject_name = subject_name_input
            else:
                print(f"Subject {subject_name_input} not found. Please try again.")
        return subject_name

    def _get_next_session_number(self, subject_name):
        subjects_df = self.data_manager.load_subjects()
        subject_data = subjects_df[
            subjects_df["subject_name"].str.lower().str.replace(" ", "") == subject_name
        ]
        if subject_data.empty:
            return 1  # If new subject, start with session 1
        else:
            last_session_number = subject_data["last_session_number"].max()
            return last_session_number + 1

    def _choose_session_type(self):
        session_types = {"1": "RP-A", "2": "RP-H", "3": "RP-E", "4": "RP-R"}
        session_type = ""
        while session_type not in session_types:
            print("\nChoose session type:")
            for key, value in session_types.items():
                print(f"{key} - {value}")
            choice = input("\nEnter session type: ")
            session_type = session_types.get(choice)
            if not session_type:
                print("Invalid choice. Please try again.")
        return session_type

    def _confirm_experiment_details(self):
        print(f"\nSubject name: {self.subject_name}")
        print(f"Session number: {self.session_number}")
        print(f"Experiment type: {self.session_type}")
        confirm = input("\nAre the details ok for this session (Y (or return) - continue / N - exit)?: ")
        return confirm.lower() in ["y", "yes", ""]

    def _start_experiment(self):
        self.data_manager.log_event("Experiment started")
        self.session_active = True
        self.trial_number = 0
        # Play a sound to indicate the experiment is starting
        self.sound_manager.play_system_ready()
        # ... additional start experiment logic ...

    def _run_trial(self):
        self.data_manager.log_event(f"Trial {self.trial_number} started")
        # Play the start tone
        self.sound_manager.play_start_tone()
        start_time = datetime.now()

        # Wait for a response or timeout
        response = self._wait_for_response(start_time)

        if response:
            self._handle_response(start_time)
        else:
            self._handle_timeout()

        # ... additional trial logic ...

    def _end_experiment(self):
        self.session_active = False
        self.data_manager.log_event("Experiment ended")
        # Play a sound to indicate the experiment is ending
        self.sound_manager.play_session_terminated()
        # ... additional end experiment logic ...

    def _wait_for_response(self, start_time):
        # Logic to wait for touch sensor or button press
        # This is a placeholder for actual implementation
        # Return True if response is detected, False if timeout occurs
        return True

    def _handle_response(self, start_time):
        response_time = datetime.now()
        latency = (response_time - start_time).total_seconds()
        self.data_manager.log_event(f"Response received in {latency} seconds")
        self.sound_manager.play_correct_tone()
        # Dispense feed if appropriate for session type
        if self.session_type in ["RP-A", "RP-R"]:
            self.hardware["servo"].dispense_feed()
        # ... additional response handling logic ...

    def _handle_timeout(self):
        self.data_manager.log_event("Response timeout")
        if self.session_type == "RP-H":
            self.sound_manager.play_incorrect_tone()
        # ... additional timeout handling logic ...
