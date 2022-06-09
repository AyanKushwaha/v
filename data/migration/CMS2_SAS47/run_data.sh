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
RELEASE=CMS2_SAS47
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


echo "  * SKCMS-1434 ..."
python $CARMUSR/data/migration/$RELEASE/skcms_1434.py 2>&1 | tee $LOG_DIR/SKCMS-1434.log

echo "  * SKCMS-1052 ..."
python $CARMUSR/data/migration/$RELEASE/skcms_1052_article_codes.py 2>&1 | tee $LOG_DIR/SKCMS-1052_article_codes.log


echo "  * SKCMS-448 ..."
python $CARMUSR/data/migration/$RELEASE/skcms_448.py 2>&1 | tee $LOG_DIR/SKCMS-448.log

echo "  * SKPROJ-45a ..."
python $CARMUSR/data/migration/$RELEASE/skproj_45a.py 2>&1 | tee $LOG_DIR/SKPROJ-45A.log

echo "  * SKCMS-921 ..."
python $CARMUSR/data/migration/$RELEASE/skcms_921_period_filter.py 2>&1 | tee $LOG_DIR/SKCMS-921.log

mv change* $LOG_DIR/


echo "********************************************"
echo "Migration finished"
echo "  Check for possible problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
