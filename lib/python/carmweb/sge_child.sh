#!/bin/sh
#
# sge_child.sh
#

if [ -z $CARMUSR ]; then
    echo "CARMUSR variable not set"
    exit 1
fi

if [ -z "$LOGDIR" ]; then
    LOGDIR=/tmp
fi
exec >> $HOME/sgestartup.$HOST.log

export TWS_LOGDIR=$LOGDIR

if [ -z "$JOB_ID" ]; then
    echo "Must be run from SGE"
    exit 1
fi
if [ -z "$COMMAND" ]; then
    echo "Command not specified"
    exit 1
fi
if [ -z "$PROCESS_TYPE" ]; then
    echo "Process type not specified"
    exit 1
fi
if [ -z "$CALLBACK_URI" ]; then
    echo "Callback not specified"
    exit 1
fi

archive_logfile() {
	CHLOGDIR=$LOGDIR/$1/$USER/$PROCESS_TYPE/`date +%Y%m%d`/
	mkdir -p $CHLOGDIR
	mv $_LOGFILE $CHLOGDIR
}
archive_logfile_term() {
    echo "Job was terminated by SGE"  >> $_LOGFILE
    archive_logfile "terminated"
	exit 0
}

mkdir -p $LOGDIR

LAUNCHT=`date +%Y%m%d.%H%M`
_LOGFILE=$LOGDIR/$PROCESS_TYPE.$HOST.$LAUNCHT.$JOB_ID.log
echo "Here! $_LOGFILE"
exec > $_LOGFILE
trap archive_logfile_term INT TERM HUP ABRT QUIT STOP
echo "=== BEGIN $PROCESS_TYPE (pid: $$, host: $HOST) ==="
env
qalter $JOB_ID -ac tws_logfile="$_LOGFILE",tws_status=STARTUP,tws_host=$HOST > /dev/null || true
echo ">$COMMAND"
eval $COMMAND 2>&1
echo "=== END $0 (exit status: $?) ==="
archive_logfile "finished"
