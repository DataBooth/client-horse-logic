# data_manager.py
import pandas as pd
from pathlib import Path


class DataManager:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.subjects_file = self.data_dir / "experiment_subjects.xlsx"
        self.parameters_file = self.data_dir / "experiment_parameters.xlsx"
        self.log_file = None
        self.quantity_file = None

    def load_subjects(self):
        return pd.read_excel(self.subjects_file)

    def load_parameters(self):
        return pd.read_excel(self.parameters_file)

    def set_log_files(self, subject_name, session_number, session_type):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        base_filename = f"Experiment_{timestamp}_{subject_name}_{session_number}_{session_type}"
        self.log_file = self.data_dir / f"{base_filename}.log"
        self.quantity_file = self.data_dir / f"{base_filename}.csv"

    def log_event(self, event):
        with open(self.log_file, "a") as log:
            log.write(f"{datetime.now()}: {event}\n")

    def log_quantity(self, trial_number, quantity_name, quantity_value):
        with open(self.quantity_file, "a") as qfile:
            qfile.write(f"{datetime.now()},{trial_number},{quantity_name},{quantity_value}\n")

    # Additional methods for updating subjects, confirming details, etc.
