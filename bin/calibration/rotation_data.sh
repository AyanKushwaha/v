#!/bin/bash

wherami=`dirname $0`
_CARMUSR=`(cd $wherami/../..; pwd)`

# If CARMUSR not set, use current directory as reference point.
CARMUSR=${CARMUSR-"${_CARMUSR}"}
export CARMUSR

SK_APP=Planning
export SK_APP
echo "loading CMS shell environment ..."
. $CARMUSR/bin/carmenv.sh

logdir="$CARMTMP/logfiles"
[ ! -d $logdir ] && mkdir -p $logdir
logfile="$logdir/calibration_transfer_master_rotation_data.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"
#logfile="fakelog.txt"

exec &> >(tee -i $logfile)

echo "[$(date)]"
echo "Starting script rotation_data.sh with args:" 
echo "$@"

echo "Starting Mirador"

# Example of script usage with arguments:
# $CARMUSR/bin/startMirador.sh --script -s carmusr.calibration.util.data_transfer_from_cms --pmp 350 --hours_to_op $HOURS_TO_OP

$CARMUSR/bin/startMirador.sh --script -s carmusr.calibration.util.data_transfer_from_cms "$@"
echo "Mirador ended."

echo "Script finished"
echo "[$(date)]"
