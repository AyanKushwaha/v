#!/bin/sh

LOG=${CARMTMP}/logfiles/`basename $0 .sh`.${USER}.$(date +%Y%m%d.%H%M.%S).`hostname -s`.log
{
echo "[$(date)] Running script `basename $0` $1"
echo

userid=$1

_DB_LOC="`echo $DB_CP_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

sqlplus -S $_DB_LOC <<EOF ;
SET linesize 2000
SET pages 50000
--SET heading off
SET feedback off

SELECT u.userid, u.firstname, u.lastname, g.groupname, u.inactive
FROM users u, usergroups ug, groups g
WHERE u.userid = ug.userid AND ug.groupid = g.groupid AND u.userid = '$userid';

EOF

bidgroupids=`
sqlplus -S $_DB_LOC <<EOF ;
set heading off
set feedback off

SELECT bidgroupid
FROM bidgroups
WHERE userid = '$userid'
ORDER BY startdate DESC;

EOF
`

for bidgroupid in $bidgroupids
do
sqlplus -S $_DB_LOC <<EOF ;
SET linesize 2000
SET pages 50000
--SET heading off
SET feedback off

COLUMN startdate format a29
COLUMN enddate format a29
COLUMN name format a20
COLUMN category format a20
COLUMN type format a20
COLUMN createdby format a10
COLUMN updatedby format a10
COLUMN created format a29
COLUMN invalid format a29

SELECT bidgroupid,
       startdate,
       name,
       category,
       type,
       createdby,
       created
FROM bidgroups
WHERE bidgroupid = '$bidgroupid';

PROMPT -----------------------------------------------------------------------------------------------------------------------

SELECT bidid, bidtype, startdate, enddate, createdby, created, updatedby, invalid
FROM bids
WHERE bidgroupid = '$bidgroupid'
ORDER BY bidid DESC;

EOF
echo =======================================================================================================================

done

} | tee -a ${LOG}
