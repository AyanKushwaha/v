#!/bin/sh
#
# This script performs conversion of 36 qualification codes to 38
#
# The scripts behaves like normal migration scripts, but is separate and need not be run at the same time
#
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
LOG_DIR="$CARMUSR/data/migration/CMS2_SAS36/migration_logs_`date +%Y%m%d_%H.%M.%S`"
UPDATE_SCHEMA_LOG="$LOG_DIR/database_update.log"
UPDATE_FILTERS_LOG="$LOG_DIR/database_update_filters.log"
RAVE_COMPILE_LOG="$LOG_DIR/rave_compile.log"

echo "********************************************"
echo "CMS2 Test skcms_703b.py and skcms_703a. only"
echo "********************************************"

echo " - Setting up ..."

echo "  * Creating log dir $LOG_DIR ..."
mkdir -p $LOG_DIR

echo "  * Setting up CARMENV ..."
. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/CMS2_SAS36



# first convert the BIG table, 50'000 operations per commit. There are about 300000 matching rows, so 7 turns should be enough

echo "  * SKCMS-703b 1 ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_703b.py 2>&1 | tee $LOG_DIR/SKCMS-703b1.log
mv changed_crew_training_log.py $LOG_DIR/changed_crew_training_log_1.py

echo "  * SKCMS-703b 2 ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_703b.py 2>&1 | tee $LOG_DIR/SKCMS-703b2.log
mv changed_crew_training_log.py $LOG_DIR/changed_crew_training_log_2.py

echo "  * SKCMS-703b 3 ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_703b.py 2>&1 | tee $LOG_DIR/SKCMS-703b3.log
mv changed_crew_training_log.py $LOG_DIR/changed_crew_training_log_3.py

echo "  * SKCMS-703b 4 ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_703b.py 2>&1 | tee $LOG_DIR/SKCMS-703b4.log
mv changed_crew_training_log.py $LOG_DIR/changed_crew_training_log_4.py

echo "  * SKCMS-703b 5 ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_703b.py 2>&1 | tee $LOG_DIR/SKCMS-703b5.log
mv changed_crew_training_log.py $LOG_DIR/changed_crew_training_log_5.py

echo "  * SKCMS-703b 6 ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_703b.py 2>&1 | tee $LOG_DIR/SKCMS-703b6.log
mv changed_crew_training_log.py $LOG_DIR/changed_crew_training_log_6.py

echo "  * SKCMS-703b 7 ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_703b.py 2>&1 | tee $LOG_DIR/SKCMS-703b7.log
mv changed_crew_training_log.py $LOG_DIR/changed_crew_training_log_7.py

# this is the rest of tables
echo "  * SKCMS-703a ..."
python $CARMUSR/data/migration/CMS2_SAS36/skcms_703a.py 2>&1 | tee $LOG_DIR/SKCMS-703a.log
mv changed* $LOG_DIR/



echo "********************************************"
echo "Test finished"
echo "  Check for eventual problems in:"
echo "  $LOG_DIR"
echo "********************************************"
echo ""
echo "  $LOG_DIR"
echo "********************************************"
echo ""
