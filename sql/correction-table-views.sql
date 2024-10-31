CREATE OR REPLACE TABLE Corrections (
    Cohort VARCHAR,
    ExperimentDate DATE,
    SessionType VARCHAR,
    SubjectName VARCHAR,
    TrialNumber INTEGER,
    TrialType VARCHAR,
    ResponseTime DOUBLE,
    ResponseType VARCHAR,
    Comment VARCHAR,
    LogFilename VARCHAR,
    CorrectTable VARCHAR,
    CorrectField VARCHAR,
    CurrentValue VARCHAR,
    CorrectValue VARCHAR
);

ALTER TABLE Corrections DROP COLUMN CurrentValue;

CREATE OR REPLACE VIEW CorrectionsSplit AS
SELECT 
    Cohort,
    ExperimentDate,
    SessionType,
    SubjectName,
    TrialNumber,
    TrialType,
    ResponseTime,
    ResponseType,
    Comment,
    LogFilename,
    TRIM(UNNEST(STRING_TO_ARRAY(CorrectTable, ','))) AS TableToCorrect,
    TRIM(UNNEST(STRING_TO_ARRAY(CorrectField, ','))) AS FieldToCorrect,
    TRIM(UNNEST(STRING_TO_ARRAY(CorrectValue, ','))) AS ValueToCorrect
FROM Corrections;

CREATE OR REPLACE VIEW CorrectionWithExistingValues AS
SELECT 
    sc.*,
    CASE 
        WHEN sc.TableToCorrect = 'TrialCBs' AND sc.FieldToCorrect = 'ResponseType' THEN
            t.ResponseType
        ELSE
            NULL
    END AS ExistingResponseType,
    CASE 
        WHEN sc.TableToCorrect = 'ResponseCBs' AND sc.FieldToCorrect = 'ResponseTime' THEN
            r.ResponseTime
        ELSE
            NULL
    END AS ExistingResponseTime,
    CASE
        WHEN sc.TableToCorrect = 'TrialCBs' AND sc.FieldToCorrect = 'ResponseType' THEN
            CASE WHEN t.ResponseType = sc.ValueToCorrect THEN 'EQUAL' ELSE 'NOT EQUAL' END
        WHEN sc.TableToCorrect = 'ResponseCBs' AND sc.FieldToCorrect = 'ResponseTime' THEN
            CASE WHEN CAST(r.ResponseTime AS VARCHAR) = sc.ValueToCorrect THEN 'EQUAL' ELSE 'NOT EQUAL' END
        ELSE
            'UNKNOWN'
    END AS ComparisonResult
FROM 
    CorrectionsSplit  sc
LEFT JOIN ExperimentCBs e ON sc.LogFilename = e.LogFileName
LEFT JOIN TrialCBs t ON e.ExperimentID = t.ExperimentID AND sc.TrialNumber = t.TrialNumber
LEFT JOIN ResponseCBs r ON t.TrialID = r.TrialID
WHERE 
    (sc.TableToCorrect = 'TrialCBs' AND sc.FieldToCorrect = 'ResponseType')
    OR (sc.TableToCorrect = 'ResponseCBs' AND sc.FieldToCorrect = 'ResponseTime')


CREATE OR REPLACE VIEW ExperimentCBsCorrected AS
WITH NewExperiments AS (
    SELECT DISTINCT
        c.LogFilename,
        c.Cohort,
        c.ExperimentDate,
        c.SessionType,
        c.SubjectName
    FROM 
        Corrections c
    LEFT JOIN 
        ExperimentCBs e ON c.LogFilename = e.LogFileName
    WHERE 
        e.LogFileName IS NULL
),
MaxExperimentID AS (
    SELECT COALESCE(MAX(ExperimentID), 0) AS MaxID
    FROM ExperimentCBs
)
SELECT 
    e.ExperimentID,
    e.Cohort,
    e.DateTime,
    e.SessionType,
    e.SubjectName,
    e.LogFileName,
    'ExperimentCBs' AS DataSource
FROM 
    ExperimentCBs e

UNION ALL

SELECT 
    ROW_NUMBER() OVER (ORDER BY ne.LogFilename) + m.MaxID AS ExperimentID,
    ne.Cohort,
    CAST(ne.ExperimentDate AS TIMESTAMP) AS DateTime,
    ne.SessionType,
    ne.SubjectName,
    ne.LogFilename AS LogFileName,
    'Corrections xlsx: ADD' AS DataSource
FROM 
    NewExperiments ne
CROSS JOIN 
    MaxExperimentID m
ORDER BY 
    ExperimentID;


