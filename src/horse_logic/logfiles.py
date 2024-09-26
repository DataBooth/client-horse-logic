import glob
import json
import re
from dataclasses import dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

import pandas as pd
from IPython.display import Markdown, display
from loguru import logger

def parse_direction(comment):
    comment_lower = comment.lower()
    if "right" in comment_lower:
        return "RIGHT"
    elif "left" in comment_lower:
        return "LEFT"
    else:
        return None

# RPE Experiments

@dataclass
class Experiment:
    ExperimentID: int
    Cohort: str
    SubjectName: str
    SubjectNumber: int
    SessionNumber: int
    ExperimentType: str
    Comment: Optional[str]
    DateTime: datetime
    LogFileName: str
    Parameters: Dict


@dataclass
class Trial:
    TrialID: int
    ExperimentID: int
    TrialNumber: int
    TrialStartTime: datetime
    TrialEndTime: datetime


@dataclass
class Event:
    EventID: int
    TrialID: int
    EventNumber: int
    EventTime: datetime
    EventType: str
    EventElapsedTime: float


# CB Experiments


@dataclass
class ExperimentCB:
    ExperimentID: int
    Cohort: str
    SubjectName: str
    SubjectNumber: int
    SessionNumber: int
    SessionType: str  # New field: "training" or "test"
    ExperimentType: str
    Comment: Optional[str]
    DateTime: datetime
    LogFileName: str
    Parameters: Dict

@dataclass
class TrialCB:
    TrialID: int
    ExperimentID: int
    TrialNumber: int
    ResponseType: str
    TrialSubType: str
    Direction: str
    CriterionType: Optional[str]
    CriterionCount: Optional[float]
    TrialStartTime: datetime
    TrialEndTime: datetime
    SessionType: str  # New field: "training" or "test"

@dataclass
class ResponseCB:
    ResponseID: int
    TrialID: int
    ResponseTime: Optional[float]
    EventDateTime: datetime

@dataclass
class EventCB:
    EventID: int
    TrialID: int
    EventType: str
    EventTime: datetime
    ElapsedTime: float


