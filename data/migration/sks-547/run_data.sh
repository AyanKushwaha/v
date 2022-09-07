#!/bin/sh
#
# This script performs migration related data changes for the release corresponding to the directory where it resides
#
# It is normally run without closing any other db connections
#
# This has to be run after run_schema.sh
#

dir=`dirname $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
RELEASE=`basename $dir`
LOG_DIR="$CARMUSR/data/migration/sks-547/migration_logs_data_`date +%Y%m%d_%H.%M.%S`"

echo "********************************************"
echo $RELEASE "Database Data Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/sks-547

echo " - Processing migration tasks"

#### Insert migration tasks below ####
# Example:
# echo "  * sks-547: Some description"
python $CARMUSR/data/migration/sks-547/sks-547.py 2>&1 | tee $LOG_DIR/sks-547.log



# Uncomment this in case dave filters shall be modified, remember to update JIRA number
#echo "  * sks-547: Importing crc/etable/dave_filter/*.etab into database"
#$CARMUSR/bin/admin/setup/setup_filters.sh -c -d | tee -a $LOG_DIR/sks-547.log


echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
