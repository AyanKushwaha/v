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
    LOG_DIR="$CARMUSR/data/migration/CMS2_SP5/migration_logs_`date +%Y%m%d_%H.%M.%S`"
fi

unset CARM_PRE_PYTHONPATH
unset CARMSYS
export SK_APP=Manpower

cd $CARMUSR
. $CARMUSR/bin/carmenv.sh

echo $PYTHONPATH
prependDirs PYTHONPATH $CARMSYS/lib/python $CARMSYS/lib/python/$ARCH
echo $PYTHONPATH

echo "  * SASCMS-5079 ..."
echo "  * Add attribute \"NO ATTRIBUTE\" to table crew_training_t_set"
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5079.py 2>&1 | tee $LOG_DIR/SASCMS-5079.log

echo "  * SKBMM-647 ..."
echo "  * Validation fix for ExtraVacation bid"
python $CARMUSR/data/migration/CMS2_SP5.1/skbmm-647.py 2>&1 | tee $LOG_DIR/SKBMM-647.log

echo "  * SASCMS-5403 ..."
echo "  * Add new entries in leave_entitlement for norwegian crew"
python $CARMUSR/data/migration/CMS2_SP5.1/sascms-5403.py 2>&1 | tee $LOG_DIR/SASCMS-5403.log

