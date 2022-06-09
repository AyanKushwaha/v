#!/bin/sh
#
# This script performs migration related model changes for CMS2 SAS 13
#
# Included migrations:
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SAS13/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 SAS 13 Database Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SAS13

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

echo " - Processing migration tasks"

# echo "  * Compiling Tracking rulesets ..."
# rave compile cct 2>&1 | tee $RAVE_COMPILE_LOG

echo "  * SASCMS-6304 ..."
python $CARMUSR/data/migration/CMS2_SAS13/sascms-6304.py 2>&1 | tee $LOG_DIR/SASCMS-6304.log

echo "  * SASCMS-6381 ... populate JMP table"
$CARMUSR/data/migration/CMS2_SAS13/sascms-6381.sh 2>&1 | tee $LOG_DIR/SASCMS-6381.log

#echo "  Copy parameters to carmdata ..."
#cp -f $CARMUSR/crc/parameters/tracking/request_reportserver $CARMUSR/current_carmdata/RaveParameters/tracking/request_reportserver
#cp -f $CARMUSR/crc/parameters/tracking/studio $CARMUSR/current_carmdata/RaveParameters/tracking/studio
#cp -f $CARMUSR/crc/parameters/tracking/alertgenerator $CARMUSR/current_carmdata/RaveParameters/tracking/alertgenerator
#cp -f $CARMUSR/crc/parameters/tracking/rule_info $CARMUSR/current_carmdata/RaveParameters/tracking/rule_info


#echo " - Updating DB filters"
#db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

#$CARMUSR/data/migration/CMS2_SAS13/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
