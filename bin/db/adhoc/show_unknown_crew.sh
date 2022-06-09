#!/bin/sh

# This script shows the crew that are currently in the table crew_unknown but their extperkey is not found in crew_employment,
# i.e. they need to be added in CMS
_DB_LOC="`echo $DB_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

sqlplus -S $_DB_LOC <<EOF ;
SET linesize 2000
SET pages 50000

alter session set nls_date_format='yyyy-mm-dd hh24:mi:ss';

column extperkey format a9;
column name format a20;
column forenames format a30;
column empcountry format a10;
column corrected format a9;
column si format a30;

SELECT cu.extperkey, cu.name, cu.forenames, cu.empcountry, cu.corrected, cu.si, TO_TIMESTAMP('198601010000', 'yyyymmddMISS') + dr.committs/24/60/60 as committime
FROM crew_unknown cu, dave_revision dr
WHERE deleted = 'N' AND next_revid = 0 AND dr.revid = cu.revid AND cu.extperkey NOT IN (SELECT DISTINCT extperkey FROM crew_employment WHERE deleted = 'N' AND next_revid = 0)
ORDER BY extperkey DESC;

EOF
