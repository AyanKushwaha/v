#!/bin/sh

# This script shows the current information for the specified crew id

if [ -z "$1" ]
then
    echo Usage: $0 CREWID
    exit
fi

id=$1

_DB_LOC="`echo $DB_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

sqlplus -S $_DB_LOC <<EOF ;
SET linesize 2000
SET pages 50000

column empno format a5;
column sex format a3;
column title format a3;
column name format a20;
column forenames format a20;
column logname format a20;
column si format a11;
column maincat format a7;
column bcity format a15;
column bstate format a15;
column bcountry format a8;
column alias format a10;

SELECT id, empno, sex, carmdate.min2date(birthday*24*60) as birthday, title, name, forenames, logname, si, maincat, bcity, bstate, bcountry, alias, carmdate.min2date(employmentdate*24*60) as employmentdate, carmdate.min2date(retirementdate*24*60) as retirementdate
FROM crew
WHERE deleted = 'N' AND next_revid = 0 AND id = '$id';

EOF
