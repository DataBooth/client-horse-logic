# This is a refactored (classed-base) version of logfiles.py (it has not been used/tested) and is for
# demonstration purposes only to think about possibilities for enhancements in the future.

import glob
import json
import re
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from loguru import logger


# Configuration
class Config:
    LOG_FILE_EXT = ".log"
    FILENAME_PATTERNS = {
        "RPE": r"(?P<experiment_type>[\w]+)_(?P<datetime_str>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)_(?P<subject_name>[\w]+)_(?P<session_number>nan|\d+(\.\d+)?)_(?P<experiment_subtype>[\w-]+)\.log",
        "CB": r"Experiment_(?P<datetime_str>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)_(?P<subject_name>[\w]+)_(?P<session_number>nan|\d+(\.\d+)?)_(?P<experiment_type>.+)\.log",
    }
    EVENT_PATTERN = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): (.+)"
    CB_EVENT_PATTERN = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): ((GO|NOGO) for Trial (\d+) - (P|N|M|NP|NN) - (positive|negative|median|near positive|near negative)( - response time (\d+\.\d+))?( - (positive|negative) criterion count (\d+))?|Green button pressed - horse released)"


# Base classes
@dataclass
class BaseExperiment(ABC):
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
class BaseTrial(ABC):
    TrialID: int
    ExperimentID: int
    TrialNumber: int
    TrialStartTime: datetime
    TrialEndTime: datetime


@dataclass
class BaseEvent(ABC):
    EventID: int
    TrialID: int
    EventTime: datetime
    EventType: str


# RPE Experiments
@dataclass
class Experiment(BaseExperiment):
    pass


@dataclass
class Trial(BaseTrial):
    pass


@dataclass
class Event(BaseEvent):
    EventNumber: int
    EventElapsedTime: float


# CB Experiments
@dataclass
class ExperimentCB(BaseExperiment):
    SessionType: str


@dataclass
class TrialCB(BaseTrial):
    ResponseType: str
    TrialSubType: str
    Direction: str
    CriterionType: Optional[str]
    CriterionCount: Optional[float]
    SessionType: str


@dataclass
class ResponseCB:
    ResponseID: int
    TrialID: int
    ResponseTime: Optional[float]
    EventDateTime: datetime


@dataclass
class EventCB(BaseEvent):
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


class LogfileParser(ABC):
    def __init__(self, file_name: str, file_contents: Optional[List[str]] = None):
        self.file_name = Path(file_name).name
        self.file_contents = (
            self._read_file_contents(file_name) if file_contents is None else file_contents
        )
        self.num_lines = len(self.file_contents)

    @staticmethod
    def _read_file_contents(file_name: str) -> List[str]:
        try:
            with open(file_name, "r") as file:
                return file.readlines()
        except FileNotFoundError:
            logger.error(f"File missing: {Path(file_name).resolve()}")
            raise

    @abstractmethod
    def parse_filename_components(self) -> Union[Experiment, ExperimentCB]:
        pass

    def parse_parameters(self) -> Dict[str, Any]:
        params_pattern = r"PARAMETERS:\n({.*?})\n"
        file_content_str = "".join(self.file_contents)
        params_match = re.search(params_pattern, file_content_str, re.DOTALL)
        if params_match:
            params_block = params_match.group(1)
            return eval(params_block)
        return {}

    def parse_comments(self) -> str:
        file_content_str = "".join(self.file_contents)
        comment_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): Comment: (.+)"
        comments = re.findall(comment_pattern, file_content_str)
        return " ".join(comment[1] for comment in comments)

    @staticmethod
    def parse_direction(comment: str) -> Optional[str]:
        comment_lower = comment.lower()
        if "right" in comment_lower:
            return "RIGHT"
        elif "left" in comment_lower:
            return "LEFT"
        return None

    @abstractmethod
    def parse_trials_and_events(self) -> Optional[Dict[str, List]]:
        pass