class Logfile:
    def __init__(self, file_name: str, file_contents: Optional[List[str]] = None) -> None:
        """
        Initialise a Logfile object.

        Args:
            file_name (str): The name of the log file.
            file_contents (Optional[List[str]]): The contents of the log file as a list of strings.

        Returns:
            None
        """
        self.file_name = Path(file_name).name
        # If file_contents is None, read the contents from the file
        if file_contents is None:
            if Path(file_name).exists():
                with open(file_name, "r") as file:
                    self.file_contents = file.readlines()
            else:
                raise FileNotFoundError(f"File missing: {Path(file_name).resolve()}")
        else:
            self.file_contents = file_contents
        self.num_lines = len(self.file_contents)

    def parse_filename_components(self) -> Experiment:
        """
        Parse the components of the filename for RPE experiments.

        Returns:
            Experiment: An Experiment object containing the parsed information.

        Raises:
            ValueError: If the filename does not match the expected pattern.
        """
        # Adjusted regular expression pattern to match 'nan' or numbers with optional decimal part
        pattern = r"(?P<suffix>[\w]+)_(?P<datetime_str>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)_(?P<subject_name>[\w]+)_(?P<session_number>nan|\d+(\.\d+)?)_(?P<experiment_type>[\w-]+)\.log"
        match = re.match(pattern, self.file_name)
        if match:
            components = match.groupdict()
            # Handle 'nan' and convert numbers with '.0' to integers
            session_number = components["session_number"]
            if session_number.lower() != "nan":
                components["session_number"] = int(float(session_number))
            else:
                components["session_number"] = (
                    None  # or np.nan if you prefer to use numpy's NaN representation
                )
            components["datetime"] = datetime.fromisoformat(components["datetime_str"])
            components["filename"] = self.file_name
            return Experiment(
                ExperimentID=None,  # ID is auto-generated or not needed for insertion
                Cohort=None,
                SubjectName=components["subject_name"],
                SubjectNumber=None,  # This needs to be inserted from the external SubjectName, SubjectNumber table
                SessionNumber=components["session_number"],
                ExperimentType=components["experiment_type"],
                Comment=self.parse_comments(),
                DateTime=components["datetime"],
                LogFileName=components["filename"],
                Parameters=None
            )
        else:
            raise ValueError(f"Filename {self.file_name} does not match the expected pattern.")

    def parse_filename_components_cog_bias(self) -> ExperimentCB:
        """
        Parse the components of the filename for cognitive bias experiments.

        Returns:
            Experiment: An Experiment object containing the parsed information.

        Raises:
            ValueError: If the filename does not match the expected pattern.
        """
        # Adjusted regular expression pattern to match the new filename format
        pattern = r"Experiment_(?P<datetime_str>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)_(?P<subject_name>[\w]+)_(?P<session_number>nan|\d+(\.\d+)?)_(?P<experiment_type>.+)\.log"
        match = re.match(pattern, self.file_name)
        if match:
            components = match.groupdict()
            # Handle 'nan' and convert numbers with '.0' to integers
            session_number = components["session_number"]
            if session_number.lower() != "nan":
                components["session_number"] = int(float(session_number))
            else:
                components["session_number"] = None
            components["datetime"] = datetime.fromisoformat(components["datetime_str"])
            components["filename"] = self.file_name

            # Determine SessionType based on the presence of criterion count/type
            has_criterion = 'criterion count' in self.file_contents or 'criterion type' in self.file_contents
            session_type = "training" if has_criterion else "test"

            return ExperimentCB(
                ExperimentID=None,  # ID is auto-generated or not needed for insertion
                Cohort=None,        # This needs to be inserted from the external Cohort table
                SubjectName=components["subject_name"],
                SubjectNumber=None,  # This needs to be inserted from the external SubjectName, SubjectNumber table
                SessionNumber=components["session_number"],
                SessionType=session_type,
                ExperimentType=components["experiment_type"],
                Comment=self.parse_comments(),
                DateTime=components["datetime"],
                LogFileName=components["filename"],
                Parameters=None
            )
        else:
            raise ValueError(f"Filename {self.file_name} does not match the expected pattern.")


    def parse_parameters(self) -> Dict[str, Any]:
        """
        Parse the parameters from the log file.

        Returns:
            Dict[str, Any]: A dictionary containing the parsed parameters.
        """
        params_pattern = r"PARAMETERS:\n({.*?})\n"
        file_content_str = "".join(self.file_contents)
        params_match = re.search(params_pattern, file_content_str, re.DOTALL)
        if params_match:
            params_block = params_match.group(1)
            # Assuming the parameters block is in a Python dictionary format
            params_dict = eval(params_block)
            return params_dict
        return {}

    def parse_comments(self) -> str:
        """
        Parse comments from the log file.

        Returns:
            str: A string containing all comments found in the log file.
        """
        # Join the list of strings into a single string if necessary
        file_content_str = (
            "".join(self.file_contents) if isinstance(self.file_contents, list) else self.file_contents
        )
        comment_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): Comment: (.+)"
        comments = re.findall(comment_pattern, file_content_str)
        # Extract just the comment part
        comment_text = " ".join(comment[1] for comment in comments)
        return comment_text

    def parse_trials_and_events(self) -> Tuple[Optional[List[Dict[str, Any]]], Optional[List[Dict[str, Any]]]]:
        """
        Parse trials and events from RPE log files.

        Returns:
            A tuple containing lists of trials and events.
            Returns (None, None) if no data is found.
        """
        trials = []
        events = []
        trial_pattern = r"Current trial: (\d+)"
        event_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): (.+)"
        file_content_str = "".join(self.file_contents)
        trials_split = re.split(trial_pattern, file_content_str)
        for i in range(1, len(trials_split), 2):
            trial_number = int(trials_split[i])
            trial_events = re.findall(event_pattern, trials_split[i + 1])
            trials.append({"TrialNumber": trial_number})
            for event_datetime, event_desc in trial_events:
                events.append(
                    {
                        "TrialNumber": trial_number,
                        "EventType": event_desc,
                        "EventDateTime": event_datetime,
                    }
                )
        if trials == [] or events == []:
            logger.error(f"{self.file_name} contains no data - exclude from analysis.")
            return None, None
        return trials, events


    def parse_direction(self, comments):
            # Implement direction parsing logic here
            pass

    def parse_trials_and_events_cog_bias(self) -> Optional[Dict[str, List]]:
        file_content_str = "".join(self.file_contents)
        direction = self.parse_direction(self.parse_comments())
        trial_start_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): Green button pressed - system ready"
        trial_start_match = re.search(trial_start_pattern, file_content_str)

        if not trial_start_match:
            logger.error(f"{self.file_name} does not contain a trial start time.")
            return None

        experiment_start_time = datetime.fromisoformat(trial_start_match.group(1))
        event_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): ((GO|NOGO) for Trial (\d+) - (P|N|M|NP|NN) - (positive|negative|median|near positive|near negative)( - response time (\d+\.\d+))?( - (positive|negative) criterion count (\d+))?|Green button pressed - horse released)"
        event_matches = re.findall(event_pattern, file_content_str)

        experiment = self.parse_filename_components_cog_bias()
        trials = []
        responses = []
        events = []

        for event in event_matches:
            event_datetime_str, event_desc, response_type, trial_number, trial_sub_type, criterion_type, _, response_time, _, _, criterion_count = event
            event_datetime = datetime.fromisoformat(event_datetime_str)

            if trial_number:
                trial = TrialCB(
                    TrialID=len(trials) + 1,
                    ExperimentID=experiment.ExperimentID,
                    TrialNumber=int(trial_number),
                    ResponseType=response_type,
                    TrialSubType=trial_sub_type,
                    Direction=direction,
                    CriterionType=criterion_type if criterion_count else None,
                    CriterionCount=float(criterion_count) if criterion_count else None,
                    TrialStartTime=event_datetime,
                    TrialEndTime=event_datetime,
                    SessionType=experiment.SessionType
                )
                trials.append(trial)

                if response_type == "GO" and response_time:
                    responses.append(ResponseCB(
                        ResponseID=len(responses) + 1,
                        TrialID=trial.TrialID,
                        ResponseTime=float(response_time),
                        EventDateTime=event_datetime
                    ))

            events.append(EventCB(
                EventID=len(events) + 1,
                TrialID=trial.TrialID if trial_number else None,
                EventType=event_desc,
                EventTime=event_datetime,
                ElapsedTime=(event_datetime - experiment_start_time).total_seconds()
            ))

            if trials:
                trials[-1].TrialEndTime = event_datetime

        if not trials:
            logger.error(f"{self.file_name} contains no data - exclude from analysis.")
            return None

        return {
            "experiment": experiment,
            "trials": trials,
            "responses": responses,
            "events": events
        }


    def insert_record_to_database(self, con, record):
        table_name = record.__class__.__name__.lower() + 's'  # Assumes table name is plural of the class name
        columns = ', '.join(field.name for field in fields(record))
        placeholders = ', '.join('?' for _ in fields(record))
        values = []
        for field in fields(record):
            value = getattr(record, field.name)
            if isinstance(value, dict):  # Convert dict to JSON string
                value = json.dumps(value)
            values.append(value)
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        con.execute(query, tuple(values))

    def __str__(self):
        return f"Logfile: {self.file_name}, {self.num_lines} lines"

    def __repr__(self):
        return f"<Logfile file_name={self.file_name!r}, num_lines={self.num_lines}>"


