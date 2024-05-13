
CREATE OR REPLACE TABLE Experiments (
    ExperimentID INTEGER PRIMARY KEY,
    SubjectName VARCHAR,
    SessionNumber INTEGER,
    ExperimentType VARCHAR,
    Comment VARCHAR,
    DateTime TIMESTAMP,
    LogFileName VARCHAR
);

CREATE OR REPLACE TABLE Parameters (
    ParameterID INTEGER PRIMARY KEY,
    ExperimentID INTEGER,
    ParameterName VARCHAR,
    ParameterValue VARCHAR,
    FOREIGN KEY (ExperimentID) REFERENCES Experiments (ExperimentID)
);

CREATE OR REPLACE TABLE Trials (
    TrialID INTEGER PRIMARY KEY,
    ExperimentID INTEGER,
    TrialNumber INTEGER,
    StartToneDateTime TIMESTAMP,
    FOREIGN KEY (ExperimentID) REFERENCES Experiments (ExperimentID)
);

CREATE OR REPLACE TABLE Events (
    EventID INTEGER PRIMARY KEY,
    TrialID INTEGER,
    EventType VARCHAR,
    EventDateTime TIMESTAMP,
    FOREIGN KEY (TrialID) REFERENCES Trials (TrialID)
);
