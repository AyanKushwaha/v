#!/bin/bash
#
# Script to start mirador

if [ -z "$CARMSYS" ]; then
  . $CARMUSR/bin/carmenv.sh
else
  . $CARMUSR/etc/scripts/shellfunctions.sh
  setCarmvars "$SK_APP"
fi

# Set up a logfile
timestamp=`date '+'%Y%m%d.%H%M.%S`
LOG_FILE=$CARMTMP/logfiles/mirador.$USER.$timestamp.$HOSTNAME
export LOG_FILE

exec $CARMSYS/bin/mirador "$@" >>  $LOG_FILE 2>&1
