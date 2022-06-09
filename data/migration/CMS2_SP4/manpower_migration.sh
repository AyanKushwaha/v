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
    LOG_DIR="$CARMUSR/data/migration/CMS2_SP4/migration_logs_`date +%Y%m%d_%H.%M.%S`"
fi

unset CARM_PRE_PYTHONPATH
unset CARMSYS
export SK_APP=Manpower

cd $CARMUSR
. $CARMUSR/bin/carmenv.sh

echo $PYTHONPATH
prependDirs PYTHONPATH $CARMSYS/lib/python $CARMSYS/lib/python/$ARCH
echo $PYTHONPATH

echo "  * Running migration_to_bids ..."
$CARMUSR/bin/startMirador.sh --script -s carmusr.manpower.util.migration_to_bids 2>&1 | tee $LOG_DIR/migration_to_bids.log

echo "  * Running migrate_bids_prio_to_bidorder ..."
bin/startMirador.sh --manpower --script -s carmensystems.manpower.util.migrate_bids_prio_to_bidorder 2>&1 | tee $LOG_DIR/migrate_bids_prio_to_bidorder.log

