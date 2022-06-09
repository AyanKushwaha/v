#!/bin/sh
#
# This script adds fake data for SAS Link testing purposes
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

#echo "  * SKCMS-2778: Add or update fake crew"
#python $CARMUSR/data/migration/$RELEASE/add_fake_svs_crew.py 2>&1 | tee $LOG_DIR/add_fake_svs_crew.log

echo "  * SKCMS-2778: Change some SKD crew to SVS"
python $CARMUSR/data/migration/$RELEASE/change_crew_to_svs.py 2>&1 | tee $LOG_DIR/change_crew_to_svs.log

# Uncomment this in case dave filters shall be modified, remember to update JIRA number
#echo "  * SKCMS-XXXX: Importing crc/etable/dave_filter/*.etab into database"
#$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/SKCMS-XXXX.log

echo "  * Updating Crew User Filter"
$CARMUSR/bin/updateCrewUserFilter.sh 2>&1 | tee $LOG_DIR/change_crew_to_svs.log

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"