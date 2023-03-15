#!/bin/sh
# Script started by sysmond and used to wait for all accumulation to be completed.
# When the cleanup is done, nighlty cleanup and truncate is done.

echo "accumulate_and_cleanup.sh" > logfile 

# Sets CARMUSR if not set
if [ -z "$CARMUSR" ]; then
    a=`pwd`
    cd `dirname $0`/..
    CARMUSR=`pwd`
    export CARMUSR
    cd $a
fi

logfile="$CARMTMP/logfiles/accumulate_and_clean.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"

echo "[$(date)] Starting script accumulate_and_cleanup.sh" > $logfile 

(echo "[$(date)] Accumulate" >> $logfile
${CARMUSR}/bin/accumulators/accumulator.sh
echo "[$(date)] Accumulate done" >> $logfile ) &

wait

#Manpower jobs removed from chain. They run separately.
#${CARMUSR}/bin/manpower/accumulate_cmp.sh -t C &
#${CARMUSR}/bin/manpower/accumulate_cmp.sh -t F &

(echo "[$(date)] Truncate archiving tables" >> $logfile
${CARMUSR}/bin/db/truncate_schema_archiving.sh 
echo "[$(date)] Truncate archiving tables done" >> $logfile ) &

wait

(echo "[$(date)] Cleanup archiving tables" >> $logfile
${CARMUSR}/bin/db/cleanup_schema_archiving.sh
echo "[$(date)] Claneup archibing tables done" >> $logfile) &

wait

echo "[$(date)] Nightly cleanup" >> $logfile
${CARMUSR}/bin/db/nightly_cleanups.sh
echo "[$(date)] Nightly cleanup done" >> $logfile

wait 

echo "[$(date)] Truncate schema regular" >> $logfile
${CARMUSR}/bin/db/truncate_schema_regular.sh 
echo "[$(date)] Truncate schema regular done" >> $logfile

wait

echo "[$(date)] Cleanup schema regular" >> $logfile
${CARMUSR}/bin/db/cleanup_schema_regular.sh  
echo "[$(date)] Claneup schema regular done" >> $logfile

echo "[$(date)] Schema stats" >> $logfile
${CARMUSR}/bin/cmsshell db schemastats | tee -a ${CARMTMP}/logfiles/cmd_gather_schema_stats.log
echo "[$(date)] Schema stats done" >> $logfile


echo "[$(date)] Script finished" >> $logfile

