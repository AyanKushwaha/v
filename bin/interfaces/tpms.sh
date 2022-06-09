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
logfile="$logdir/TPMS.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"
#logfile="fakelog.txt"

exec &> >(tee -i $logfile)



echo "[$(date)]"
echo "starting script tpms.sh ..."

cmd=$1
echo "    command: $cmd"

#exec python $CARMUSR/lib/python/salary/account/f0.py $cmd --daemon
exec python $CARMUSR/lib/python/interfaces/tpms.py $cmd --daemon

echo "Script finished"
echo "[$(date)]"

