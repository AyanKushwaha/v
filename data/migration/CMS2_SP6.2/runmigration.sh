#!/bin/sh
#
# This script performs migration related model changes for CMS2 Service Pack 6.2
#
# Included migrations:
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SP6.2/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SP 6.2 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP6.2


#echo "  * Compiling Tracking rulesets ..."
#rave compile cct 2>&1 | tee $RAVE_COMPILE_LOG

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

$CARMUSR/data/migration/CMS2_SP6.2/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
