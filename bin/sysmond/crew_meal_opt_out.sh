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
logfile="$logdir/crew_meal_opt_out.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"

exec &> >(tee -i $logfile)

echo "[$(date)]"
echo "starting script meal_opt_out.sh ..."
echo $CARMUSR
exec python $CARMUSR/lib/python/meal/meal_optout_import_runner.py --daemon --save

echo "Script finished"
echo "[$(date)]"

