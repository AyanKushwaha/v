#!/bin/bash

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

# Sets CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
if [ -z "$CARMSYS" ]; then
  . $CARMUSR/bin/carmenv.sh
fi

python $CARMUSR/lib/python/behave/test_behave.py $@