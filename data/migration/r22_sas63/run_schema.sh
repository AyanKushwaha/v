#!/bin/sh
#
# This script performs schema changes and other operations requiring exclusive access
# to the database/system, which relates to the release's corresponding the directory
# where it resides
#
# It should only be present in migration directories where schema changes are required.
# Running of this script requires all connections closed.
#
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
RELEASE=r22_sas63
LOG_DIR="$CARMUSR/data/migration/$RELEASE/migration_logs_schema_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"

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
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo "********************************************"
echo "Migration finished"
echo "  Check for potential problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