class Logs:
    def __init__(self, path: str, patterns: Optional[List[str]] = None, include: bool = True, logfile_ext: str = ".log") -> None:
        """
        Initialise Logs object.

        Args:
            path (str): The directory path containing log files.
            patterns (Optional[List[str]]): Patterns to match log files.
            include (bool): Whether to include or exclude files matching the patterns.
            logfile_ext (str): The file extension for log files.

        Returns:
            None
        """
        self.path = path
        self.include = include
        self.logfiles = []  # A list of Logfile objects
        self.included_files = []
        self.excluded_files = []
        self.logfile_ext = logfile_ext
        if patterns is not None:
            if isinstance(patterns, str):
                patterns = [patterns]
            self.patterns = patterns
            self.load_logfiles()  # A method to load the log files from the directory
        else:
            self.patterns = []

    # Define a method to load the log files from the directory
    def load_logfiles(self) -> None:
        """
        Load log files from the specified directory based on patterns.

        Returns:
            None
        """
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

    def handle_specific_files(self, file_names: List[str], include: bool = True) -> None:
        """
        Handle specific file names to include or exclude.

        Args:
            file_names (List[str]): List of file names to include or exclude.
            include (bool): Flag indicating whether to include (True) or exclude (False) the files.

        Returns:
            None
        """
        # Convert file_names to a set for faster operations
        file_names_set = set(file_names)
        # Get all files in the directory with the specified extension
        all_files = set(glob.glob(f"{self.path}/*{self.logfile_ext}"))
        # Get the base names of all files
        all_file_names = {Path(file).name for file in all_files}
        # Determine the intersection and difference
        matched_files = file_names_set & all_file_names
        unmatched_files = file_names_set - all_file_names

        included_count = 0
        excluded_count = 0

        # Process matched files
        for file_name in sorted(matched_files):
            if include:
                if file_name in self.included_files:
                    logger.info(f"File {file_name} is already included.")
                else:
                    self.included_files.append(file_name)
                    logger.info(f"File {file_name} has been included.")
                    included_count += 1
            else:
                if file_name in self.excluded_files:
                    logger.info(f"File {file_name} is already excluded.")
                else:
                    self.excluded_files.append(file_name)
                    if file_name in self.included_files:
                        self.included_files.remove(file_name)
                    logger.info(f"File {file_name} has been excluded.")
                    excluded_count += 1

        # Report unmatched files
        for file_name in unmatched_files:
            logger.warning(f"File {file_name} not found in the path.")

        # Update the logfiles list based on the new included_files
        self.logfiles = [
            Logfile(f"{self.path}/{file_name}", open(f"{self.path}/{file_name}", "r").readlines())
            for file_name in self.included_files
            if Path(f"{self.path}/{file_name}").exists()
        ]

        if include:
            logger.info(f"# Files specifically included: {included_count}")
        else:
            logger.info(f"# Files specifically excluded: {excluded_count}")

    def create_filename_components_dataframe(self, file_list: List[str]) -> pd.DataFrame:
        """
        Create a DataFrame containing filename components for RPE experiments.

        Args:
            file_list (List[str]): List of filenames to process.

        Returns:
            pd.DataFrame: A DataFrame containing parsed filename components.
        """
        # Initialize lists to hold the data
        data = {
            "original_filename": [],
            "suffix": [],
            "datetime": [],
            "subject_name": [],
            "session_number": [],
            "experiment_type": [],
        }

        # Process included and excluded files
        # for file_list in (self.included_files, self.excluded_files):
        for file_name in file_list:
            try:
                # Parse the filename components
                experiment = Logfile(file_name, "").parse_filename_components()
                if experiment is not None:
                    data["original_filename"].append(experiment.LogFileName)
                    data["suffix"].append("Experiment")
                    data["datetime"].append(experiment.DateTime)
                    data["subject_name"].append(experiment.SubjectName)
                    data["session_number"].append(experiment.SessionNumber)
                    data["experiment_type"].append(experiment.ExperimentType)
                    # data['filename']
                else:
                    logger.info(f"Can't match {file_name}")
            except ValueError as e:
                logger.info(f"Error processing file {file_name}: {e}")

        # Create a DataFrame from the collected data
        df = pd.DataFrame(data)
        return df

    def create_filename_components_dataframe_cog_bias(self, file_list: List[str]) -> pd.DataFrame:
        """
        Create a DataFrame containing filename components for cognitive bias experiments.

        Args:
            file_list (List[str]): List of filenames to process.

        Returns:
            pd.DataFrame: A DataFrame containing parsed filename components.
        """
        # Initialize lists to hold the data
        data = {
            "original_filename": [],
            "suffix": [],
            "datetime": [],
            "subject_name": [],
            "session_number": [],
            "experiment_type": [],
        }

        # Process included and excluded files
        # for file_list in (self.included_files, self.excluded_files):
        for file_name in file_list:
            #try:
            # Parse the filename components
            experiment = Logfile(file_name, "").parse_filename_components_cog_bias()
            if experiment is not None:
                data["original_filename"].append(experiment.LogFileName)
                data["suffix"].append("Experiment")
                data["datetime"].append(experiment.DateTime)
                data["subject_name"].append(experiment.SubjectName)
                data["session_number"].append(experiment.SessionNumber)
                data["experiment_type"].append(experiment.ExperimentType)
                # data['filename']
            else:
                logger.info(f"Can't match {file_name}")
            #except ValueError as e:
                logger.info(f"Error processing file {file_name}: {e}")

        # Create a DataFrame from the collected data
        df = pd.DataFrame(data)
        return df

    def load_specific_logfiles_from_csv(self, csv_file_path: str) -> None:
        """
        Load specific log files listed in a CSV file.

        Args:
            csv_file_path (str): Path to the CSV file containing log file names.

        Returns:
            None
        """
        # Read the CSV file into a DataFrame, specifying that it has no header
        df = pd.read_csv(csv_file_path, header=None)

        # Get the second column (index 1) and convert it to a list
        file_names = df[1].tolist()

        # Filter out any non-log files
        log_file_names = [file_name for file_name in file_names if file_name.endswith(self.logfile_ext)]

        # Load these log files
        for file_name in log_file_names:
            file_path = Path(self.path) / file_name
            if file_path.exists():
                with open(file_path, "r") as file:
                    self.logfiles.append(Logfile(file_name, file.readlines()))
            else:
                logger.warning(f"File {file_name} does not exist.")

    def display_sessions_by_subject(self, df_out, subject_df):
        session_summary = []
        for n_subject, subject_name in enumerate(subject_df["subject_name"]):
            df_ = df_out.drop(columns=["suffix", "subject_name"])[df_out["subject_name"] == subject_name]
            n_session = len(df_)
            session_summary.append((n_subject + 1, subject_name.capitalize(), n_session))
            if n_session == 0:
                logger.info(f"Subject {subject_name}: No experiments conducted")
            else:
                df_.loc[:, "time_dff"] = df_["datetime"].diff()
                display(
                    Markdown(f"### {n_subject+1}. {subject_name.capitalize()}: {n_session} session(s)")
                )
                display(df_)
        return pd.DataFrame(session_summary, columns=["Subject number", "Subject name", "Session count"])



    def __str__(self):
        return f"Logs: {len(self.logfiles)} log files in {self.path}"

    def __repr__(self):
        return f"<Logs path={self.path!r}, num_logfiles={len(self.logfiles)}>"
