#!/bin/sh

LOG=${CARMTMP}/logfiles/`basename $0 .sh`.${USER}.$(date +%Y%m%d.%H%M.%S).`hostname -s`.log
{
echo "[$(date)] Starting script `basename $0`"
echo

_DB_LOC="`echo $DB_CP_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

sqlplus -S $_DB_LOC <<EOF ;
SET linesize 2000
SET pages 50000
--SET heading off
SET feedback off

SELECT u.userid, u.firstname, u.lastname, g.groupname, u.inactive
FROM users u, usergroups ug, groups g
WHERE u.userid = ug.userid AND ug.groupid = g.groupid
ORDER BY u.userid;

EOF

} | tee -a ${LOG}
