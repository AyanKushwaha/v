#!/bin/sh

LOG=${CARMTMP}/logfiles/`basename $0 .sh`.${USER}.$(date +%Y%m%d.%H%M.%S).`hostname -s`.log
{
echo "[$(date)] Running script `basename $0` $1"
echo

runid=$1

_DB_LOC="`echo $DB_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

sqlplus -S $_DB_LOC <<EOF ;
SET linesize 2000
SET pages 50000


SELECT runid,
       to_char(carmdate.min2date(starttime), 'YYYY-MM-DD hh:mm') starttime,
       runtype,
       selector,
       extsys,
       to_char(carmdate.min2date(firstdate * 1440), 'YYYY-MM-DD') firstdate,
       to_char(carmdate.min2date(lastdate * 1440), 'YYYY-MM-DD') lastdate,
       to_char(carmdate.min2date(releasedate), 'YYYY-MM-DD hh:mm') releasedate,
       note
FROM salary_run_id
WHERE deleted = 'N' AND next_revid = 0 AND runid = '$runid'
ORDER BY runid DESC;

prompt Salary basic data
SELECT crewid, extperkey, extartid, amount
FROM salary_basic_data
WHERE deleted = 'N' AND next_revid = 0 AND runid = '$runid'
ORDER BY crewid, extartid;

prompt Salary extra data
SELECT crewid, intartid, amount
FROM salary_extra_data
WHERE deleted = 'N' AND next_revid = 0 AND runid = '$runid'
ORDER BY crewid, intartid;

EOF
} | tee -a ${LOG}
