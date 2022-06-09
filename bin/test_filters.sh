#!/bin/sh
# Sets the CARMUSR variable, if it is not set
if [ -z "$CARMUSR" ]; then
  a=`pwd`
  cd `dirname $0`
  while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
  done
  CARMUSR=`pwd`
  export CARMUSR
  cd $a
fi

unset CARM_PRE_PYTHONPATH
unset CARMSYS

SK_APP=Manpower
export SK_APP

. $CARMUSR/bin/carmenv.sh

echo "CARMSYS:" $CARMSYS
echo "CARMTMP:" $CARMTMP
echo "CARMUSR:" $CARMUSR
$CARMSYS/bin/mirador -s adhoc.test_filters $@
