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
    LOG_DIR="$CARMUSR/data/migration/CMS2_SP6.1/migration_logs_`date +%Y%m%d_%H.%M.%S`"
fi

unset CARM_PRE_PYTHONPATH
unset CARMSYS
export SK_APP=Manpower

cd $CARMUSR
. $CARMUSR/bin/carmenv.sh

echo $PYTHONPATH
prependDirs PYTHONPATH $CARMSYS/lib/python $CARMSYS/lib/python/$ARCH
echo $PYTHONPATH

echo "  * Interbids SP6 Migration ..."
echo "  * Populating tables"

python $CARMUSR/data/migration/CMS2_SP6.1/skbmm731.py 2>&1 | tee $LOG_DIR/skbmm731.log
python $CARMUSR/data/migration/CMS2_SP6.1/interbidsMigration.py 2>&1 | tee $LOG_DIR/interbidsMigration.log
python $CARMUSR/data/migration/CMS2_SP6.1/skbmm600.py 2>&1 | tee $LOG_DIR/skbmm600.log
python $CARMUSR/data/migration/CMS2_SP6.1/skbmm700.py 2>&1 | tee $LOG_DIR/skbmm700.log
python $CARMUSR/data/migration/CMS2_SP6.1/skbmm735.py 2>&1 | tee $LOG_DIR/skbmm735.log
