#!/bin/sh
#
# This script performs schema changes and such things requiring exclusive access
# to the database/system, which relates to the release corresponding to the directory
# where it resides
#
# It should only be present in migration directories where schema changes are required.
# Running of this script requires all connections closed.
#
# Before running this script, make a dry run of the migration by running:
#   db updateschema
#
# This has to be run before run_data.sh

dir=`dirname $0`

cd $dir/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
RELEASE=`basename $dir`
LOG_DIR="$CARMUSR/data/migration/$RELEASE/migration_logs_schema_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
DATA_CONFIG_FILE="$CARMUSR/data/migration/$RELEASE/data_migration.config"

echo "********************************************"
echo $RELEASE "Database Schema Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/$RELEASE

echo " - Updating schema"
db updateschema $LOG_DIR doit $DATA_CONFIG_FILE 2>&1 | tee $UPDATE_SCHEMA_LOG

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
