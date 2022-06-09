#!/bin/sh
#
# This script performs migration related model changes for CMS2 Service Pack 3.3
#
# Included migrations:
# SASCMS-4073


script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SP3.3/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SP 3.3 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP3.3

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo "  * SASCMS-4073 ..."
python $CARMUSR/data/migration/CMS2_SP3.3/sascms-4073.py 2>&1 | tee $LOG_DIR/SASCMS-4073.log

echo "  * SASCMS-2040 ..."
python $CARMUSR/data/migration/CMS2_SP3.3/sascms-2040.py 2>&1 | tee $LOG_DIR/SASCMS-2040.log

echo "  * SASCMS-4143 ..."
python $CARMUSR/data/migration/CMS2_SP3.3/sascms-4143.py 2>&1 | tee $LOG_DIR/SASCMS-4143.log


echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
