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

echo "  * SKCMS-2546: A2LR JCRT: Legality for ETOPS LIFUS/LC"
python $CARMUSR/data/migration/$RELEASE/skcms_2546_add_cnx_time_etops.py 2>&1 | tee $LOG_DIR/skcms_2546_add_cnx_time_etops.log

echo "  * SKCMS-2557 A2LR: Add position A2_OW for A2 crew"
python $CARMUSR/data/migration/$RELEASE/skcms-2557.py 2>&1 | tee $LOG_DIR/skcms-2557.log

echo "  * SKCMS-2509: Add agreement validity cau_co_on_freeday_comp"
python $CARMUSR/data/migration/$RELEASE/skcms-2509.py 2>&1 | tee $LOG_DIR/skcms-2509.log

echo "  * SKCMS-2555: ALF is forbidden destination for SKD/SKS FP"
python $CARMUSR/data/migration/$RELEASE/skcms-2555.py 2>&1 | tee $LOG_DIR/skcms-2555.log

echo "  * SKCMS-2545: Introduce training attribute ETOPS LIFUS/LC"
python $CARMUSR/data/migration/$RELEASE/skcms-2545.py 2>&1 | tee $LOG_DIR/skcms-2545.log

echo "  * SKCMS-2545: Introduce training attribute ETOPS LIFUS/LC"
python $CARMUSR/data/migration/$RELEASE/skcms-2545.py 2>&1 | tee $LOG_DIR/skcms-2545.log

echo "  * SKCMS-2516: Latest checkout before longhaul"
python $CARMUSR/data/migration/$RELEASE/skcms-2516.py 2>&1 | tee $LOG_DIR/skcms-2516.log

echo "  * SKCMS-2564_add_validity_parameters: changes to freeday control logic "
python $CARMUSR/data/migration/$RELEASE/skcms-2564_add_validity_parameters.py 2>&1 | tee $LOG_DIR/skcms-2564_add_validity_parameters.log

# Uncomment this in case dave filters shall be modified, remember to update JIRA number
#echo "  * SKCMS-XXXX: Importing crc/etable/dave_filter/*.etab into database"
#$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SKCMS-XXXX.log


echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
