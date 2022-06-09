#!/bin/sh
# Start script to start Studio in the different modes that are
# available for in the SAS user. 
#

usageText() {
  echo "Script to start a planning studio instance as a batch deamon"
  echo "without a GUI. This will execute a script that exists in adhoc.ScriptRunner"
  echo " Usage:"
  echo " function"

}

function start_studio() {
    # Sets default arguments (used for all studio applications). 
    SK_ARG="-w -p PythonRunFile(\"carmensystems/studio/webserver/InitWebServer.py\")"

    # If nothing else is set, the log will contain the application name
    LOG_ID=$SK_APP

    # Sets default window size. 
    WIN_SIZE=1180x950

    # Put all arguments in quotes and feed them to the python function
    SCRIPT_ARGS="'$1'"
    with_arg=false
    for arg in $@;
    do
      if $with_arg; then
	  SCRIPT_ARGS="$SCRIPT_ARGS,'$arg'"
      fi
      with_arg=true
    done;

    SK_ARG="$SK_ARG -d -p PythonEvalExpr(\"adhoc.ScriptRunner.run_script($SCRIPT_ARGS)\")"
    echo $SK_ARG
    
    timestamp=`date '+%Y%m%d.%H%M.%S'`
    LOGDIR=$CARMTMP/logfiles
    [ -d $LOGDIR ] || mkdir -m a+rwxt $LOGDIR
    LOG_FILE=$LOGDIR/scriptRunner.$LOG_ID.$USER.$timestamp.$HOSTNAME
    export LOG_FILE
    SK_ARG="$SK_ARG -l $LOG_FILE"
    echo     $CARMSYS/bin/studio $SK_ARG
    $CARMSYS/bin/studio $SK_ARG
}

# Sets the CARMUSR variable, if it is not set
if [ -z "$CARMUSR" ]; then
    a=`pwd`
    cd `dirname $0`
    while [ `pwd` != '/' -a ! -d "crc" ]; do
	cd ..
    done
    CARMUSR=`pwd`
    export CARMUSR
    cd $a
fi

echo CARMUSR: $CARMUSR

#
# Get the command line options and take actions
# 

SK_APP="Planning"
export SK_APP

SK_APP_NAME="BatchDeamon"
export SK_APP_NAME

# Set the default editor
CARM_EDITOR=emacs
export CARM_EDITOR

# Sets CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
. $CARMUSR/bin/carmenv.sh

# Must alway pass schema, function, start_p, area_p as arguments (strings)
start_studio $@

