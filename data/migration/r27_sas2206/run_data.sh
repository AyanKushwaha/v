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
echo "  * SKCMS-2922: Splitting ETOPS LIFUS/LC"
python $CARMUSR/data/migration/$RELEASE/skcms-2922.py 2>&1 | tee $LOG_DIR/skcms-2922.log

echo "  * SKCMS-2975: Add LC AP-POS to table training_log_set"
python $CARMUSR/data/migration/$RELEASE/skcms-2975.py 2>&1 | tee $LOG_DIR/skcms-2975.log


echo "  * SKCMS-2774: TE: Overtime Pay for checkout on day off for Link crew"
python $CARMUSR/data/migration/$RELEASE/skcms-2774.py 2>&1 | tee $LOG_DIR/skcms-2774.log

echo "  * SKCMS-3022: Link Salary addition for flight duty hours"
python $CARMUSR/data/migration/$RELEASE/skcms-3022.py 2>&1 | tee $LOG_DIR/skcms-3022.log

# Uncomment this in case dave filters shall be modified, remember to update JIRA number
#echo "  * SKCMS-XXXX: Importing crc/etable/dave_filter/*.etab into database"
#$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SKCMS-XXXX.log

echo "  * SKCMS-2740: Alert gen Crash issue"
python $CARMUSR/data/migration/$RELEASE/skcms-2740.py 2>&1 | tee $LOG_DIR/skcms-2740.log

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
