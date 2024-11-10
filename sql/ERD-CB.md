### CB Experiments - Entity Relationship Diagram (ERD)

```{mermaid}
erDiagram
    ExperimentCBs ||--o{ TrialCBs : contains
    TrialCBs ||--o{ ResponseCBs : has
    TrialCBs ||--o{ EventCBs : has
    ExperimentCBs ||--o{ SubjectCBs : aggregates
    Corrections ||--|{ CorrectionsSplit : splits
    ExperimentCBs ||--o{ ExperimentCBsCorrected : corrects
    TrialCBs ||--o{ TrialCBsCorrected : corrects
    ResponseCBs ||--o{ ResponseCBsCorrected : corrects
    EventCBs ||--o{ EventCBsCorrected : corrects
    ExperimentCBsCorrected ||--o{ TrialCBsCorrected : contains
    TrialCBsCorrected ||--o{ ResponseCBsCorrected : has
    TrialCBsCorrected ||--o{ EventCBsCorrected : has

    ExperimentCBs {
        int ExperimentID PK
        string Cohort
        string SubjectName
        int SubjectNumber
        int SessionNumber
        string SessionType
        string ExperimentType
        string Direction
        string Comment
        datetime DateTime
        string LogFileName
        json Parameters
    }

    TrialCBs {
        int TrialID PK
        int ExperimentID FK
        int TrialNumber
        string ResponseType
        string TrialSubType
        string CriterionType
        int CriterionCount
        datetime TrialStartTime
        datetime TrialEndTime
    }

    ResponseCBs {
        int ResponseID PK
        int TrialID FK
        float ResponseTime
        datetime EventDateTime
    }

    EventCBs {
        int EventID PK
        int TrialID FK
        string EventType
        datetime EventTime
        float ElapsedTime
    }

    SubjectCBs {
        string SubjectName PK
        int SubjectNumber
        string Cohort
        string Direction
        int TotalExperiments
    }

    Corrections {
        string Cohort
        date ExperimentDate
        string SessionType
        string SubjectName
        int TrialNumber
        string TrialType
        float ResponseTime
        string ResponseType
        string Comment
        string LogFilename
        string CorrectTable
        string CorrectField
        string CurrentValue
        string CorrectValue
    }

    CorrectionsSplit {
        string TableToCorrect
        string FieldToCorrect
        string ValueToCorrect
    }

    ExperimentCBsCorrected {
        int ExperimentID PK
        string Cohort
        string SubjectName
        int SubjectNumber
        int SessionNumber
        string SessionType
        string ExperimentType
        string Direction
        string Comment
        datetime DateTime
        string LogFileName
        json Parameters
        string DataSource
    }

    TrialCBsCorrected {
        int TrialID PK
        int ExperimentID FK
        int TrialNumber
        string ResponseType
        string TrialSubType
        string CriterionType
        int CriterionCount
        datetime TrialStartTime
        datetime TrialEndTime
        string CorrectedFlag
    }

    ResponseCBsCorrected {
        int ResponseID PK
        int TrialID FK
        float ResponseTime
        datetime EventDateTime
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
```

### `ExperimentCBsCorrected`

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

```{mermaid}
erDiagram
    TrialCBs ||--|{ CorrectTrials : "corrects existing trials"
    Corrections ||--|{ AddTrials : "identifies new trials"
    CorrectTrials ||--|{ TrialCBsCorrected : combines
    AddTrials ||--|{ TrialCBsCorrected : combines
    ExperimentCBsCorrected ||--o{ AddTrials : "links new trials"
    ExperimentCBsCorrected ||--o{ CorrectTrials : "links existing trials"

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
```

### `ResponseCBsCorrected`

```{mermaid}
erDiagram
    ResponseCBs ||--|{ ExistingResponses : "corrects existing responses"
    Corrections ||--|{ NewResponses : "adds new responses"
    ExistingResponses ||--|{ ResponseCBsCorrected : combines
    NewResponses ||--|{ ResponseCBsCorrected : combines
    TrialCBsCorrected ||--o{ NewResponses : "links new responses"
    TrialCBsCorrected ||--o{ ExistingResponses : "links existing responses"

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
```

### `EventCBsCorrected`

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