--use experiments_cb_2023_q4;

select
    e.cohort,
    e.subjectname,
    e.sessionnumber,
    e.sessiontype,
    e.experimenttype,
    e.comment
    , t.trialid,
    t.trialnumber,
    t.responsetype,
    t.trialsubtype,
    t.criteriontype,
    t.criterioncount
    --             , ev.eventType
    --             , case when t.responseType = 'NOGO' then 30 else r.eventTime end as responseSeconds
    , case
        when t.responsetype = 'NOGO' then 30 else
            epoch(hr.eventtime) - epoch(r.eventtime)
    end as latencyseconds
    , r.eventtime, r.eventtype
    , hr.eventtime as horsereleasedeventtime
--, hr.elapsedTime as horseReleasedElapsedTime, hr.elapsedTime
from experimentcbscorrected e
join trialcbscorrected t on t.experimentid = e.experimentid
--join EventCbsCorrected ev on ev.trialId = t.trialId
join (
    select eventid, trialid, eventtime, elapsedtime
    from eventcbscorrected
    where eventtype like '%horse released%'
) hr on hr.trialid = t.trialid
join (
    select
        trialid, eventtime
        , case
            when eventtype like 'GO for% - NP - %' then 'GO NP'
            when eventtype like 'GO for% - NN - %' then 'GO N'
            when eventtype like 'GO for% - P - %' then 'GO P'
            when eventtype like 'GO for% - N - %' then 'GO N'
            when eventtype like 'NOGO for% - NP - %' then 'NOGO NP'
            when eventtype like 'NOGO for% - NN - %' then 'NOGO N'
            when eventtype like 'NOGO for% - P - %' then 'NOGO P'
            when eventtype like 'NOGO for% - N - %' then 'NOGO N'
            else null
        end as response
        , eventtype
    from eventcbscorrected
) r on r.trialid = t.trialid
where
    e.subjectname = 'apollo'
    and r.eventtype like '%for Trial 1 -%'
    and e.experimenttype = 'Test Type 1'
--and e.comment = 'CB T 1 after RP E '
-- 11 oct - test 1 - 8.76
--and t.trialSubType = 'NP'
order by e.cohort, e.subjectnumber, e.sessionnumber, t.trialnumber;
