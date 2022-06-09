#!/bin/sh

wherami=`dirname $0`
_CARMUSR=`(cd $wherami/../..; pwd)`

echo "[$(date)] Starting script tester.sh"

SK_APP=Tracking
export SK_APP

# If CARMUSR not set, use current directory as reference point.
CARMUSR=${CARMUSR-"${_CARMUSR}"}
export CARMUSR

# Get other environment (CARMSYS, ...)
. $CARMUSR/bin/carmenv.sh

exec python $CARMUSR/lib/python/salary/account/tester.py "$@"

echo "[$(date)] Script finished"

