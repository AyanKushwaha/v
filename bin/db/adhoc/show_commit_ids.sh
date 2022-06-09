#!/bin/sh

# This script shows the commit ids with time stamps
_DB_LOC="`echo $DB_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

sqlplus -S $_DB_LOC <<EOF ;
SET linesize 2000
SET pages 50000

alter session set nls_date_format='yyyy-mm-dd hh24:mi:ss';

column remark format a40;
column reason format a6;
column cliprogram format a25;
column clihost format a10;

SELECT TO_TIMESTAMP('198601010000', 'yyyymmddMISS') + dr.committs/24/60/60 as committime, commitid, revid, remark, reason, cliprogram, clihost
FROM dave_revision dr
ORDER BY committs DESC;

EOF
