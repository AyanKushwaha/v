#!/bin/sh
#
# This script performs migration related model changes for CMS2 Service Pack 6
#
# Included migrations:
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SP6/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SP 6 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP6

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo "  * SASCMS-5177 ..."
python $CARMUSR/data/migration/CMS2_SP6/sascms-5177.py 2>&1 | tee $LOG_DIR/SASCMS-5177.log

echo "  * SASCMS-5172 ..."
python $CARMUSR/data/migration/CMS2_SP6/sascms-5172.py 2>&1 | tee $LOG_DIR/SASCMS-5172.log

echo "  * SASCMS-5590 ..."
python $CARMUSR/data/migration/CMS2_SP6/sascms-5590.py 2>&1 | tee $LOG_DIR/SASCMS-5590.log

echo "  * Compiling Tracking rulesets ..."
rave compile cct 2>&1 | tee $RAVE_COMPILE_LOG

echo "  * SASCMS-5584/5617: F36 corrections ..."
python $CARMUSR/data/migration/CMS2_SP6/recalc_f36.py 2>&1 | tee $LOG_DIR/recalc_f36.log

echo "  * Interbids leave bidding default configuration ..."
$CARMUSR/crc/etable/leave_bid_conf/import.sh -na

echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

$CARMUSR/data/migration/CMS2_SP6/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
