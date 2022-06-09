#!/bin/sh

LOG=${CARMTMP}/logfiles/`basename $0 .sh`.${USER}.$(date +%Y%m%d.%H%M.%S).`hostname -s`.log
{
echo "[$(date)] Starting script `basename $0`"
echo

_DB_LOC="`echo $DB_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

jobids=`
sqlplus -S $_DB_LOC <<EOF ;
set heading off
set feedback off

SELECT id
FROM job
WHERE deleted = 'N' AND next_revid = 0 AND channel in ('salary_manual', 'salary')
ORDER BY id DESC;

EOF
`
echo =======================================================================================================================

for jobid in $jobids
do
sqlplus -S $_DB_LOC <<EOF ;
SET linesize 2000
SET pages 50000
SET heading off
SET feedback off

SELECT id,
       substr(submitter, 1, 19) submitter,
       substr(start_at, 1, 20) start_at,
       substr(submitted_at, 1, 20) submitted_at,
       substr(started_at, 1, 20) started_at,
       substr(ended_at, 1, 20) ended_at,
       substr(status, 1, 80) status
FROM job
WHERE deleted = 'N' AND next_revid = 0 AND channel in ('salary_manual', 'salary') AND id = $jobid;

PROMPT
PROMPT ------------------------------------------------------------------------------------------------------------------------

SELECT substr(paramname, 1, 20) paramname,
       substr(paramvalue, 1, 200) paramvalue
FROM job_parameter
WHERE deleted = 'N' AND next_revid = 0 AND job = '$jobid'
ORDER BY paramname;


EOF

echo
echo =======================================================================================================================

done

} | tee -a ${LOG}
