#!/bin/sh
#
# This script performs migration related model changes for CMS2 SAS 34
#
# Included migrations:
# Crew bunks for inflight rest corrected
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SAS34/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SAS 34 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SAS34

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo "  * RULES_VALIDITY ..."
python $CARMUSR/data/migration/CMS2_SAS34/rules_validity.py 2>&1 | tee $LOG_DIR/SAS34_VALIDITY.log

echo "  * SKCMS-666 ..."
python $CARMUSR/data/migration/CMS2_SAS34/skcms_666.py 2>&1 | tee $LOG_DIR/SKCMS-666.log

echo "  * SKCMS-766 ..."
python $CARMUSR/data/migration/CMS2_SAS34/skcms_766.py 2>&1 | tee $LOG_DIR/SKCMS-766.log

echo "  * SKCMS-699 ..."
python $CARMUSR/data/migration/CMS2_SAS34/skcms_699.py 2>&1 | tee $LOG_DIR/SKCMS-699.log


echo "  * SKCMS-837 ..."
python $CARMUSR/data/migration/CMS2_SAS34/skcms_837.py 2>&1 | tee $LOG_DIR/SKCMS-837.log



#echo " - Updating DB filters"
#db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

#echo "  Copy parameters to carmdata ..."
#cp -f $CARMUSR/crc/parameters/rostering/column_generation $CARMUSR/current_carmdata/RaveParameters/rostering/.

#cp -f $CARMUSR/crc/parameters/rostering/column_generation_short $CARMUSR/current_carmdata/RaveParameters/rostering/.

#$CARMUSR/data/migration/CMS2_SAS34/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
