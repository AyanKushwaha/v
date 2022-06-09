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
RELEASE=r24_sas77
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

echo "  * SAS77 ..."
echo " * Adding validiy parameter for norvegian contract groups"
python $CARMUSR/data/migration/$RELEASE/1968_add_agreement_validity.py 2>&1 | tee -a $LOG_DIR/SAS77.log
echo " * Adding validiy parameter for SKD CC F36 quotas (F00660, F00661 and VG 90%) SKCMS-2002 "
python $CARMUSR/data/migration/$RELEASE/2002_add_agreement_validity.py 2>&1 | tee -a $LOG_DIR/SAS77.log
echo " * Importing dave_filter_ref.etab and dave_entity_filter.etab into database SKCMS-1980"
$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SAS77.log
echo " * Adding FS1 activity in SAS77 (needed because of db dump)"
python $CARMUSR/data/migration/$RELEASE/FS1_activity.py 2>&1 | tee -a $LOG_DIR/SAS77.log

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
