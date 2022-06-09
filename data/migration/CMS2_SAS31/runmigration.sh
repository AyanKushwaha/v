#!/bin/sh
#
# This script performs migration related model changes for CMS2 SAS 31
#
# Included migrations:
# Agreement groups created
# crew_contract_set changed to reference to ag 
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SAS31/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SAS 31 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SAS31

#echo " - Updating schema"
#db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

# echo "  * Compiling Tracking rulesets ..."
# rave compile cct 2>&1 | tee $RAVE_COMPILE_LOG

echo "  * RULES_VALIDITY ..."
python $CARMUSR/data/migration/CMS2_SAS31/rules_validity.py 2>&1 | tee $LOG_DIR/SAS31_VALIDITY.log

echo "  * SKCMS-761 ..."
python $CARMUSR/data/migration/CMS2_SAS31/skcms_761.py 2>&1 | tee $LOG_DIR/SKCMS-761.log

echo "  * SKCMS-566 ..."
python $CARMUSR/data/migration/CMS2_SAS31/skcms_566.py 2>&1 | tee $LOG_DIR/SKCMS-566.log

echo "  * SKCMS-691 ..."
python $CARMUSR/data/migration/CMS2_SAS31/skcms_691.py 2>&1 | tee $LOG_DIR/SKCMS-691.log

echo "  * SKCMS-712 ..."
python $CARMUSR/data/migration/CMS2_SAS31/skcms_712.py 2>&1 | tee $LOG_DIR/SKCMS-712.log

echo "  * SKCMS-784 ..."
python $CARMUSR/data/migration/CMS2_SAS31/skcms_784.py 2>&1 | tee $LOG_DIR/SKCMS-784.log

echo "  * SKCMS-645 ..."
python $CARMUSR/data/migration/CMS2_SAS31/skcms_645.py 2>&1 | tee $LOG_DIR/SKCMS-645.log

echo "  * SKCMS-691v ..."
python $CARMUSR/data/migration/CMS2_SAS31/skcms_691v.py 2>&1 | tee $LOG_DIR/SKCMS-691v.log

echo " - Updating DB filters"
#db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

echo "  Copy parameters to carmdata ..."
#cp -f $CARMUSR/crc/parameters/rostering/column_generation $CARMUSR/current_carmdata/RaveParameters/rostering/.

#cp -f $CARMUSR/crc/parameters/rostering/column_generation_short $CARMUSR/current_carmdata/RaveParameters/rostering/.

#$CARMUSR/data/migration/CMS2_SAS31/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
