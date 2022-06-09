#!/bin/sh
#
# This script performs migration related model changes for CMS2 Service Pack 4.4
#
# Included migrations:
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SP6.1/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SP 6.1 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP6.1

echo "  * SASCMS-5552 ..."
$CARMUSR/data/migration/CMS2_SP6.1/sascms-5552.sh 2>&1 | tee $LOG_DIR/SASCMS-5552.log

echo "  * SASCMS-5797 ..."
python $CARMUSR/data/migration/CMS2_SP6.1/sascms-5797.py 2>&1 | tee $LOG_DIR/SASCMS-5797.log

#echo "  * Compiling Tracking rulesets ..."
#rave compile cct 2>&1 | tee $RAVE_COMPILE_LOG

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo "  * SASCMS-5576"
cp -f $CARMUSR/crc/parameters/tracking/request_reportserver $CARMUSR/current_carmdata/RaveParameters/tracking/request_reportserver

echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

$CARMUSR/data/migration/CMS2_SP6.1/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
