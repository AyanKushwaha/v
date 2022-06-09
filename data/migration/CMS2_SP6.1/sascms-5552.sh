#!/bin/sh
echo "************************************************************"
echo "* SASCMS-5552: migration of preferred_hotel_exc:           *"
echo "*     Migrating table by adding flight_nr to primary key.  *"
echo "*     This script will copying a model to drop the current *"
echo "*     version of the table and running updateschema, then  *"
echo "*     copy back the correct version and run updateschema   *"
echo "*     again. This will add the new version of the table.   *"
echo "************************************************************"
echo ""
DB_ERROR=$LOG_DIR/sascms-5552_DB_ERROR.log

source $CARMUSR/bin/carmenv.sh
db sql "select dep_flight_nr from preferred_hotel_exc" 2> $DB_ERROR > /dev/null

if [ $? != "1" ]; then
    echo "ERROR"
    echo "  SASCMS-5552 has already been migrated in this"
    echo "  database or some problem connecting to the"
    echo "  database. Make sure cmsshell is setup. Ceck db"
    echo "  error log for more info in:"
    echo "  $DB_ERROR"
    echo "************************************************************"
    exit 1
fi

echo "Saving data from preferred_hotel_exc"
python `dirname $0`/sascms-5552_save.py

source `dirname $0`/migrate_single_table.sh
migrate_table sas_air_crew preferred_hotel_exc

if [ $? != "0" ]; then
    exit 1
fi

echo "Loading data to preferred_hotel_exc"
python `dirname $0`/sascms-5552_load.py