class RPELogfileParser(LogfileParser):
    def parse_filename_components(self) -> Experiment:
        match = re.match(Config.FILENAME_PATTERNS["RPE"], self.file_name)
        if not match:
            raise ValueError(f"Filename {self.file_name} does not match the expected pattern.")

        components = match.groupdict()
        components["session_number"] = (
            int(float(components["session_number"]))
            if components["session_number"].lower() != "nan"
            else None
        )
        components["datetime"] = datetime.fromisoformat(components["datetime_str"])

        return Experiment(
            ExperimentID=None,
            Cohort=None,
            SubjectName=components["subject_name"],
            SubjectNumber=None,
            SessionNumber=components["session_number"],
            ExperimentType=components["experiment_type"],
            Comment=self.parse_comments(),
            DateTime=components["datetime"],
            LogFileName=self.file_name,
            Parameters=None,
        )

    def parse_trials_and_events(self) -> Optional[Dict[str, List]]:
        trials = []
        events = []
        trial_pattern = r"Current trial: (\d+)"
        file_content_str = "".join(self.file_contents)
        trials_split = re.split(trial_pattern, file_content_str)

        for i in range(1, len(trials_split), 2):
            trial_number = int(trials_split[i])
            trial_events = re.findall(Config.EVENT_PATTERN, trials_split[i + 1])
            trials.append({"TrialNumber": trial_number})
            for event_datetime, event_desc in trial_events:
                events.append(
                    {
                        "TrialNumber": trial_number,
                        "EventType": event_desc,
                        "EventDateTime": event_datetime,
                    }
                )

        if not trials or not events:
            logger.error(f"{self.file_name} contains no data - exclude from analysis.")
            return None

        return {"trials": trials, "events": events}


class CBLogfileParser(LogfileParser):
    def parse_filename_components(self) -> ExperimentCB:
        match = re.match(Config.FILENAME_PATTERNS["CB"], self.file_name)
        if not match:
            raise ValueError(f"Filename {self.file_name} does not match the expected pattern.")

        components = match.groupdict()
        components["session_number"] = (
            int(float(components["session_number"]))
            if components["session_number"].lower() != "nan"
            else None
        )
        components["datetime"] = datetime.fromisoformat(components["datetime_str"])

        has_criterion = "criterion count" in self.file_contents or "criterion type" in self.file_contents
        session_type = "training" if has_criterion else "test"

        return ExperimentCB(
            ExperimentID=None,
            Cohort=None,
            SubjectName=components["subject_name"],
            SubjectNumber=None,
            SessionNumber=components["session_number"],
            SessionType=session_type,
            ExperimentType=components["experiment_type"],
            Comment=self.parse_comments(),
            DateTime=components["datetime"],
            LogFileName=self.file_name,
            Parameters=None,
        )

    def parse_trials_and_events(self) -> Optional[Dict[str, List]]:
        file_content_str = "".join(self.file_contents)
        direction = self.parse_direction(self.parse_comments())
        trial_start_pattern = (
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): Green button pressed - system ready"
        )
        trial_start_match = re.search(trial_start_pattern, file_content_str)

        if not trial_start_match:
            logger.error(f"{self.file_name} does not contain a trial start time.")
            return None

        experiment_start_time = datetime.fromisoformat(trial_start_match.group(1))
        event_matches = re.findall(Config.CB_EVENT_PATTERN, file_content_str)

        experiment = self.parse_filename_components()
        trials = []
        responses = []
        events = []

        for event in event_matches:
            (
                event_datetime_str,
                event_desc,
                response_type,
                trial_number,
                trial_sub_type,
                criterion_type,
                _,
                response_time,
                _,
                _,
                criterion_count,
            ) = event
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
                    SessionType=experiment.SessionType,
                )
                trials.append(trial)

                if response_type == "GO" and response_time:
                    responses.append(
                        ResponseCB(
                            ResponseID=len(responses) + 1,
                            TrialID=trial.TrialID,
                            ResponseTime=float(response_time),
                            EventDateTime=event_datetime,
                        )
                    )

            events.append(
                EventCB(
                    EventID=len(events) + 1,
                    TrialID=trial.TrialID if trial_number else None,
                    EventType=event_desc,
                    EventTime=event_datetime,
                    ElapsedTime=(event_datetime - experiment_start_time).total_seconds(),
                )
            )

            if trials:
                trials[-1].TrialEndTime = event_datetime

        if not trials:
            logger.error(f"{self.file_name} contains no data - exclude from analysis.")
            return None

        return {"experiment": experiment, "trials": trials, "responses": responses, "events": events}


