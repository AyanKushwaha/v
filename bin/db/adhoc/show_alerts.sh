#!/bin/sh

# This script shows the currently active alerts grouped by rule and sorted by number of occurrences

# if [ -z "$1" ]
# then
#     echo Usage: $0 CREWID
#     exit
# fi

# id=$1

_DB_LOC="`echo $DB_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

sqlplus -S $_DB_LOC <<EOF ;
SET linesize 2000
SET pages 50000

COLUMN rule FORMAT a80;
COLUMN isactive FORMAT a8;
COLUMN alert_time FORMAT a15;
COLUMN activity_id FORMAT a40;

SELECT rule, count(*) AS count
FROM track_alert
WHERE deleted = 'N' AND next_revid = 0
GROUP BY rule
ORDER BY count DESC;

SELECT rule, isactive, activity_id, carmdate.min2date(alerttime) as alert_time
FROM track_alert
WHERE deleted = 'N' AND next_revid = 0
ORDER BY rule, alerttime;

EOF
