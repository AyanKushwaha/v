#!/bin/sh
#
# This script performs migration related data changes for the release corresponding to the directory where it resides
#
# It is normally run without closing any other db connections
#

dir=`dirname $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
RELEASE=`basename $dir`
LOG_DIR="$CARMUSR/data/migration/$RELEASE/migration_logs_data_`date +%Y%m%d_%H.%M.%S`"

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

#### Insert migration tasks below ####
# Example:
# echo "  * SKCMS-1234: Some description"
# python $CARMUSR/data/migration/$RELEASE/skcms-1234.py 2>&1 | tee $LOG_DIR/skcms-1234.log

# Uncomment this in case dave filters shall be modified, remember to update JIRA number
#echo "  * SKCMS-XXXX: Importing crc/etable/dave_filter/*.etab into database"
#$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SKCMS-XXXX.log

echo "  * SKCMS-2333 A2LR: Add Q2LR to activity_set and activity_set_period tables"
python $CARMUSR/data/migration/$RELEASE/skcms_2333_add_Q2LR_activity.py 2>&1 | tee $LOG_DIR/skcms_2333_add_Q2LR_activity.log
echo "  * SKCMS-2329 A2LR: Add Pos A2LR for A2 crew"
python $CARMUSR/data/migration/$RELEASE/skcms_2329_add_position_A2LR.py 2>&1 | tee $LOG_DIR/skcms_2329_add_position_A2LR.log
echo "  * SKCMS-2333 A2LR: Add Q2LR to activity_set and activity_set_period tables"
python $CARMUSR/data/migration/$RELEASE/skcms_2333_add_Q2LR_activity.py 2>&1 | tee $LOG_DIR/skcms_2333_add_Q2LR_activity.log



echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
