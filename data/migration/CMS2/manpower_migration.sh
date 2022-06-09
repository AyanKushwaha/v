#!/bin/sh
echo "********************************************"
echo "*   - Running `basename $BASH_SOURCE`"
echo "********************************************"

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
if [ -z $1 ];then
    LOG_DIR="`pwd`"
else
    LOG_DIR="$1"
fi

unset CARM_PRE_PYTHONPATH
unset CARMSYS
export SK_APP=Manpower

cd $CARMUSR
. $CARMUSR/bin/carmenv.sh

echo " - Running migrate_cms1_to_cms2.sh..."
$CARMUSR/bin/manpower/migrate_cms1_to_cms2.sh

echo $PYTHONPATH
prependDirs PYTHONPATH $CARMSYS/lib/python $CARMSYS/lib/python/$ARCH
echo $PYTHONPATH

echo " - Running migrating Manpower via Mirador..."
$CARMUSR/bin/manpower/start-mirador_prompt.sh <<EOF
print "------------------------------------------"
print "About to do manpower migration tasks..."
print " - Task 1/3: remove_redundant_data_est_task"
import carmusr.manpower.util.remove_redundant_data_est_task
print " - Task 2/3: migrate_establishment"
import carmensystems.manpower.util.migrate_establishment
print " - Task 3/3; migrate_cms1_to_cms2"
import carmusr.manpower.util.migrate_cms1_to_cms2
print "Migration tasks finished"
print "------------------------------------------"
EOF

python $CARMUSR/lib/python/adhoc/sascms-3732.py 2>&1 | tee $LOG_DIR/SASCMS-3732.log
