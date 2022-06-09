#!/bin/bash

wherami=`dirname $0`
_CARMUSR=`(cd $wherami/../..; pwd)`

SK_APP=Tracking
export SK_APP

# If CARMUSR not set, use current directory as reference point.
CARMUSR=${CARMUSR-"${_CARMUSR}"}
export CARMUSR

echo "loading CMS shell environment ..."
. $CARMUSR/bin/carmenv.sh

logdir="$CARMTMP/logfiles"
[ ! -d $logdir ] && mkdir -p $logdir
logfile="$logdir/DELAYCODE_IMPORT.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"

exec &> >(tee -i $logfile)

echo "[$(date)]"
echo "starting script delay_code_import.sh ..."

exec python $CARMUSR/lib/python/carmusr/calibration/delaycodes_to_etab.py $@ 

echo "Script finished"
echo "[$(date)]"

