#!/bin/sh
#
# This script performs migration related model changes for CMS2 SAS 26
#
# Included migrations:
# Planning groups table created and referenced in crew employment
# Agreement groups created 
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SAS26/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SAS 26 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SAS26

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

# echo "  * Compiling Tracking rulesets ..."
# rave compile cct 2>&1 | tee $RAVE_COMPILE_LOG

echo "  * SKCMS-553 ..."
python $CARMUSR/data/migration/CMS2_SAS26/skcms_553.py 2>&1 | tee $LOG_DIR/SKCMS-553.log
echo "  * SKCMS-598 ..."
python $CARMUSR/data/migration/CMS2_SAS26/skcms_598.py 2>&1 | tee $LOG_DIR/SKCMS-598.log
echo "  * SKCMS-554 ..."
python $CARMUSR/data/migration/CMS2_SAS26/skcms_554.py 2>&1 | tee $LOG_DIR/SKCMS-554.log
echo "  * SKCMS-499 ..."
python $CARMUSR/data/migration/CMS2_SAS26/skcms_499.py  2>&1 | tee $LOG_DIR/SKCMS-499.log
echo "  * SKCMS-554 Part 2 ..."
python $CARMUSR/data/migration/CMS2_SAS26/skcms_554_2.py 2>&1 | tee $LOG_DIR/SKCMS-554_2.log


echo " - Updating DB filters"
#db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

echo "  Copy parameters to carmdata ..."
#cp -f $CARMUSR/crc/parameters/rostering/column_generation $CARMUSR/current_carmdata/RaveParameters/rostering/.

#cp -f $CARMUSR/crc/parameters/rostering/column_generation_short $CARMUSR/current_carmdata/RaveParameters/rostering/.

#$CARMUSR/data/migration/CMS2_SAS19/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
