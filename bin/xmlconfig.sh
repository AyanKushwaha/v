#!/bin/sh
# $$
#
# Wrapper script for evaluating xml-config settings.
#

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
. $CARMUSR/bin/carmenv.sh

$CARMSYS/bin/xmlconfig $@
