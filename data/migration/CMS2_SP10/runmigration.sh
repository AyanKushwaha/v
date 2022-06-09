#!/bin/sh
#
# This script performs migration related model changes for CMS2 Service Pack 10
#
# Included migrations:
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SP10/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SP 10 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SP10

#echo " - Updating schema"
#db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

# echo "  * Compiling Tracking rulesets ..."
# rave compile cct 2>&1 | tee $RAVE_COMPILE_LOG

echo "  * SASCMS-2191 ..."
python $CARMUSR/data/migration/CMS2_SP10/sascms-2191.py 2>&1 | tee $LOG_DIR/SASCMS-2191.log
echo "  * SASCMS-6069 ..."
python $CARMUSR/data/migration/CMS2_SP10/sascms-6069.py 2>&1 | tee $LOG_DIR/SASCMS-6069.log

echo "  * SASCMS-6064 ..."
python $CARMUSR/data/migration/CMS2_SP10/sascms-6064.py 2>&1 | tee $LOG_DIR/SASCMS-6064.log

echo " - Updating DB filters"
db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

#$CARMUSR/data/migration/CMS2_SP10/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for any problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
