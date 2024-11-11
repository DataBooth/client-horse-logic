### CB Experiments - Entity Relationship Diagram (ERD)

The Entity-Relationship Diagram (ERD) below can be summarised as follows:

1. **Core Data Tables**:
   - `ExperimentCBs`: This is the main table that stores information about each experiment. It includes details like the subject's name, experiment date, and type of experiment.
   - `TrialCBs`: This table contains information about individual trials within each experiment. It's connected to ExperimentCBs because each experiment consists of multiple trials.
   - `ResponseCBs`: This table records the responses given during each trial. It's linked to `TrialCBs` because each trial can have a response.
   - `EventCBs`: This table stores events that occur during trials. It's also connected to `TrialCBs` as events are associated with specific trials.

2. **Supporting Tables**:
   - `SubjectCBs`: This table holds information about the subjects (e.g. horses) involved in the experiments. It's connected to `ExperimentCBs` as each experiment involves a specific subject.
   - `Corrections`: This is a special table that contains information about corrections or additions that need to be made to the existing data (which is a consolidated table of the information in the Corrections workbook).

3. **Correction Process**:
   - `CorrectionsSplit`: This view breaks down the `Corrections` table into more specific pieces of information.
   - `AddExperiments` and `ReformattedAddExperiments`: These views identify and format new experiments that need to be added to the database. It turns out there is only one experiment to add.
   - `AddTrials`: This view identifies new trials that need to be added to existing experiments.
   - `CorrectTrials`: This view shows what corrections need to be made to existing trials.

4. **Corrected Data Views**:
   - `ExperimentCBsCorrected`: This view combines the original experiment data with any new experiments that need to be added.
   - `TrialCBsCorrected`: This view shows all trials, including both original and new ones, with any necessary corrections applied.
   - `ResponseCBsCorrected`: This view presents all responses, including both original and new ones, with any necessary corrections applied.
   - `EventCBsCorrected`: This view shows all events, including both original and new ones, with any necessary additions for new trials.

The overall data flow is:

1. Original data is stored in the core tables (`ExperimentCBs`, `TrialCBs`, `ResponseCBs`, `EventCBs`).
2. Corrections and additions are specified in the `Corrections` table.
3. Various views process these corrections and additions.
4. The final corrected views (`ExperimentCBsCorrected`, `TrialCBsCorrected`, `ResponseCBsCorrected`, `EventCBsCorrected`) present the updated and corrected data for use in subsequent analysis.

```{mermaid}
erDiagram
    ExperimentCBs ||--o{ TrialCBs : contains
    TrialCBs ||--o{ ResponseCBs : has
    TrialCBs ||--o{ EventCBs : has
    ExperimentCBs ||--o{ SubjectCBs : aggregates
    Corrections ||--|{ CorrectionsSplit : splits
    Corrections ||--o{ AddExperiments : identifies
    Corrections ||--o{ AddTrials : identifies
    Corrections ||--o{ CorrectTrials : informs
    Corrections ||--o{ ResponseCBsCorrected : informs
    ExperimentCBs ||--o{ ExperimentCBsCorrected : corrects
    TrialCBs ||--o{ TrialCBsCorrected : corrects
    ResponseCBs ||--o{ ResponseCBsCorrected : corrects
    EventCBs ||--o{ EventCBsCorrected : corrects
    ExperimentCBsCorrected ||--o{ TrialCBsCorrected : contains
    TrialCBsCorrected ||--o{ ResponseCBsCorrected : has
    TrialCBsCorrected ||--o{ EventCBsCorrected : has
    AddExperiments ||--o{ ReformattedAddExperiments : reformats
    ReformattedAddExperiments ||--o{ ExperimentCBsCorrected : adds
    AddTrials ||--o{ TrialCBsCorrected : adds
    CorrectTrials ||--o{ TrialCBsCorrected : informs
    CorrectionsSplit ||--o{ CorrectTrials : informs
    CorrectionsSplit ||--o{ ResponseCBsCorrected : informs

    ExperimentCBs {
        int ExperimentID PK
        string LogFileName
    }

    TrialCBs {
        int TrialID PK
        int ExperimentID FK
        int TrialNumber
        string ResponseType
    }

    ResponseCBs {
        int ResponseID PK
        int TrialID FK
        float ResponseTime
    }

    EventCBs {
        int EventID PK
        int TrialID FK
    }

    Corrections {
        string LogFilename
        int TrialNumber
        string ResponseType
        float ResponseTime
    }

    CorrectionsSplit {
        string LogFilename
        int TrialNumber
        string TableToCorrect
        string FieldToCorrect
        string ValueToCorrect
    }

    ExperimentCBsCorrected {
        int ExperimentID PK
        string DataSource
    }

    TrialCBsCorrected {
        int TrialID PK
        string CorrectedFlag
    }

    ResponseCBsCorrected {
        int ResponseID PK
        string CorrectedFlag
    }

    EventCBsCorrected {
        int EventID PK
        string CorrectedFlag
    }

    AddExperiments {
        string LogFilename
        string DataSource
    }

    ReformattedAddExperiments {
        int ExperimentID PK
        string DataSource
    }

    AddTrials {
        int ExperimentID FK
        int TrialNumber
        string CorrectedFlag
    }

    CorrectTrials {
        int TrialID PK
        string CorrectedFlag
    }
```

