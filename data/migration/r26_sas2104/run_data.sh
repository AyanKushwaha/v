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

echo "  * SKCMS-2613: Delete course type ETOPS LR from course_type table"
python $CARMUSR/data/migration/$RELEASE/2613_update_course_typ.py 2>&1 | tee $LOG_DIR/2613_update_course_typ.log

echo "  * SKCMS-2613: Update qual set from POSITION A2LR to POSITION A2NX in crew_qualification_set table"
python $CARMUSR/data/migration/$RELEASE/2613_update_qual_set.py 2>&1 | tee $LOG_DIR/2613_update_qual_set.log

echo "  * SKCMS-2613: Update aircraft_type from LR to NX in aircraft_type table"
python $CARMUSR/data/migration/$RELEASE/2613_update_actype.py 2>&1 | tee $LOG_DIR/2613_update_actype.log

echo "  * SKCMS-2613: Rename position A2LR to A2NX in crew_qualification table"
python $CARMUSR/data/migration/$RELEASE/2613_update_crewqual.py 2>&1 | tee $LOG_DIR/2613_update_crewqual.log

# Uncomment this in case dave filters shall be modified, remember to update JIRA number
#echo "  * SKCMS-XXXX: Importing crc/etable/dave_filter/*.etab into database"
#$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SKCMS-XXXX.log


echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
