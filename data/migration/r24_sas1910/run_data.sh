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
# echo "  * SKCMS-1234 - Some description"
# python $CARMUSR/data/migration/$RELEASE/skcms-1234.py 2>&1 | tee $LOG_DIR/skcms-1234.log
echo "  * SKCMS-2078 - FMST activity"
python $CARMUSR/data/migration/$RELEASE/skcms-2078.py 2>&1 | tee $LOG_DIR/skcms-2078.log
echo "  * SKCMS-2262 - Add MAY season for cabin crew"
python $CARMUSR/data/migration/$RELEASE/skcms-2262.py 2>&1 | tee $LOG_DIR/skcms-2262.log
echo "  * SKCMS-2188: Importing crc/etable/dave_filter/*.etab into database"
$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SKCMS-2188.log

echo "  * SKAM-785 - Fix/Remove of unused crc/parameters files"
bash crc-parameters.sh 2>&1 | tee $LOG_DIR/skam-785.log
echo "  * SKCMS-2088 - A350 with AL qual require TW99"
python $CARMUSR/data/migration/$RELEASE/skcms-2088.py 2>&1 | tee $LOG_DIR/skcms-2088.log
echo "  * SKCMS-2153 - A5 crew needs AST in PC grace period"
python $CARMUSR/data/migration/$RELEASE/skcms-2153.py 2>&1 | tee $LOG_DIR/skcms-2153.log
echo "  * SKCMS-2118 - New sick deduction rules"
python $CARMUSR/data/migration/$RELEASE/skcms-2118.py 2>&1 | tee $LOG_DIR/skcms-2118.log

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
