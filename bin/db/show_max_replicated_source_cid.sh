#!/bin/sh

_DB_LOC="`echo $DB_URL_HISTORY |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

sqlplus -S $_DB_LOC <<EOF ;
SET HEADING OFF
SET FEEDBACK OFF

SELECT MAX(source_cid) from replicated_revision;

EOF