CREATE OR REPLACE VIEW TrialCBsCorrected AS
WITH NewTrials AS (
    SELECT 
        NULL AS TrialID,
        e.ExperimentID,
        c.TrialNumber,
        c.TrialType AS TrialSubType,
        c.ResponseType,
        'Criterion' AS CriterionType, -- You may need to adjust this if you have this information
        0 AS CriterionCount, -- You may need to adjust this if you have this information
        NULL AS TrialStartTime, -- You may need to adjust this if you have this information
        NULL AS TrialEndTime, -- You may need to adjust this if you have this information
        'Added from Corrections' AS CorrectedFlag
    FROM 
        Corrections c
    JOIN 
        ExperimentCBsCorrected e ON c.LogFilename = e.LogFileName
    WHERE 
        e.DataSource = 'Corrections xlsx: ADD'
),
ExistingTrials AS (
    SELECT 
        t.TrialID,
        t.ExperimentID,
        t.TrialNumber,
        t.TrialSubType,
        COALESCE(cs.ValueToCorrect, t.ResponseType) AS ResponseType,
        t.CriterionType,
        t.CriterionCount,
        t.TrialStartTime,
        t.TrialEndTime,
        CASE 
            WHEN cs.ValueToCorrect IS NOT NULL THEN 'Corrected'
            ELSE 'Original'
        END AS CorrectedFlag
    FROM 
        TrialCBs t
    LEFT JOIN ExperimentCBsCorrected e ON t.ExperimentID = e.ExperimentID
    LEFT JOIN CorrectionsSplit cs ON e.LogFileName = cs.LogFilename 
        AND t.TrialNumber = cs.TrialNumber
        AND cs.TableToCorrect = 'TrialCBs'
        AND cs.FieldToCorrect = 'ResponseType'
)
SELECT 
    COALESCE(TrialID, ROW_NUMBER() OVER (ORDER BY ExperimentID, TrialNumber) + (SELECT MAX(TrialID) FROM TrialCBs)) AS TrialID,
    ExperimentID,
    TrialNumber,
    TrialSubType,
    ResponseType,
    CriterionType,
    CriterionCount,
    TrialStartTime,
    TrialEndTime,
    CorrectedFlag
FROM (
    SELECT * FROM ExistingTrials
    UNION ALL
    SELECT * FROM NewTrials
) AllTrials
ORDER BY ExperimentID, TrialNumber;


CREATE OR REPLACE VIEW ResponseCBsCorrected AS
WITH NewResponses AS (
    SELECT 
        NULL AS ResponseID,
        t.TrialID,
        CAST(c.ResponseTime AS DOUBLE) AS ResponseTime,
        NULL AS EventDateTime, -- You may need to adjust this if you have this information
        'Added from Corrections' AS CorrectedFlag
    FROM 
        TrialCBsCorrected t
    JOIN 
        ExperimentCBsCorrected e ON t.ExperimentID = e.ExperimentID
    JOIN 
        Corrections c ON e.LogFileName = c.LogFilename AND t.TrialNumber = c.TrialNumber
    WHERE 
        e.DataSource = 'Corrections xlsx: ADD'
),
ExistingResponses AS (
    SELECT 
        r.ResponseID,
        r.TrialID,
        CASE 
            WHEN cs.ValueToCorrect IS NOT NULL AND cs.ValueToCorrect != '' THEN 
                CAST(cs.ValueToCorrect AS DOUBLE)
            ELSE 
                r.ResponseTime
        END AS ResponseTime,
        r.EventDateTime,
        CASE 
            WHEN cs.ValueToCorrect IS NOT NULL THEN 'Corrected'
            ELSE 'Original'
        END AS CorrectedFlag
    FROM 
        ResponseCBs r
    JOIN TrialCBsCorrected t ON r.TrialID = t.TrialID
    LEFT JOIN ExperimentCBsCorrected e ON t.ExperimentID = e.ExperimentID
    LEFT JOIN CorrectionsSplit cs ON e.LogFileName = cs.LogFilename 
        AND t.TrialNumber = cs.TrialNumber
        AND cs.TableToCorrect = 'ResponseCBs'
        AND cs.FieldToCorrect = 'ResponseTime'
)
SELECT 
    COALESCE(ResponseID, ROW_NUMBER() OVER (ORDER BY TrialID) + (SELECT MAX(ResponseID) FROM ResponseCBs)) AS ResponseID,
    TrialID,
    ResponseTime,
    EventDateTime,
    CorrectedFlag
FROM (
    SELECT * FROM ExistingResponses
    UNION ALL
    SELECT * FROM NewResponses
) AllResponses
ORDER BY TrialID;



CREATE OR REPLACE VIEW EventCBsCorrected AS
WITH NewTrialEvents AS (
    SELECT 
        t.TrialID,
        NULL AS EventType,
        NULL AS EventTime,
        NULL AS ElapsedTime,
        'Added from Corrections' AS CorrectedFlag
    FROM 
        TrialCBsCorrected t
    WHERE 
        t.CorrectedFlag = 'Added from Corrections'
),
ExistingEvents AS (
    SELECT 
        ev.*,
        'Original' AS CorrectedFlag
    FROM 
        EventCBs ev
    JOIN TrialCBsCorrected t ON ev.TrialID = t.TrialID
)
SELECT 
    COALESCE(ev.EventID, ROW_NUMBER() OVER (ORDER BY COALESCE(ev.TrialID, nte.TrialID), ev.EventTime) + (SELECT COALESCE(MAX(EventID), 0) FROM EventCBs)) AS EventID,
    COALESCE(ev.TrialID, nte.TrialID) AS TrialID,
    ev.EventType,
    ev.EventTime,
    ev.ElapsedTime,
    COALESCE(ev.CorrectedFlag, nte.CorrectedFlag) AS CorrectedFlag
FROM 
    ExistingEvents ev
FULL OUTER JOIN NewTrialEvents nte ON ev.TrialID = nte.TrialID
ORDER BY 
    TrialID, ev.EventTime;

