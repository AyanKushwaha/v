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
echo " *Add CMR course document for Cabin Crew. CRMC and OCRC valid from 1 January 2020 SKCMS-2255"
python $CARMUSR/data/migration/$RELEASE/2255_add_CRM_for_CC.py 2>&1 | tee -a $LOG_DIR/skcms-2255.log
echo " *Add new recurrent document type for Cabin Crew SKCMS-2256"
python $CARMUSR/data/migration/$RELEASE/2256_add_new_rec_type_cc.py 2>&1 | tee -a $LOG_DIR/skcms-2256.log
echo "  * SKCMS-2266: Migrate Jeppesen database changes"
etabdiff -na -c ${DB_URL} -s $DB_SCHEMA K19_etabs/
echo "  * SKCMS-2257 - Crew recurrent set"
python $CARMUSR/data/migration/$RELEASE/skcms-2257_crew_recurrent_set.py 2>&1 | tee $LOG_DIR/skcms-2257_1.log
echo "  * SKCMS-2257 - Add validity"
python $CARMUSR/data/migration/$RELEASE/2257_add_agreement_validity.py 2>&1 | tee $LOG_DIR/skcms-2257_3.log




# Uncomment this in case dave filters shall be modified, remember to update JIRA number
echo "  * SKCMS-2266: Importing crc/etable/dave_filter/*.etab into database"
$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SKCMS-2266.log

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
