#!/bin/sh

LOG=${CARMTMP}/logfiles/`basename $0 .sh`.${USER}.$(date +%Y%m%d.%H%M.%S).`hostname -s`.log
{
echo "[$(date)] Starting script `basename $0`"
echo

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
WHERE deleted = 'N' AND next_revid = 0
ORDER BY runid DESC;

EOF
} | tee -a ${LOG}
