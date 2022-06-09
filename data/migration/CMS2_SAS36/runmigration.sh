#!/bin/sh
#
# This script performs migration related model changes for CMS2 SAS 36
#
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SAS36/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SAS 36 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SAS36

#echo " - Updating schema"
#db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

echo "  * RULES_VALIDITY ..."
python $CARMUSR/data/migration/CMS2_SAS36/rules_validity.py 2>&1 | tee $LOG_DIR/SAS36_VALIDITY.log


echo "  * SKCMS-400 ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_400.py 2>&1 | tee $LOG_DIR/SKCMS-400.log

echo "  * SKCMS-677 ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_677.py 2>&1 | tee $LOG_DIR/SKCMS-677.log

echo "  * SKCMS-837b ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_837b.py 2>&1 | tee $LOG_DIR/SKCMS-837b.log

echo "  * SKCMS-981 ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_981.py 2>&1 | tee $LOG_DIR/SKCMS-981.log

mv change* $LOG_DIR/

#echo " - Updating DB filters"
#db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

#echo "  Copy parameters to carmdata ..."
#cp -f $CARMUSR/crc/parameters/rostering/column_generation $CARMUSR/current_carmdata/RaveParameters/rostering/.

#cp -f $CARMUSR/crc/parameters/rostering/column_generation_short $CARMUSR/current_carmdata/RaveParameters/rostering/.

#$CARMUSR/data/migration/CMS2_SAS36/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
