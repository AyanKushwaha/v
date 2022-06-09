#!/bin/bash
echo "    * Running `basename $BASH_SOURCE`"

MIGRATION_DIR=.
JIRA_NUMBER="SASCMS-3241"
LOG_DIR="$MIGRATION_DIR/${JIRA_NUMBER}_logs"
HANDLE_SCHEMA_LOG="$LOG_DIR/database_update.log"

echo " - Setting up ..."

if [ ! -e $LOG_DIR ]; then
    echo "    - Creating log dir ..."
    mkdir -p $LOG_DIR
fi

echo " - Updating database definition ..."
$CARMUSR/bin/handle_schemas.sh -u $DB_SCHEMA $DB_SCHEMA > $HANDLE_SCHEMA_LOG 2>&1

echo " - Database updated, now remember to run the adhoc script lib/python/adhoc/sascms-3241.py!"