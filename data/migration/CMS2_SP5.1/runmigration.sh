#!/bin/sh
#
# This script performs migration related model changes for CMS2 Service Pack 5.1
#
# Included migrations:
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SP5.1/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SP 5.1 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP5.1

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo "  * SASCMS-5353 ..."
$CARMUSR/data/migration/CMS2_SP5.1/sascms-5353.sh 2>&1 | tee $LOG_DIR/SASCMS-5353.log

echo "  * SASCMS-4960 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-4960.py 2>&1 | tee $LOG_DIR/SASCMS-4960.log

echo "  * SASCMS-5161 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5161.py 2>&1 | tee $LOG_DIR/SASCMS-5161.log

echo "  * SASCMS-5262 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5262.py 2>&1 | tee $LOG_DIR/SASCMS-5262.log

echo "  * SASCMS-5302 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5302.py 2>&1 | tee $LOG_DIR/SASCMS-5302.log

echo "  * Compiling Tracking rulesets ..."
rave compile cct 2>&1 | tee $RAVE_COMPILE_LOG

echo "  * SASCMS-5302_add ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5302_add.py 2>&1 | tee $LOG_DIR/SASCMS-5302_add.log

echo "  * Interbids leave bidding default configuration ..."
$CARMUSR/crc/etable/leave_bid_conf/import.sh -na

echo "  * SASCMS-5424 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5424.py 2>&1 | tee $LOG_DIR/SASCMS-5424.log

echo "  * SKBMM-670 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/skbmm-670.py 2>&1 | tee $LOG_DIR/SKBMM-670.log

echo "  * SASCMS-5326 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5326.py 2>&1 | tee $LOG_DIR/SASCMS-5326.log

echo "  * SASCMS-5371 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5371.py 2>&1 | tee $LOG_DIR/SASCMS-5371.log

echo "  * SASCMS-5417 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5417.py 2>&1 | tee $LOG_DIR/SASCMS-5417.log

echo "  * SASCMS-5437 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5437.py 2>&1 | tee $LOG_DIR/SASCMS-5437.log

echo "  * SASCMS-5529 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5529.py 2>&1 | tee $LOG_DIR/SASCMS-5529.log

echo "  * SASCMS-5551 ..."
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5551.py 2>&1 | tee $LOG_DIR/SASCMS-5551.log

echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

$CARMUSR/data/migration/CMS2_SP5.1/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
