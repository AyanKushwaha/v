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
RELEASE=r24_sas1903
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

echo "  * SAS1903..."
echo " *Updating all A3A4 qualifications to AWB (Airbus widebody) SKCMS-2054"
python $CARMUSR/data/migration/$RELEASE/AWB_qual.py 2>&1 | tee -a $LOG_DIR/SAS1903.log
echo " *Adding validity parameter for additional briefing time for SKN and SKD SKCMS-2028"
python $CARMUSR/data/migration/$RELEASE/2028_add_validity_parameter.py 2>&1 | tee -a $LOG_DIR/SAS1903.log
echo " *Adding FAM FLT course type in JMP. SKCMS-2067"
python $CARMUSR/data/migration/$RELEASE/FAM_FLT.py 2>&1 | tee -a $LOG_DIR/SAS1903.log
echo " * SKCMS-1968 Adding validiy parameter for norwegian contract groups"
python $CARMUSR/data/migration/$RELEASE/1968_add_agreement_validity.py 2>&1 | tee -a $LOG_DIR/SAS1903.log


echo " * Add table ADDITIONAL_REST by reading information from sas_legality.xml, SKS-211"
db updateschema | tee -a $LOG_DIR/SAS1903.log


echo "  * SAS1903 ..."

echo "  * Updating dave filters ..."
bash $CARMUSR/bin/admin/setup/setup_filters.sh -c

#mv change* $LOG_DIR/


echo "********************************************"
echo "Migration finished"
echo "  Check for possible problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo "Migration finished"
echo "  Check for possible problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo "Migration finished"
echo "  Check for possible problems in:"
echo "  * SAS1903 ..."

