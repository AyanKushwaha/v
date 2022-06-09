#!/bin/sh
# Script started by sysmond 
#

echo "accumulator_update_baseline.sh" > logfile 

# Sets CARMUSR if not set
if [ -z "$CARMUSR" ]; then
    a=`pwd`
    cd `dirname $0`/..
    CARMUSR=`pwd`
    export CARMUSR
    cd $a
fi

logfile="$CARMTMP/logfiles/accumulator_update_baseline.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"

# The baseline should be set to 10 days earlier than execution time
# to ensure that enough data is loaded for the period which Studio is
# opened for.
today=`date '+%d%b%Y' -d '10 days ago'`

echo "[$(date)] Starting script accumulator_update_baseline.sh" > $logfile 

echo "[$(date)] Update baseline to $today" >> $logfile

${CARMUSR}/bin/accumulators/accumulateBaseline.sh "$today" RECALC SHORT >> $logfile

wait
echo "[$(date)] Update baseline done" >> $logfile

echo "[$(date)] Script finished" >> $logfile