class DatabaseManager:
    def __init__(self, connection):
        self.connection = connection

    def insert_record(self, record: Union[BaseExperiment, BaseTrial, BaseEvent, ResponseCB]):
        table_name = record.__class__.__name__
        record_dict = asdict(record)

        columns = ", ".join(record_dict.keys())
        placeholders = ", ".join("?" for _ in record_dict)
        values = tuple(json.dumps(v) if isinstance(v, dict) else v for v in record_dict.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            self.connection.execute(query, values)
            self.connection.commit()
            logger.debug(f"Successfully inserted record into {table_name}")
        except Exception as e:
            logger.error(f"Error inserting into table {table_name}: {str(e)}")
            raise


class LogManager:
    def __init__(self, path: str, patterns: Optional[List[str]] = None, include: bool = True):
        self.path = Path(path)
        self.patterns = patterns or []
        self.include = include
        self.logfiles = []
        self.included_files = []
        self.excluded_files = []
        self.load_logfiles()

    def load_logfiles(self):
        all_files = set(self.path.glob(f"*{Config.LOG_FILE_EXT}"))
        matched_files = set()
        for pattern in self.patterns:
            matched_files.update(self.path.glob(pattern))

        if self.include:
            self.included_files = list(matched_files)
            self.excluded_files = list(all_files - matched_files)
        else:
            self.included_files = list(all_files - matched_files)
            self.excluded_files = list(matched_files)

        for file_path in self.included_files:
            parser_class = CBLogfileParser if "Experiment_" in file_path.name else RPELogfileParser
            self.logfiles.append(parser_class(str(file_path)))

    def handle_specific_files(self, file_names: List[str], include: bool = True):
        file_names_set = set(file_names)
        all_files = set(self.path.glob(f"*{Config.LOG_FILE_EXT}"))
        all_file_names = {file.name for file in all_files}

        matched_files = file_names_set & all_file_names
        unmatched_files = file_names_set - all_file_names

        for file_name in sorted(matched_files):
            if include:
                if file_name not in self.included_files:
                    self.included_files.append(self.path / file_name)
                    logger.info(f"File {file_name} has been included.")
            else:
                if file_name in self.included_files:
                    self.included_files.remove(self.path / file_name)
                    self.excluded_files.append(self.path / file_name)
                    logger.info(f"File {file_name} has been excluded.")

        for file_name in unmatched_files:
            logger.warning(f"File {file_name} not found in the path.")

        self.load_logfiles()


def create_filename_components_dataframe(self, file_list: List[str]) -> pd.DataFrame:
    """
    Create a DataFrame containing filename components for RPE experiments.

    Args:
        file_list (List[str]): List of filenames to process.

    Returns:
        pd.DataFrame: A DataFrame containing parsed filename components.
    """
    data = {
        "original_filename": [],
        "suffix": [],
        "datetime": [],
        "subject_name": [],
        "session_number": [],
        "experiment_type": [],
    }

    for file_name in file_list:
        try:
            experiment = Logfile(file_name, "").parse_filename_components()
            if experiment is not None:
                data["original_filename"].append(experiment.LogFileName)
                data["suffix"].append("Experiment")
                data["datetime"].append(experiment.DateTime)
                data["subject_name"].append(experiment.SubjectName)
                data["session_number"].append(experiment.SessionNumber)
                data["experiment_type"].append(experiment.ExperimentType)
            else:
                logger.info(f"Can't match {file_name}")
        except ValueError as e:
            logger.info(f"Error processing file {file_name}: {e}")

    return pd.DataFrame(data)


def create_filename_components_dataframe_cog_bias(self, file_list: List[str]) -> pd.DataFrame:
    """
    Create a DataFrame containing filename components for cognitive bias experiments.

    Args:
        file_list (List[str]): List of filenames to process.

    Returns:
        pd.DataFrame: A DataFrame containing parsed filename components.
    """
    data = {
        "original_filename": [],
        "suffix": [],
        "datetime": [],
        "subject_name": [],
        "session_number": [],
        "experiment_type": [],
        "session_type": [],  # Added for cognitive bias experiments
    }

    for file_name in file_list:
        try:
            experiment = Logfile(file_name, "").parse_filename_components_cog_bias()
            if experiment is not None:
                data["original_filename"].append(experiment.LogFileName)
                data["suffix"].append("Experiment")
                data["datetime"].append(experiment.DateTime)
                data["subject_name"].append(experiment.SubjectName)
                data["session_number"].append(experiment.SessionNumber)
                data["experiment_type"].append(experiment.ExperimentType)
                data["session_type"].append(experiment.SessionType)
            else:
                logger.info(f"Can't match {file_name}")
        except ValueError as e:
            logger.info(f"Error processing file {file_name}: {e}")

    return pd.DataFrame(data)
