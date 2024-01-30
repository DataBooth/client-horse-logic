
CREATE TABLE Experiments (
    ExperimentID INTEGER PRIMARY KEY,
    SubjectName VARCHAR,
    SessionNumber INTEGER,
    ExperimentType VARCHAR,
    Comment VARCHAR,
    DateTime TIMESTAMP,
    LogFileName VARCHAR
);

CREATE TABLE Parameters (
    ParameterID INTEGER PRIMARY KEY,
    ExperimentID INTEGER,
    ParameterName VARCHAR,
    ParameterValue VARCHAR,
    FOREIGN KEY (ExperimentID) REFERENCES Experiments (ExperimentID)
);

CREATE TABLE Trials (
    TrialID INTEGER PRIMARY KEY,
    ExperimentID INTEGER,
    TrialNumber INTEGER,
    StartToneDateTime TIMESTAMP,
    FOREIGN KEY (ExperimentID) REFERENCES Experiments (ExperimentID)
);

CREATE TABLE Events (
    EventID INTEGER PRIMARY KEY,
    TrialID INTEGER,
    EventType VARCHAR,
    EventDateTime TIMESTAMP,
    FOREIGN KEY (TrialID) REFERENCES Trials (TrialID)
);
