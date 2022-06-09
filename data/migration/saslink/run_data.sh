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

echo "  * SKCMS-2881: Update Link crew data"
python $CARMUSR/data/migration/$RELEASE/update_link_crew.py 2>&1 | tee $LOG_DIR/update_link_crew.log

echo "  * SKCMS-2881: Add new contracts for link crew"
python $CARMUSR/data/migration/$RELEASE/add_link_contract_employment.py 2>&1 | tee $LOG_DIR/add_link_contract_employment.log

echo "  * SKCMS-2672: Static table updates for Link"
python $CARMUSR/data/migration/$RELEASE/skcms-2762.py 2>&1 | tee $LOG_DIR/skcms-2762.log

echo "  * SKCMS-2825: Hotel customer entry for Link"
python $CARMUSR/data/migration/$RELEASE/skcms-2825.py 2>&1 | tee $LOG_DIR/skcms-2825.log

echo "  * SKCMS-2814: Aircraft type related changes for Link"
python $CARMUSR/data/migration/$RELEASE/skcms-2814.py 2>&1 | tee $LOG_DIR/skcms-2814.log

echo "  * SKCMS-2897 ..."
python $CARMUSR/data/migration/saslink/skcms_2897.py 2>&1 | tee $LOG_DIR/SKCMS-2897.log

echo "  * SKCMS-2908: Preffered Hotel entry for Link"
python $CARMUSR/data/migration/saslink/skcms-2908.py 2>&1 | tee $LOG_DIR/skcms-2908.log


echo "  * SKCMS-2827: Meal airport entry for Link"
python $CARMUSR/data/migration/saslink/skcms-2827_meal_airport.py 2>&1 | tee $LOG_DIR/skcms-2827_meal_airport.log

echo "  * SKCMS-2827: Meal customer entry for Link"
python $CARMUSR/data/migration/saslink/skcms-2827_meal_customer.py 2>&1 | tee $LOG_DIR/skcms-2827_meal_customer.log


echo "  * SKCMS-2827: Meal comsumption code entry for Link"
python $CARMUSR/data/migration/saslink/skcms-2827_meal_consumption_code.py 2>&1 | tee $LOG_DIR/skcms-2827_meal_consumption_code.log


echo "  * SKCMS-2827: Meal customer entry for Link"
python $CARMUSR/data/migration/saslink/skcms-2827_meal_supplier.py 2>&1 | tee $LOG_DIR/skcms-2827_meal_supplier.log

# Uncomment this in case dave filters shall be modified, remember to update JIRA number
#echo "  * SKCMS-XXXX: Importing crc/etable/dave_filter/*.etab into database"
#$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SKCMS-XXXX.log

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
