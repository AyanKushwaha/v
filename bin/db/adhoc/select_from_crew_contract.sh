#!/bin/sh

# This script shows the current contract information for the specified crew id

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

column contract format a10;
column si format a30;
column endreason format a20;

SELECT crew, carmdate.min2date(validfrom) as validfrom, carmdate.min2date(validto) as validto, contract, si, endreason, cyclestart, patternstart
FROM crew_contract
WHERE deleted = 'N' AND next_revid = 0 AND crew = '$id';

EOF
