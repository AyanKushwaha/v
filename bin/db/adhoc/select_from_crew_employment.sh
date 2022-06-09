#!/bin/sh

# This script shows the current employment information for the specified crew id

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

column carrier format a7;
column company format a7;
column base format a4;
column crewrank format a8;
column titlerank format a9;
column si format a30;
column civicstation format a12;
column station format a7;
column country format a7;
column extperkey format a9;
column planning_group format a14;

SELECT crew, carmdate.min2date(validfrom) as validfrom, carmdate.min2date(validto) as validto, carrier, company, base, crewrank, titlerank, si, region, civicstation, station, country, extperkey, planning_group
FROM crew_employment
WHERE deleted = 'N' AND next_revid = 0 AND crew = '$id';

EOF
