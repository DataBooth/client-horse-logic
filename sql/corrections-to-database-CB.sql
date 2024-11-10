CREATE OR REPLACE TABLE SubjectCBs AS
WITH SubjectInfo AS (
    SELECT 
        SubjectName,
        Cohort,
        MAX(SubjectNumber) AS SubjectNumber,
        Direction,
        COUNT(DISTINCT ExperimentID) AS TotalExperiments
    FROM ExperimentCBs
    GROUP BY SubjectName, Cohort, Direction
)
SELECT 
    SubjectName,
    COALESCE(SubjectNumber, 0) AS SubjectNumber,
    Cohort,
    Direction,
    TotalExperiments
FROM SubjectInfo
ORDER BY SubjectNumber;

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

SELECT 
    ExperimentDate,
    SessionType,
    SubjectName,
    TrialNumber,
    LogFilename,
    COUNT(*) AS Count
FROM 
    Corrections
GROUP BY 
    ExperimentDate,
    SessionType,
    SubjectName,
    TrialNumber,
    LogFilename
HAVING 
    COUNT(*) > 1
ORDER BY 
    Count DESC;

WITH CorrectionLogs AS (
    SELECT DISTINCT LogFilename
    FROM Corrections
),
ExperimentLogs AS (
    SELECT DISTINCT LogFileName
    FROM ExperimentCBs
),
DistanceCalc AS (
    SELECT 
        c.LogFilename AS CorrectionFileName,
        CASE 
            WHEN c.LogFilename LIKE 'NO_LOGFILE_AVAILABLE%' THEN NULL
            ELSE e.LogFileName
        END AS ClosestExperimentFileName,
        CASE 
            WHEN c.LogFilename LIKE 'NO_LOGFILE_AVAILABLE%' THEN NULL
            ELSE levenshtein(c.LogFilename, e.LogFileName)
        END AS LevenshteinDistance
    FROM CorrectionLogs c
    CROSS JOIN ExperimentLogs e
),
MinDistance AS (
    SELECT 
        CorrectionFileName,
        MIN(LevenshteinDistance) AS MinLevenshteinDistance
    FROM DistanceCalc
    GROUP BY CorrectionFileName
)
SELECT 
    c.*,
    CASE 
        WHEN c.LogFilename LIKE 'NO_LOGFILE_AVAILABLE%' THEN NULL
        ELSE md.MinLevenshteinDistance
    END AS MinLevenshteinDistance,
    CASE 
        WHEN c.LogFilename LIKE 'NO_LOGFILE_AVAILABLE%' THEN NULL
        ELSE dc.ClosestExperimentFileName
    END AS ClosestExperimentFileName
FROM Corrections c
LEFT JOIN MinDistance md ON c.LogFilename = md.CorrectionFileName
LEFT JOIN DistanceCalc dc ON md.CorrectionFileName = dc.CorrectionFileName AND md.MinLevenshteinDistance = dc.LevenshteinDistance
WHERE 
    c.LogFilename NOT LIKE 'NO_LOGFILE_AVAILABLE%' AND md.MinLevenshteinDistance > 0
    OR c.LogFilename LIKE 'NO_LOGFILE_AVAILABLE%'
ORDER BY 
    CASE 
        WHEN c.LogFilename LIKE 'NO_LOGFILE_AVAILABLE%' THEN 1
        ELSE 0
    END,
    COALESCE(md.MinLevenshteinDistance, 0),
    c.LogFilename;

SELECT 
    Cohort, 
    ExperimentDate, 
    SessionType, 
    SubjectName, 
    COUNT(*) as nCorrectionRow
FROM Corrections
GROUP BY Cohort, ExperimentDate, SessionType, SubjectName
ORDER BY SubjectName, Cohort, ExperimentDate, SessionType;

CREATE OR REPLACE VIEW CorrectionsSplit AS
SELECT 
    *,
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
    OR (sc.TableToCorrect = 'ResponseCBs' AND sc.FieldToCorrect = 'ResponseTime');

CREATE OR REPLACE VIEW ActualCorrections AS
SELECT *
FROM CorrectionWithExistingValues
WHERE ComparisonResult = 'NOT EQUAL';

