#!/bin/sh
#
# This script performs migration related model changes for CMS2 Service Pack 4.1
#
# Included migrations:
# SASCMS-3990


script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SP4.1/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SP 4.1 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP4.1

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo "  * SASCMS-3990 ..."
python $CARMUSR/data/migration/CMS2_SP4.1/sascms-3990.py 2>&1 | tee $LOG_DIR/SASCMS-3990.log

echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
