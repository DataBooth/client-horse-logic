/* Note that (data)classes are actually defined in logfiles.py
 */

/* class Experiment:
    ExperimentID: int
    Cohort: str
    SubjectName: str
    SubjectNumber: int
    SessionNumber: int
    ExperimentType: str
    Comment: Optional[str]
    DateTime: datetime
    LogFileName: str
    Parameters: Dict */

CREATE OR REPLACE TABLE Experiments (
    ExperimentID INTEGER PRIMARY KEY,
    Cohort VARCHAR,
    SubjectName VARCHAR,
    SubjectNumber INTEGER,
    SessionNumber INTEGER,
    ExperimentType VARCHAR,
    Comment VARCHAR,
    DateTime TIMESTAMP,
    LogFileName VARCHAR,
    Parameters JSON
);


/* class Trial:
    TrialID: int
    ExperimentID: int
    TrialNumber: int
    TrialStartTime: datetime
    TrialEndTime: datetime */

CREATE OR REPLACE TABLE Trials (
    TrialID INTEGER PRIMARY KEY,
    ExperimentID INTEGER,
    TrialNumber INTEGER,
    TrialStartTime TIMESTAMP,
    TrialEndTime TIMESTAMP,
    FOREIGN KEY (ExperimentID) REFERENCES Experiments (ExperimentID)
);


/* class Event:
    EventID: int
    TrialID: int
    EventNumber: int
    EventTime: datetime
    EventType: str
    EventElapsedTime: float */

CREATE OR REPLACE TABLE Events (
    EventID INTEGER PRIMARY KEY,
    TrialID INTEGER,
    EventNumber INTEGER,
    EventTime TIMESTAMP,
    EventType VARCHAR,
    EventElapsedTime DOUBLE,
    FOREIGN KEY (TrialID) REFERENCES Trials (TrialID)
);
