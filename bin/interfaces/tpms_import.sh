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
logfile="$logdir/TPMS_IMPORT.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"

exec &> >(tee -i $logfile)

echo "[$(date)]"
echo "starting script tpms_import.sh ..."

exec python $CARMUSR/lib/python/interfaces/tpms_import_runner.py --daemon --save

echo "Script finished"
echo "[$(date)]"

