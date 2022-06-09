#!/bin/sh

LOG=${CARMTMP}/logfiles/`basename $0 .sh`.${USER}.$(date +%Y%m%d.%H%M.%S).`hostname -s`.log
{
_DB_LOC="`echo $DB_ADM_URL_HISTORY |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";
if [[ -z "$_DB_LOC" ]]; then
   echo "ERROR: No admin DB URL was found."
   exit 1
fi

_RO_SCHEMA=`xmlconfig /carmen/config[1]/global[3]/default/db/dave/history_readonly/user 2> /dev/null | cut -d ' ' -f 3- | awk '{print toupper($0)}'`
if [[ -z "$_RO_SCHEMA" ]]; then
   echo "ERROR: No readonly user was found. Make sure this is run in a history carmusr."
   exit 1
fi

_RW_SCHEMA=`xmlconfig /carmen/config[1]/global[3]/default/db/dave/history_readonly/schema 2> /dev/null | cut -d ' ' -f 3- | awk '{print toupper($0)}'`
if [[ -z "$_RW_SCHEMA" ]]; then
   echo "ERROR: No history schema was found. Make sure this is run in a history carmusr."
   exit 1 
fi


echo Granting $_RO_SCHEMA access to $_RW_SCHEMA in database $_DB_LOC
echo $_RO_SCHEMA

_GRANTS=`
sqlplus -S $_DB_LOC <<EOF ;
SET HEADING OFF
SET FEEDBACK OFF
SET LINESIZE 5000

SELECT 
    'GRANT SELECT ON "'||owner||'"."'||TABLE_NAME||'" TO $_RO_SCHEMA;'
FROM dba_tables
WHERE owner='$_RW_SCHEMA';

EOF
`

echo "$_GRANTS"

echo "$_GRANTS" | sqlplus -S $_DB_LOC

} | tee -a ${LOG}
