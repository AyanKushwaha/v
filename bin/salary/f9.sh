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



logdir="$CARMTMP/logfiles/salary/account"
[ ! -d $logdir ] && mkdir -p $logdir
logfile="$logdir/f9.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"
#logfile="fakelog.txt"

exec &> >(tee -i $logfile)



echo "[$(date)]"
echo "starting script f9.sh ..."

cmd=$1
echo "    command: $cmd"

#exec python $CARMUSR/lib/python/salary/account/f9.py $cmd --daemon
exec python $CARMUSR/lib/python/salary/account/f9.py $cmd --save --daemon

echo "Script finished"
echo "[$(date)]"

