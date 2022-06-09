#!l/bin/sh
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
echo " *Add CMR course document for Cabin Crew. CRMC and OCRC valid from 1 January 2020 SKCMS-2255"
python $CARMUSR/data/migration/$RELEASE/2255_add_CRM_for_CC.py 2>&1 | tee -a $LOG_DIR/SAS1911.log
python $CARMUSR/data/migration/$RELEASE/skcms-2282.py 2>&1 | tee $LOG_DIR/skcms-2282.log

echo "  * SKCMS-2248: Change F0 activity group to F4XNG"
python $CARMUSR/data/migration/$RELEASE/skcms-2248.py 2>&1 | tee $LOG_DIR/skcms-2248.log

# Uncomment this in case dave filters shall be modified, remember to update JIRA number
#echo "  * SKCMS-XXXX: Importing crc/etable/dave_filter/*.etab into database"
#$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SKCMS-XXXX.log


echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
