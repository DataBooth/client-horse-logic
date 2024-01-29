import glob
from pathlib import Path
import re
import pandas as pd
import numpy as np
from datetime import datetime


class Logfile:
    # Use the __init__ method to initialize the object attributes
    def __init__(self, file_name, file_contents):
        self.file_name = Path(file_name).name
        self.file_contents = file_contents
        self.num_lines = len(file_contents)


    def parse_filename_components(self):
        # Adjusted regular expression pattern to match 'nan' or numbers with optional decimal part
        pattern = r'(?P<suffix>[\w]+)_(?P<datetime_str>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)_(?P<subject_name>[\w]+)_(?P<trial_number>nan|\d+(\.\d+)?)_(?P<experiment_type>[\w-]+)\.log'
        match = re.match(pattern, self.file_name)
        if match:
            components = match.groupdict()
            # Handle 'nan' and convert numbers with '.0' to integers
            trial_number = components['trial_number']
            if trial_number.lower() != 'nan':
                components['trial_number'] = int(float(trial_number))
            else:
                components['trial_number'] = None  # or np.nan if you prefer to use numpy's NaN representation
            components['datetime'] = datetime.fromisoformat(components['datetime_str'])
            return components
        else:
            raise ValueError(f"Filename {self.file_name} does not match the expected pattern.")


    # Use the __str__ method to control how the object is represented as a string
    def __str__(self):
        return f"Logfile: {self.file_name}, {self.num_lines} lines"

    def __repr__(self):
        return f"<Logfile file_name={self.file_name!r}, num_lines={self.num_lines}>"


class Logs:
    # Use the __init__ method to initialize the object attributes
    def __init__(self, path, patterns, include=True, logfile_ext=".log"):
        self.path = path
        if isinstance(patterns, str):
            patterns = [patterns]
        self.patterns = patterns
        self.include = include
        self.logfiles = []  # A list of Logfile objects
        self.included_files = []
        self.excluded_files = []
        self.logfile_ext = logfile_ext
        self.load_logfiles()  # A method to load the log files from the directory


    # Define a method to load the log files from the directory
    def load_logfiles(self):
        matched_files = set()
        for pattern in self.patterns:
            matched_files.update(glob.glob(f"{self.path}/{pattern}"))

        all_files = set(glob.glob(f"{self.path}/*{self.logfile_ext}"))
        if self.include:
            self.included_files = [Path(file).name for file in list(matched_files)]
            self.excluded_files = [Path(file).name for file in list(all_files - matched_files)]
        else:
            self.included_files = [Path(file).name for file in list(all_files - matched_files)]
            self.excluded_files = [Path(file).name for file in list(matched_files)]

        for file_name in self.included_files:
            with open(f"{self.path}/{file_name}", "r") as file:
                file_contents = file.readlines()
                logfile = Logfile(file_name, file_contents)
                self.logfiles.append(logfile)


    def create_filename_components_dataframe(self, file_list):
        # Initialize lists to hold the data
        data = {
            'original_filename': [],
            'suffix': [],
            'datetime': [],
            'subject_name': [],
            'trial_number': [],
            'experiment_type': []
        }

        # Process included and excluded files
        # for file_list in (self.included_files, self.excluded_files):
        for file_name in file_list:
            try:
                # Parse the filename components
                components = Logfile(file_name, "").parse_filename_components()
                if components is not None:
                    data['original_filename'].append(file_name)
                    data['suffix'].append(components['suffix'])
                    data['datetime'].append(components['datetime'])
                    data['subject_name'].append(components['subject_name'])
                    data['trial_number'].append(components['trial_number'])
                    data['experiment_type'].append(components['experiment_type'])
                else:
                    print(f"Can't match {file_name}")
            except ValueError as e:
                print(f"Error processing file {file_name}: {e}")

        # Create a DataFrame from the collected data
        df = pd.DataFrame(data)
        return df

    def __str__(self):
        return f"Logs: {len(self.logfiles)} log files in {self.path}"

    def __repr__(self):
        return f"<Logs path={self.path!r}, num_logfiles={len(self.logfiles)}>"
