#!/bin/sh
#
# This script performs migration related model changes for CMS2 SAS 15
#
# Included migrations:
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SAS15/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SAS 15 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SAS15

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

# echo "  * Compiling Tracking rulesets ..."
# rave compile cct 2>&1 | tee $RAVE_COMPILE_LOG

echo "  * SASCMS-6374 ..."
#Todo Stefan
$CARMUSR/bin/accumulators/accumulator.sh lifeblockhrs

echo "  * SASCMS-6524 ..."
python $CARMUSR/data/migration/CMS2_SAS15/sascms_6524.py 2>&1 | tee $LOG_DIR/SASCMS_6524.log

echo "  * SASCMS-6524 ... update baseline"
$CARMUSR/bin/accumulators/accumulateBaseline.sh 25Mar2014 RECALC SHORT 2>&1 | tee $LOG_DIR/SASCMS_6524_accumulateBaseline.log


echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

#$CARMUSR/data/migration/CMS2_SAS15/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
