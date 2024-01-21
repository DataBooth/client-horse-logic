import glob
from pathlib import Path


class Logfile:
    # Use the __init__ method to initialize the object attributes
    def __init__(self, file_name, file_contents):
        self.file_name = file_name  # The name of the log file
        self.file_contents = (
            file_contents  # The contents of the log file as a list of strings
        )
        self.num_lines = len(file_contents)  # The number of lines in the log file

    # Use the __str__ method to control how the object is represented as a string
    def __str__(self):
        return f"Logfile: {self.file_name}, {self.num_lines} lines"

    def __repr__(self):
        return f"<Logfile file_name={self.file_name!r}, num_lines={self.num_lines}>"


class Logs:
    # Use the __init__ method to initialize the object attributes
    def __init__(self, path, patterns, include=True):
        self.path = path
        if isinstance(patterns, str):
            patterns = [patterns]
        self.patterns = patterns
        self.include = include
        self.logfiles = []  # A list of Logfile objects
        self.included_files = []
        self.excluded_files = []
        self.load_logfiles()  # A method to load the log files from the directory


    # Define a method to load the log files from the directory
    def load_logfiles(self):
        import glob
        matched_files = set()
        for pattern in self.patterns:
            matched_files.update(glob.glob(f"{self.path}/{pattern}"))

        all_files = set(glob.glob(f"{self.path}/*.log"))
        if self.include:
            self.included_files = list(matched_files)
            self.excluded_files = list(all_files - matched_files)
        else:
            self.included_files = list(all_files - matched_files)
            self.excluded_files = list(matched_files)

        for file_name in self.included_files:
            with open(file_name, "r") as file:
                file_contents = file.readlines()
                logfile = Logfile(file_name, file_contents)
                self.logfiles.append(logfile)


    def __str__(self):
        return f"Logs: {len(self.logfiles)} log files in {self.path}"

    def __repr__(self):
        return f"<Logs path={self.path!r}, num_logfiles={len(self.logfiles)}>"
