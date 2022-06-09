#!/bin/sh

export DEBUG_HOST="$2"
export DEBUG_PORT="$3"
export DEBUG_TRACE="$4"

if [ -z "$DEBUG_HOST" ]; then
	export DEBUG_HOST=localhost
fi

if [ -z "$DEBUG_PORT" ]; then
	export DEBUG_PORT=5678
fi

if [ $# -lt 0 ]; then
  echo "Usage: $0 [host port start-in-breakmode]"
  exit 1
fi

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

SK_APP=Manpower
export SK_APP

. $CARMUSR/etc/carmenv.sh

shift
echo "Starting system, directories:"
echo "CARMUSR:   $CARMUSR"
echo "CARMDATA:  $CARMUSR"
echo "CARMSYS:   $CARMSYS"
echo "CARMTMP:   $CARMTMP"
echo ""


$CARMSYS/bin/mirador -s carmensystems.manpower.private.util.EclipseRemoteDebug carmensystems.manpower.private.ManpowerServices $@
