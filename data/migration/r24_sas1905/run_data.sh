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
RELEASE=r24_sas1905
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

echo " * SKCMS-2177 Adding validiy parameter for 160 hrs duty per month rule"
python $CARMUSR/data/migration/$RELEASE/skcms-2177.py 2>&1 | tee -a $LOG_DIR/skcms-2177.log


echo "  * SK_1905..."
echo "  * Adding validity parameter - 60h_rest_3_day_wops_cc"
python $CARMUSR/data/migration/$RELEASE/2178_add_agreement_validity.py 2>&1 | tee $LOG_DIR/SK_1905.log

# Apply new dave filters SKCMS-1980 (also test for bugfix in SKCMS-2180)
$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SAS1905.log
echo "  * SKCMS-2083 - Handle PC/OPC for A350"
python $CARMUSR/data/migration/$RELEASE/skcms-2083.py 2>&1 | tee $LOG_DIR/skcms-2083.log
echo "  * SKCMS-2087 - Cabin crew training for A350"
python $CARMUSR/data/migration/$RELEASE/skcms-2087.py 2>&1 | tee $LOG_DIR/skcms-2087.log
echo "  * SKCMS-2068 - Validity parameter for changes regarding rescheduling"
python $CARMUSR/data/migration/$RELEASE/skcms-2068.py 2>&1 | tee $LOG_DIR/skcms-2068.log

echo "  * SKCMS-1951 - Split AST periods into qualification groups"
python $CARMUSR/data/migration/$RELEASE/skcms-1951.py 2>&1 | tee $LOG_DIR/skcms-1951.log

echo "  * SKCMS-2173 - Add AST period for A5"
python $CARMUSR/data/migration/$RELEASE/skcms-2173.py 2>&1 | tee $LOG_DIR/skcms-2173.log

echo "  * SKCMS-2115 - Cabin crew training for A350 part 2"
python $CARMUSR/data/migration/$RELEASE/skcms-2115.py 2>&1 | tee $LOG_DIR/skcms-2115.log

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
