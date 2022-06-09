#!/bin/sh
#
# This script performs migration related model changes for CMS2 Service Pack 4
#
# Included migrations:
# SASCMS-3278


script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SP4/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SP 4 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP4

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo "  * SASCMS-3278 ..."
python $CARMUSR/data/migration/CMS2_SP4/sascms-3278.py 2>&1 | tee $LOG_DIR/SASCMS-3278.log

echo "  * SASCMS-3924 ..."
python $CARMUSR/data/migration/CMS2_SP4/sascms-3924.py 2>&1 | tee $LOG_DIR/SASCMS-3924.log

echo "  * SASCMS-4543 ..."
python $CARMUSR/data/migration/CMS2_SP4/sascms-4543.py 2>&1 | tee $LOG_DIR/SASCMS-4543.log

echo "  * SKBMM-326 ..."
python $CARMUSR/data/migration/CMS2_SP4/skbmm-326.py 2>&1 | tee $LOG_DIR/SKBMM-326.log

echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

$CARMUSR/data/migration/CMS2_SP4/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
