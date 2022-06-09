#!/bin/sh


echo "[$(date)] Starting script updateCrewUserFilter.sh"

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




echo CARMUSR: $CARMUSR


SK_APP=Server
export SK_APP
echo SK_APP:: $SK_APP

. $CARMUSR/bin/carmenv.sh

#TRACE_ON=5
#TRACE_SOURCE=On
#TRACE_SQL=On
#TRACE_DMFramework=3
#export TRACE_ON TRACE_SQL TRACE_SOURCE TRACE_DMFramework
#PYTHONPATH=$CARMSYS/lib/python/carmensystems/mave/gm/compat:$PYTHONPATH
echo PYTHONPATH:$PYTHONPATH
export PYTHONPATH
        
$CARMSYS/bin/mirador -s carmusr.FilterHandler "standalone" $1 $2 $3

echo "[$(date)] Script finished"
