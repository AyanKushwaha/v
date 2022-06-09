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
RELEASE=add_crew_ccd
LOG_DIR="$CARMUSR/current_carmtmp/migration_add_crew_ccd_logs_data_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"
echo "********************************************"
echo $RELEASE "Database Data Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

{
echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

echo "********************************************"
echo "Adding the hg patch"
echo "********************************************"

#cd $CARMUSR
#patch -p1 < $CARMUSR/data/migration/add_crew_ccd/add_convertor_logger.patch 

echo "********************************************"
echo "Running the migration"
echo "********************************************"

cd $CARMUSR/data/migration/$RELEASE

echo " - Processing migration tasks"

echo "  * add_crew ..."
python $CARMUSR/data/migration/add_crew_ccd/add_crew.py 
# python $CARMUSR/data/migration/add_crew_ccd/add_crew.py 


echo "********************************************"
echo "Running the updateCrewUserFilter.sh to make changes take effect"
echo "********************************************"
$CARMUSR/bin/updateCrewUserFilter.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for possible problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
} 2>&1 | tee $LOG_DIR/add_crew.log
