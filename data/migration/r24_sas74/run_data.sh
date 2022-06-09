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
RELEASE=r24_sas74
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

echo "  * SAS74 ..."
python $CARMUSR/data/migration/$RELEASE/F0_bidding.py 2>&1 | tee -a $LOG_DIR/SAS74.log
python $CARMUSR/data/migration/$RELEASE/F7S_modify.py 2>&1 | tee -a $LOG_DIR/SAS74.log 
#mv change* $LOG_DIR/
echo "  * Updating dave filters ..."
bash $CARMUSR/bin/admin/setup/setup_filters.sh -c
echo "  * Fixing crew that has incorrect validto, see SKCMS-1977/SKS-191"
python $CARMUSR/lib/python/adhoc/sks_191_fix_crew_user_filter.py 2>&1 | tee -a $LOG_DIR/SAS74.log
echo "  * Adding agreement validity and account set for SKCMS-1911"
python $CARMUSR/data/migration/$RELEASE/1911_FX_Compensation.py 2>&1 | tee -a $LOG_DIR/SAS74.log

echo "********************************************"
echo "Migration finished"
echo "  Check for possible problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
