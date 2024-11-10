CREATE OR REPLACE VIEW AddExperiments AS
WITH FirstComments AS (
    SELECT 
        LogFilename,
        FIRST_VALUE(Comment) OVER (
            PARTITION BY LogFilename 
            ORDER BY TrialNumber
        ) AS FirstComment
    FROM Corrections
)
SELECT DISTINCT 
    c.Cohort,
    c.ExperimentDate,
    c.SessionType,
    c.SubjectName,
    c.LogFilename,
    fc.FirstComment AS Comment,
    'Corrections xlsx: ADD' AS DataSource
FROM Corrections c
LEFT JOIN ExperimentCBs e ON c.LogFilename = e.LogFileName
LEFT JOIN FirstComments fc ON c.LogFilename = fc.LogFilename
WHERE e.LogFileName IS NULL;

CREATE OR REPLACE VIEW ReformattedAddExperiments AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY a.LogFilename) + COALESCE((SELECT MAX(ExperimentID) FROM ExperimentCBs), 0) AS ExperimentID,
    a.Cohort,
    a.SubjectName,
    sb.SubjectNumber,  -- Look up SubjectNumber from SubjectCBs
    NULL AS SessionNumber,   -- Assume unavailable from Corrections info (and/or can't be inferred)
    a.SessionType,   
    NULL AS ExperimentType,  -- Assume unavailable from Corrections info (and/or can't be inferred)
    sb.Direction,      -- Look up Direction from SubjectCBs
    a.Comment,
    CAST(a.ExperimentDate AS TIMESTAMP) AS DateTime,
    a.LogFilename,
    NULL::JSON AS Parameters,  -- Assuming Parameters is JSON and initialising as NULL
    'AddExperiments' AS DataSource  -- Optional if you want to keep track of source
FROM 
    AddExperiments a
LEFT JOIN 
    SubjectCBs sb ON a.SubjectName = sb.SubjectName;

CREATE OR REPLACE VIEW ExperimentCBsCorrected AS
SELECT 
    *,
    'ExperimentCBs' AS DataSource
FROM 
    ExperimentCBs

UNION ALL

SELECT 
    * EXCLUDE (DataSource),
    CONCAT(DataSource, ' -> ReformattedAddExperiments') AS DataSource
FROM 
    ReformattedAddExperiments
ORDER BY 
    ExperimentID;

CREATE OR REPLACE VIEW AddTrials AS
WITH AddedTrials AS (
    SELECT 
        e.ExperimentID,
        c.TrialNumber,
        c.TrialType AS TrialSubType,
        c.ResponseType,
        CASE 
            WHEN c.TrialType = 'P' AND c.ResponseType = 'GO' THEN 'positive'
            WHEN c.TrialType = 'N' AND c.ResponseType = 'NOGO' THEN 'negative'
            ELSE NULL
        END AS CriterionType,
        NULL AS TrialStartTime,
        NULL AS TrialEndTime,
        'Added from Corrections' AS CorrectedFlag
    FROM 
        Corrections c
    JOIN 
        ExperimentCBsCorrected e ON c.LogFilename = e.LogFileName
    WHERE 
        e.DataSource LIKE '%AddExperiments%'
)
SELECT 
    ExperimentID,
    TrialNumber,
    TrialSubType,
    ResponseType,
    CriterionType,
    SUM(CASE 
        WHEN CriterionType IS NOT NULL THEN 1 
        ELSE 0 
    END) OVER (
        PARTITION BY ExperimentID, CriterionType
        ORDER BY TrialNumber
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS CriterionCount,
    TrialStartTime,
    TrialEndTime,
    CorrectedFlag
FROM AddedTrials
ORDER BY ExperimentID, TrialNumber;

CREATE OR REPLACE VIEW CorrectTrials AS
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
        WHEN cs.ValueToCorrect IS NOT NULL AND cs.ValueToCorrect != t.ResponseType THEN 'Corrected: ResponseType'
        WHEN cs.FieldToCorrect = 'ResponseTime' AND cs.ValueToCorrect != r.ResponseTime THEN 'Corrected: ResponseTime'
        ELSE 'Original: not a correction'
    END AS CorrectedFlag
FROM 
    TrialCBs t
LEFT JOIN ExperimentCBsCorrected e ON t.ExperimentID = e.ExperimentID
LEFT JOIN CorrectionsSplit cs ON e.LogFileName = cs.LogFilename 
    AND t.TrialNumber = cs.TrialNumber
    AND cs.TableToCorrect = 'TrialCBs'
LEFT JOIN ResponseCBs r ON t.TrialID = r.TrialID
WHERE 
    cs.FieldToCorrect IN ('ResponseType', 'ResponseTime') OR cs.FieldToCorrect IS NULL;

CREATE OR REPLACE VIEW TrialCBsCorrected AS
WITH MaxExistingTrialID AS (
    SELECT COALESCE(MAX(TrialID), 0) AS MaxID FROM TrialCBs
),
CombinedTrials AS (
    SELECT 
        ct.TrialID,
        ct.ExperimentID,
        ct.TrialNumber,
        ct.TrialSubType,
        ct.ResponseType,
        ct.CriterionType,
        ct.CriterionCount,
        ct.TrialStartTime,
        ct.TrialEndTime,
        ct.CorrectedFlag,
        0 AS IsNewTrial
    FROM CorrectTrials ct

    UNION ALL

    SELECT 
        NULL AS TrialID,
        at.ExperimentID,
        at.TrialNumber,
        at.TrialSubType,
        at.ResponseType,
        at.CriterionType,
        at.CriterionCount,
        at.TrialStartTime,
        at.TrialEndTime,
        at.CorrectedFlag,
        1 AS IsNewTrial
    FROM AddTrials at
),
NumberedNewTrials AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            ORDER BY ExperimentID, TrialNumber
        ) AS NewTrialNum
    FROM CombinedTrials
    WHERE TrialID IS NULL
)
SELECT 
    CASE 
        WHEN ct.TrialID IS NOT NULL THEN ct.TrialID
        ELSE m.MaxID + nnt.NewTrialNum
    END AS TrialID,
    ct.ExperimentID,
    ct.TrialNumber,
    ct.TrialSubType,
    ct.ResponseType,
    ct.CriterionType,
    ct.CriterionCount,
    ct.TrialStartTime,
    ct.TrialEndTime,
    ct.CorrectedFlag
FROM CombinedTrials ct
LEFT JOIN NumberedNewTrials nnt ON ct.ExperimentID = nnt.ExperimentID AND ct.TrialNumber = nnt.TrialNumber
CROSS JOIN MaxExistingTrialID m
ORDER BY ct.ExperimentID, ct.TrialNumber;

WITH TrialDifferences AS (
    SELECT 
        COALESCE(t.ExperimentID, tc.ExperimentID) AS ExperimentID,
        COALESCE(t.TrialNumber, tc.TrialNumber) AS TrialNumber,
        CASE 
            WHEN t.TrialID IS NULL THEN 'Additions (new rows)'
            WHEN tc.TrialID IS NULL THEN 'Existing (same rows)'
            WHEN t.ResponseType != tc.ResponseType THEN 'Correction to ResponseType'
            ELSE 'Existing (same rows)'
        END AS Difference
    FROM 
        TrialCBs t
    FULL OUTER JOIN 
        TrialCBsCorrected tc ON t.ExperimentID = tc.ExperimentID AND t.TrialNumber = tc.TrialNumber
)
SELECT 
    Difference,
    COUNT(*) AS Count
FROM 
    TrialDifferences
GROUP BY 
    Difference
UNION ALL
SELECT 
    'Total TrialCBs', 
    COUNT(*) 
FROM 
    TrialCBs
UNION ALL
SELECT 
    'Total TrialCBsCorrected', 
    COUNT(*) 
FROM 
    TrialCBsCorrected
ORDER BY 
    Difference;

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
ORDER BY ResponseID;

SELECT 
    e.SubjectName,
    e.SubjectNumber,
    e.ExperimentID,
    t.TrialID,
    t.ResponseType,
    r.ResponseID,
    r.ResponseTime,
    r.EventDateTime,
    r.CorrectedFlag
FROM 
    ResponseCBsCorrected r
JOIN 
    TrialCBsCorrected t ON r.TrialID = t.TrialID
JOIN 
    ExperimentCBsCorrected e ON t.ExperimentID = e.ExperimentID
ORDER BY 
    e.ExperimentID, t.TrialID, r.ResponseID

WITH ResponseDifferences AS (
    SELECT 
        COALESCE(r.TrialID, rc.TrialID) AS TrialID,
        CASE 
            WHEN r.ResponseID IS NULL THEN 'Additions (new rows)'
            WHEN rc.ResponseID IS NULL THEN 'Same (existing rows)'
            WHEN ABS(r.ResponseTime - rc.ResponseTime) > 0.001 THEN 'Corrected response times'
            ELSE 'In Both, Identical'
        END AS Difference
    FROM 
        ResponseCBs r
    FULL OUTER JOIN 
        ResponseCBsCorrected rc ON r.TrialID = rc.TrialID
)
SELECT 
    Difference, 
    COUNT(*) AS Count
FROM 
    ResponseDifferences
GROUP BY 
    Difference
ORDER BY 
    Difference;

SELECT 
    t.TrialID,
    t.ExperimentID,
    e.SubjectName,
    e.SubjectNumber,
    t.TrialNumber,
    t.TrialSubType,
    t.ResponseType,
    t.CriterionType,
    t.CriterionCount,
    t.TrialStartTime,
    t.TrialEndTime,
    r_orig.ResponseTime AS OriginalResponseTime,
    r_corr.ResponseTime AS CorrectedResponseTime,
    t.CorrectedFlag
FROM 
    TrialCBsCorrected t
JOIN 
    ExperimentCBsCorrected e ON t.ExperimentID = e.ExperimentID
LEFT JOIN 
    ResponseCBs r_orig ON t.TrialID = r_orig.TrialID
LEFT JOIN 
    ResponseCBsCorrected r_corr ON t.TrialID = r_corr.TrialID
ORDER BY 
    t.ExperimentID, t.TrialNumber;

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

WITH EventDifferences AS (
    SELECT 
        COALESCE(e.TrialID, ec.TrialID) AS TrialID,
        CASE 
            WHEN e.EventID IS NULL THEN 'Additions (new rows)'
            WHEN ec.EventID IS NULL THEN 'Existing (same rows)'
            WHEN e.EventType != ec.EventType OR ABS(e.ElapsedTime - ec.ElapsedTime) > 0.001 THEN 'Corrections TBA'
            ELSE 'In Both, Identical'
        END AS Difference
    FROM 
        EventCBs e
    FULL OUTER JOIN 
        EventCBsCorrected ec ON e.TrialID = ec.TrialID AND e.EventType = ec.EventType
)
SELECT 
    Difference, 
    COUNT(*) AS Count
FROM 
    EventDifferences
GROUP BY 
    Difference
ORDER BY 
    Difference;

