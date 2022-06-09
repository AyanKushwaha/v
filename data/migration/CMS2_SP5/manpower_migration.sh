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

echo "  * SASCMS-4887 ..."
echo "  * Enable consume strategy for Establishment View"
python $CARMUSR/data/migration/CMS2_SP5/sascms-4887.py 2>&1 | tee $LOG_DIR/SASCMS-4887.log

echo "  * SKBMM-450 ..."
echo "  * Validation fix for ExtraVacation bid"
python $CARMUSR/data/migration/CMS2_SP5/skbmm-450.py 2>&1 | tee $LOG_DIR/SKBMM-450.log
