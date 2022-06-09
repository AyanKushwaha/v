#!/bin/sh

#
# Assume that the start script is located in the carmusr get abolute path
# by assuming that a crc directory exist at the top level
#
cd `dirname $0`
while [ `pwd` != '/' -a ! -d "crc" ]
do
  cd ..
done

#
# Set the CARMUSR path.
#
CARMUSR=`pwd`

#
# Should we start Tracking or Manpower Mirador
#
RegisterPythonCode=""
case $1 in
   --manpower)
   RegisterPythonCode=carmensystems.manpower.core.ManpowerServices
   SK_APP=Manpower
   CMP_SERVICE_LOGGING='True'
   OVERRIDE_TABLEMANAGER_SINGLETON=TRUE
   export SK_APP
   export CMP_SERVICE_LOGGING
   export OVERRIDE_TABLEMANAGER_SINGLETON
   shift
   ;;
   --manpower_debug)
   RegisterPythonCode=carmensystems.manpower.core.ManpowerServices
   SK_APP=Manpower
   DEBUG_SUFFIX='_g'
   CMP_SERVICE_LOGGING='True'
   OVERRIDE_TABLEMANAGER_SINGLETON=TRUE
   export DEBUG_SUFFIX
   export SK_APP
   export CMP_SERVICE_LOGGING
   export OVERRIDE_TABLEMANAGER_SINGLETON
   shift
   ;;
   --planning/tracking)
   RegisterPythonCode=miradorRegisterAndLoop
   shift
   ;;
   --tableeditor)
   RegisterPythonCode=miradorRegisterAndLoopTableEditor
   SK_APP=Planning
   export SK_APP
   shift
   ;;
esac

if [ -z "$CARMSYS" ]; then
  . $CARMUSR/bin/carmenv.sh
else
  . $CARMUSR/etc/scripts/shellfunctions.sh
  setCarmvars "$SK_APP"
fi

case "$1" in
    --watchdog|--deamon)
	timestamp=`date '+%Y%m%d.%H%M.%S'`
	LOGDIR=$CARMTMP/logfiles
	[ -d $LOGDIR ] || mkdir -m a+rwxt $LOGDIR
	LOGFILE=$LOGDIR/mirador.$USER.$HOSTNAME.$timestamp
	echo "Starting system, directories:" > $LOGFILE 2>&1
	echo "CARMUSR:   $CARMUSR"  >> $LOGFILE 2>&1
	echo "CARMDATA:  $CARMDATA" >> $LOGFILE 2>&1
	echo "CARMSYS:   $CARMSYS"  >> $LOGFILE  2>&1
	echo "CARMTMP:   $CARMTMP"  >> $LOGFILE  2>&1
	echo ""  >> $LOGFILE  2>&1
	chmod ou+rw $LOGFILE
	;;
    *)
	echo "Starting system, directories:"
	echo "CARMUSR:   $CARMUSR"
	echo "CARMDATA:  $CARMDATA"
	echo "CARMSYS:   $CARMSYS"
	echo "CARMTMP:   $CARMTMP"
	echo ""
	;;
esac

if [ "$1" == "--deamon" ]; then
  setsid $CARMSYS/bin/mirador "$@"  </dev/null >>  $LOGFILE 2>&1 &
elif [ "$1" == "--watchdog" ]; then
  [ -z "$RegisterPythonCode" ] && exec $CARMSYS/bin/mirador "$@"  >> $LOGFILE 2>&1
  exec $CARMSYS/bin/mirador -s $RegisterPythonCode "$@"  >> $LOGFILE 2>&1
elif [ "$1" == "--script" ]; then
  shift
  exec $CARMSYS/bin/mirador "$@"
else
  [ -z "$RegisterPythonCode" ] && exec $CARMSYS/bin/mirador "$@"
  exec $CARMSYS/bin/mirador -s $RegisterPythonCode "$@"
fi

