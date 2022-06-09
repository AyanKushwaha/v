#!/bin/sh
echo "********************************************"
echo "*   - Running `basename $BASH_SOURCE`"
echo "********************************************"

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
if [ -z $LOG_DIR ];then
    LOG_DIR="$CARMUSR/data/migration/CMS2_SP4.3/migration_logs_`date +%Y%m%d_%H.%M.%S`"
fi

unset CARM_PRE_PYTHONPATH
unset CARMSYS
export SK_APP=Manpower

cd $CARMUSR
. $CARMUSR/bin/carmenv.sh

echo $PYTHONPATH
prependDirs PYTHONPATH $CARMSYS/lib/python $CARMSYS/lib/python/$ARCH
echo $PYTHONPATH

echo "  * SASCMS-2984 ..."
echo "  * Adding entries in est_task"
python $CARMUSR/data/migration/CMS2_SP4.3/sascms-2984.py 2>&1 | tee $LOG_DIR/SASCMS-2984.log

echo "  * SASCMS-4919 ..."
echo "  * Checking if the award_key column size in bid_leave_vacation needs to be changed ..."
$CARMUSR/data/migration/CMS2_SP4.3/sascms-4919.sh 2>&1 | tee $LOG_DIR/SASCMS-4919.log

echo "  * SASCMS-4945 ..."
echo "  * Set the award_key in bid_leave_vacation table for bids between 1jan2012 and 6jan2013 for Cabin Crew and between 1jan2012 and 31may2013 for Flight..."
$CARMUSR/bin/startMirador.sh --manpower --script -s adhoc.sascms-4945 2>&1 | tee $LOG_DIR/SASCMS-4945.log
