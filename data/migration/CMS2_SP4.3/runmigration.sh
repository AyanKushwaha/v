#!/bin/sh
#
# This script performs migration related model changes for CMS2 Service Pack 4.3
#
# Included migrations:
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SP4.3/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SP 4.3 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP4.3

echo "  * Compiling Tracking rulesets ..."
rave compile cct 2>&1 | tee $RAVE_COMPILE_LOG

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo "  * SASCMS-3997 ..."
python $CARMUSR/data/migration/CMS2_SP4.3/sascms-3997.py 2>&1 | tee $LOG_DIR/SASCMS-3997.log

echo "  * SASCMS-4507 ..."
python $CARMUSR/data/migration/CMS2_SP4.3/sascms-4507.py 2>&1 | tee $LOG_DIR/SASCMS-4507.log

echo "  * SASCMS-4710 ..."
python $CARMUSR/data/migration/CMS2_SP4.3/sascms-4710.py 2>&1 | tee $LOG_DIR/SASCMS-4710.log

echo "  * SASCMS-4903 ..."
python $CARMUSR/data/migration/CMS2_SP4.3/sascms-4903.py 2>&1 | tee $LOG_DIR/SASCMS-4903.log

echo "  * SASCMS-4948 ..."
python $CARMUSR/data/migration/CMS2_SP4.3/sascms-4948.py 2>&1 | tee $LOG_DIR/SASCMS-4948.log

echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

$CARMUSR/data/migration/CMS2_SP4.3/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
