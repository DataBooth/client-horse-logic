-- class ExperimentCB:
--     ExperimentID: int
--     Cohort: str
--     SubjectName: str
--     SubjectNumber: int
--     SessionNumber: int
--     SessionType: str  # New field: "training" or "test"
--     ExperimentType: str
--     Comment: Optional[str]
--     DateTime: datetime
--     LogFileName: str
--     Parameters: Dict



CREATE OR REPLACE TABLE ExperimentCBs (
    ExperimentID INTEGER PRIMARY KEY,
    Cohort VARCHAR,
    SubjectName VARCHAR,
    SubjectNumber INTEGER,
    SessionNumber INTEGER,
    SessionType VARCHAR,  -- New field
    ExperimentType VARCHAR,
    Comment VARCHAR,
    DateTime TIMESTAMP,
    LogFileName VARCHAR,
    Parameters JSON
);

-- class TrialCB:
--     TrialID: int
--     ExperimentID: int
--     TrialNumber: int
--     ResponseType: str
--     TrialSubType: str
--     Direction: str
--     CriterionType: Optional[str]
--     CriterionCount: Optional[float]
--     TrialStartTime: datetime
--     TrialEndTime: datetime
--     SessionType: str  # New field: "training" or "test"


CREATE OR REPLACE TABLE TrialCBs (
    TrialID INTEGER PRIMARY KEY,
    ExperimentID INTEGER,
    TrialNumber INTEGER,
    ResponseType VARCHAR,
    TrialSubType VARCHAR,
    Direction VARCHAR,
    CriterionType VARCHAR,
    CriterionCount DOUBLE,
    TrialStartTime TIMESTAMP,
    TrialEndTime TIMESTAMP,
    SessionType VARCHAR,  -- New field
    FOREIGN KEY (ExperimentID) REFERENCES ExperimentCBs (ExperimentID)
);

-- class ResponseCB:
--     ResponseID: int
--     TrialID: int
--     ResponseTime: Optional[float]
--     EventDateTime: datetime

CREATE OR REPLACE TABLE ResponseCBs (
    ResponseID INTEGER PRIMARY KEY,
    TrialID INTEGER,
    ResponseTime DOUBLE,
    EventDateTime TIMESTAMP,
    FOREIGN KEY (TrialID) REFERENCES TrialCBs (TrialID)
);

-- class EventCB:
--     EventID: int
--     TrialID: int
--     EventType: str
--     EventTime: datetime
--     ElapsedTime: float

CREATE OR REPLACE TABLE EventCBs (
    EventID INTEGER PRIMARY KEY,
    TrialID INTEGER,
    EventType VARCHAR,
    EventTime TIMESTAMP,
    ElapsedTime DOUBLE,
    FOREIGN KEY (TrialID) REFERENCES TrialCBs (TrialID)
);
