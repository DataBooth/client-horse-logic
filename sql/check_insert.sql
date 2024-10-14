CREATE SEQUENCE seq_id START 1;

CREATE
OR
REPLACE
TABLE Experiments (
    ExperimentID INTEGER PRIMARY KEY, SubjectName VARCHAR, SessionNumber INTEGER, ExperimentType VARCHAR, Comment VARCHAR, DataDirectory VARCHAR, LogFileName VARCHAR
);

INSERT INTO
    Experiments
VALUES (nextval('seq_id'), 'subject_name', 1, 'experiment_type', 'comment', 'data_path', 'log_file_name');
