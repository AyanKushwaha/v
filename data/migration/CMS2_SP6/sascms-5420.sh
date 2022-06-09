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
echo "SASCMS-5420 Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP6


# Adding current dir to pythonpath
SAVED_PYTHONPATH=$PYTHONPATH
export PYTHONPATH=$CARMUSR/data/migration/CMS2_SP6:$PYTHONPATH
echo " - Migrating crew_activity_attr data "
$CARMSYS/bin/mirador -s sascms-5420 2>&1 | tee $LOG_DIR/SASCMS-5420.log
export PYTHONPATH=$SAVED_PYTHONPATH

echo "********************************************"
echo "SASCMS-5420 Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
