#!/bin/sh
#
# This script performs migration related model changes for CMS2
#
# Included migrations:
# SASCMS-2537 table dig_string patterns
# SASCMS-3256 Add property to roster_attr_set

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2

echo "  * Compiling Manpower rulesets ..."
rave compile cmp 2>&1 | tee $RAVE_COMPILE_LOG

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

. $CARMUSR/data/migration/CMS2/SASCMS-2537.sh 2>&1 | tee $LOG_DIR/SASCMS-2537.log
python $CARMUSR/data/migration/CMS2/SASCMS-3256.py 2>&1 | tee $LOG_DIR/SASCMS-3256.log
$CARMUSR/data/migration/CMS2/manpower_migration.sh "$LOG_DIR" 2>&1 | tee $LOG_DIR/manpower.log

echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
