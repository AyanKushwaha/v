#!/bin/sh

# This script shows the current qualification information for the specified crew id

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

column qual_typ format a8;
column qual_subtype format a12;
column lvl format a10;
column si format a30;
column acstring format a8;

SELECT crew, qual_typ, qual_subtype, carmdate.min2date(validfrom) as validfrom, carmdate.min2date(validto) as validto, lvl, si, acstring
FROM crew_qualification
WHERE deleted = 'N' AND next_revid = 0 AND crew = '$id';

EOF
