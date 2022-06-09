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
RELEASE=r24_sas72
LOG_DIR="$CARMUSR/data/migration/$RELEASE/migration_logs_data_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo $RELEASE "Database Data Migration script"
echo "********************************************"
echo $CARMUSR
echo $RELEASE
echo $LOG_DIR
echo $UPDATE_SCHEMA_LOG
echo $UPDATE_FILTERS_LOG
echo $RAVE_COMPILE_LOG
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/$RELEASE

echo " - Processing migration tasks"

echo "  * SAS72 ..."
echo "  * Updating salary articales, SKAM-745 "
python $CARMUSR/data/migration/$RELEASE/update_salary_article.py 2>&1 | tee -a $LOG_DIR/SAS72.log

echo "  * SAS72 ..."
echo "  * Adding validiy parameter for set  F36 entitlement zero for SKN CC , SKAM-1908 "
python $CARMUSR/data/migration/$RELEASE/1908_add_agreement_validity.py 2>&1 | tee -a $LOG_DIR/SAS72.log

echo "  * Add agreement validity, SKCMS-1879"
python $CARMUSR/data/migration/$RELEASE/1879_add_agreement_validity.py 2>&1 | tee -a $LOG_DIR/SAS72.log

#mv change* $LOG_DIR/


echo "********************************************"
echo "Migration finished"
echo "  Check for possible problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
