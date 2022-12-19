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



logdir="$CARMTMP/logfiles/empno_update"
[ ! -d $logdir ] && mkdir -p $logdir
logfile="$logdir/empno_update.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"
#logfile="fakelog.txt"

exec &> >(tee -i $logfile)



echo "[$(date)]"
echo "starting script empnoupdate.sh ..."


exec python $CARMUSR/lib/python/empno_update/empno_update_script.py 

echo "Script finished"
echo "[$(date)]"

