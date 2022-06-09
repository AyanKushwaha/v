#!/bin/sh
#
# This script performs migration related model changes for CMS2 Service Pack 5
#
# Included migrations:
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SP5/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SP 5 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP5

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo "  * SASCMS-4616 ..."
python $CARMUSR/data/migration/CMS2_SP5/sascms-4616.py 2>&1 | tee $LOG_DIR/SASCMS-4616.log

echo "  * SASCMS-4932 ..."
python $CARMUSR/data/migration/CMS2_SP5/sascms-4932.py 2>&1 | tee $LOG_DIR/SASCMS-4932.log

echo "  * SKBMM-131 ..."
python $CARMUSR/data/migration/CMS2_SP5/skbmm-131.py 2>&1 | tee $LOG_DIR/SKBMM-131.log

echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

$CARMUSR/data/migration/CMS2_SP5/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
