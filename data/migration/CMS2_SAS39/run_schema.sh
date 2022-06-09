#!/bin/sh
#
# This script performs schema channges and such things requiring exclusive access
# to the database/system, which relates to the releaes corresponding the directory
# where it resides
#
# It should only be present in migration directories where shcema changes are required.
# Running of this script requires all connections closed.
#
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
RELEASE=CMS2_SAS39
LOG_DIR="$CARMUSR/data/migration/$RELEASE/migration_logs_schema_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo $RELEASE "Database Schema Migration script"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/$RELEASE

echo " - Updating schema"
db updateschema 2>&1 | tee $UPDATE_SCHEMA_LOG

#echo " - Updating DB filters"
# Actually - not known if this need to be done when exclusive access to db, but to be on the safe side
#db updatefilters 2>&1 | tee $UPDATE_FILTERS_LOG

#echo "  Copy parameters to carmdata ..."
#cp -f $CARMUSR/crc/parameters/rostering/column_generation $CARMUSR/current_carmdata/RaveParameters/rostering/.

#cp -f $CARMUSR/crc/parameters/rostering/column_generation_short $CARMUSR/current_carmdata/RaveParameters/rostering/.

#$CARMUSR/data/migration/CMS2_SAS37/manpower_migration.sh

echo "********************************************"
echo "Migration finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