### `ExperimentCBsCorrected`

This view combines original experiment data with new experiments that need to be added:

- It starts with the original experiment data from ExperimentCBs.
- It looks at a list of new experiments (AddExperiments) that need to be added derived from the `Corrections` table.
- These new experiments are reformatted (`ReformattedAddExperiments`) to match the structure of existing experiments.
- The view then combines the original experiments with these new, reformatted experiments.
- It also looks up information from the `SubjectCBs` table to fill in some details about the properties of the new experiments.

```{mermaid}
erDiagram
    ExperimentCBs ||--|{ ExperimentCBsCorrected : "original data"
    AddExperiments ||--|{ ReformattedAddExperiments : reformats
    ReformattedAddExperiments ||--|{ ExperimentCBsCorrected : "adds new experiments"
    Corrections ||--|{ AddExperiments : "identifies new experiments"
    SubjectCBs ||--o{ ReformattedAddExperiments : "provides subject info"

    ExperimentCBs {
        int ExperimentID PK
        string LogFileName
        string DataSource
    }
    AddExperiments {
        string LogFilename
        string DataSource
    }
    ReformattedAddExperiments {
        int ExperimentID PK
        string LogFilename
        string DataSource
    }
    ExperimentCBsCorrected {
        int ExperimentID PK
        string LogFileName
        string DataSource
    }
    Corrections {
        string LogFilename
    }
    SubjectCBs {
        string SubjectName PK
        int SubjectNumber
        string Direction
    }
```

### `TrialCBsCorrected`

This view handles both existing trials and any corrections needed and new trials that need to be added (due to any new experiments):

- It starts with the original trial data from `TrialCBs`.
- It applies corrections to existing trials (`CorrectTrials`), fixing the `ResponseType`.
- It also adds completely new trials (`AddTrials`) for new experiments.
- The view combines the corrected existing trials and the new trials.
- It ensures that each trial has a unique identifier.

