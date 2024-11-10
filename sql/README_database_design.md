## Database Design - Initial Considerations

To parse the log files and model the data in a normalised database structure, I recommend the following approach:

Parsing Approach

1. Read the File: Open the log file and read it line by line.
2. Extract PARAMETERS: Identify the PARAMETERS block and parse it using ast.literal_eval or a regular expression to extract the dictionary.
3. Process Metadata: Identify and extract metadata lines (Comment, Data directory, Log file, Measurement file) using regular expressions, ignoring the date-time part.
4. Capture Trials and Events: For the trials and events, use a state machine-like approach where you:
   - Detect the start of a trial using a pattern (e.g., "Subject [subject_name] - Session [session_number] started...").
   - Capture relevant events and their timestamps following the trial start until the next trial begins.
5. Handle Different Experiment Types: If different experiment types have different events, you might need a configurable parser that can be tailored to each experiment type's pattern.

Clarifying Questions:

1. Event Types: What are all the possible event types that need to be captured for each trial, and how do they differ by experiment type?
2. Data Consistency: Is the log file format consistent across all files and experiment types?
3. Error Handling: How should the parser handle malformed lines or unexpected content in the log files?
4. Performance: Are there performance considerations, such as the number of log files or their sizes?

Database Modeling:

For a normalised database structure, you could consider the following tables:

1. Experiments Table: Stores metadata about each experiment.
   - Columns: ExperimentID, SubjectName, SessionNumber, ExperimentType, Comment, DataDirectory, LogFileName, MeasurementFileName

2. Parameters Table: Stores PARAMETERS for each experiment.
   - Columns: ExperimentID, ParameterName, ParameterValue

3. Trials Table: Stores information about each trial within an experiment.
   - Columns: TrialID, ExperimentID, TrialNumber, StartToneDateTime

4. Events Table: Stores events that occur during each trial.
   - Columns: EventID, TrialID, EventType, EventDateTime
Normalized Database Structure:

- Experiments:
- ExperimentID (Primary Key)
- SubjectName
- SessionNumber
- ExperimentType
- Comment
- DataDirectory
- LogFileName
- MeasurementFileName

- Parameters:
- ParameterID (Primary Key)
- ExperimentID (Foreign Key)
- ParameterName
- ParameterValue

- Trials:
- TrialID (Primary Key)
- ExperimentID (Foreign Key)
- TrialNumber
- StartToneDateTime

- Events:
- EventID (Primary Key)
- TrialID (Foreign Key)
- EventType
- EventDateTime

This structure allows you to link parameters and events back to their respective experiments and trials, maintaining referential integrity and enabling complex queries. Each event is recorded with its own timestamp, allowing for detailed analysis of the trial timeline.

## RPE Experiments - Data Model

```{mermaid}
erDiagram
    Experiment ||--o{ Trial : contains
    Trial ||--o{ Event : contains

    Experiment {
        int ExperimentID PK
        string Cohort
        string SubjectName
        int SubjectNumber
        int SessionNumber
        string ExperimentType
        string Comment
        datetime DateTime
        string LogFileName
        dict Parameters
    }

    Trial {
        int TrialID PK
        int ExperimentID FK
        int TrialNumber
        datetime TrialStartTime
        datetime TrialEndTime
    }

    Event {
        int EventID PK
        int TrialID FK
        int EventNumber
        datetime EventTime
        string EventType
        float EventElapsedTime
    }
```

## CB Experiments - Data Model

```{mermaid}
erDiagram
    ExperimentCB ||--o{ TrialCB : contains
    TrialCB ||--o{ EventCB : contains

    ExperimentCB {
        int ExperimentID PK
        string Cohort
        string SubjectName
        int SubjectNumber
        int SessionNumber
        string ExperimentType
        string Comment
        datetime DateTime
        string LogFileName
        dict Parameters
    }

    TrialCB {
        int TrialID PK
        int ExperimentID FK
        int TrialNumber
        datetime TrialStartTime
        datetime TrialEndTime
    }

    EventCB {
        int EventID PK
        int TrialID FK
        int EventNumber
        datetime EventTime
        string EventType
        float EventElapsedTime
    }
```