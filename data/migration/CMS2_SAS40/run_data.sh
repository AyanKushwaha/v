#!/bin/sh
#
# This script performs migration related data changes for the release corresponding to the directory where it resides
#
# It is normally run without closing any other db connections
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
RELEASE=CMS2_SAS40
LOG_DIR="$CARMUSR/data/migration/$RELEASE/migration_logs_data_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo $RELEASE "Database Data Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/$RELEASE

echo " - Processing migration tasks"

echo "  * RULES_VALIDITY ..."
python $CARMUSR/data/migration/$RELEASE/rules_validity.py 2>&1 | tee $LOG_DIR/RULES_VALIDITY.log

echo "  * SKCMS-729 ..."
python $CARMUSR/data/migration/CMS2_SAS40/skcms_729.py 2>&1 | tee $LOG_DIR/SKCMS-729.log

echo "  * SKCMS-1052 ..."
python $CARMUSR/data/migration/CMS2_SAS40/skcms_1052.py 2>&1 | tee $LOG_DIR/SKCMS-1052.log

echo "  * SKCMS-1168 ..."
python $CARMUSR/data/migration/CMS2_SAS40/skcms_1168.py 2>&1 | tee $LOG_DIR/SKCMS-1168.log


echo "  * SKCMS-1176 ..."
python $CARMUSR/data/migration/CMS2_SAS40/skcms_1176.py 2>&1 | tee $LOG_DIR/SKCMS-1176.log

echo " * SKCMS-1127 ... The lifeblockhrs accumulator is run, and the logfile is pit under $CARMTMP/logfiles"
$CARMUSR/bin/accumulators/accumulator.sh lifeblockhrs




mv change* $LOG_DIR/


echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