```{mermaid}
erDiagram
    TrialCBs ||--|{ CorrectTrials : "corrects existing trials"
    Corrections ||--|{ AddTrials : "identifies new trials"
    CorrectTrials ||--|{ TrialCBsCorrected : combines
    AddTrials ||--|{ TrialCBsCorrected : combines
    ExperimentCBsCorrected ||--o{ AddTrials : "links new trials"
    ExperimentCBsCorrected ||--o{ CorrectTrials : "links existing trials"
    ResponseCBs ||--o{ CorrectTrials : "provides ResponseTime for info"

    TrialCBs {
        int TrialID PK
        int ExperimentID FK
        string ResponseType
    }
    CorrectTrials {
        int TrialID PK
        int ExperimentID FK
        string ResponseType
        string CorrectedFlag
    }
    AddTrials {
        int ExperimentID FK
        int TrialNumber
        string ResponseType
        string CorrectedFlag
    }
    TrialCBsCorrected {
        int TrialID PK
        int ExperimentID FK
        string ResponseType
        string CorrectedFlag
    }
    Corrections {
        string LogFilename
        int TrialNumber
        string ResponseType
    }
    ExperimentCBsCorrected {
        int ExperimentID PK
        string LogFileName
    }
    ResponseCBs {
        int ResponseID PK
        int TrialID FK
        float ResponseTime
    }
```

### `ResponseCBsCorrected`

This view deals with the responses recorded during trials:

- It starts with the original response data from `ResponseCBs`.
- It applies any corrections to existing responses as necessary, fixing `ResponseTime`.
- It adds new responses for trials in new experiments.
- The view combines the corrected existing responses and the new responses.
- It uses information from the `TrialCBsCorrected` and `ExperimentCBsCorrected` views to ensure everything lines up correctly.

```{mermaid}
erDiagram
    ResponseCBs ||--|{ ExistingResponses : "corrects existing responses"
    Corrections ||--|{ NewResponses : "adds new responses"
    ExistingResponses ||--|{ ResponseCBsCorrected : combines
    NewResponses ||--|{ ResponseCBsCorrected : combines
    TrialCBsCorrected ||--o{ NewResponses : "links new responses"
    TrialCBsCorrected ||--o{ ExistingResponses : "links existing responses"
    ExperimentCBsCorrected ||--o{ NewResponses : "links to experiments"
    CorrectionsSplit ||--o{ ExistingResponses : "provides correction info"

    ResponseCBs {
        int ResponseID PK
        int TrialID FK
        float ResponseTime
    }
    ExistingResponses {
        int ResponseID PK
        int TrialID FK
        float ResponseTime
        string CorrectedFlag
    }
    NewResponses {
        int TrialID FK
        float ResponseTime
        string CorrectedFlag
    }
    ResponseCBsCorrected {
        int ResponseID PK
        int TrialID FK
        float ResponseTime
        string CorrectedFlag
    }
    Corrections {
        string LogFilename
        int TrialNumber
        float ResponseTime
    }
    TrialCBsCorrected {
        int TrialID PK
        int ExperimentID FK
    }
    ExperimentCBsCorrected {
        int ExperimentID PK
        string LogFileName
    }
    CorrectionsSplit {
        string LogFilename
        int TrialNumber
        string TableToCorrect
        string FieldToCorrect
        string ValueToCorrect
    }
```

### `EventCBsCorrected`

This view handles events that occur during trials:

- It starts with the original event data from `EventCBs`.
- It keeps all existing events as is.
- For new trials that were added, it creates placeholder events (`NewTrialEvents`).
- The view combines the existing events and the placeholder events for new trials

```{mermaid}
erDiagram
    EventCBs ||--|{ ExistingEvents : "includes existing events"
    TrialCBsCorrected ||--|{ NewTrialEvents : "generates placeholder events"
    ExistingEvents ||--|{ EventCBsCorrected : combines
    NewTrialEvents ||--|{ EventCBsCorrected : combines

    EventCBs {
        int EventID PK
        int TrialID FK
        string EventType
        datetime EventTime
        float ElapsedTime
    }
    ExistingEvents {
        int EventID PK
        int TrialID FK
        string EventType
        datetime EventTime
        float ElapsedTime
        string CorrectedFlag
    }
    NewTrialEvents {
        int TrialID FK
        string CorrectedFlag
    }
    EventCBsCorrected {
        int EventID PK
        int TrialID FK
        string EventType
        datetime EventTime
        float ElapsedTime
        string CorrectedFlag
    }
    TrialCBsCorrected {
        int TrialID PK
        string CorrectedFlag
    }
```