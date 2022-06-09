#!/bin/sh
# Start batch jobs accounts reset

wherami=`dirname $0`
_CARMUSR=`(cd $wherami/../..; pwd)`


error ( ) {
    echo "$*" 2>&1
    exit 2
}

usage ( ) {
    echo "Usage: $0 entitlement" 2>&1
    echo "   " 2>&1
    echo "       $0 correction" 2>&1
    echo "   " 2>&1
    echo "Where:" 2>&1
    echo "   entitlement" 2>&1
    echo "      Adds entitled F36 days for CC in upcoming year." 2>&1
    echo "   correction" 2>&1
    echo "      Add corrections to entitled F36 days and reductions on roster." 2>&1
    exit 1
}

command=
case $1 in
 entitlement)
   command=entitlement ;;
 correction)
   command=correction ;;
 *)
   usage ;;
esac
shift 1


echo "[$(date)] Starting script f36_account.sh"

SK_APP=Tracking
export SK_APP

# If CARMUSR not set, use current directory as reference point.
CARMUSR=${CARMUSR-"${_CARMUSR}"}
export CARMUSR

# Get other environment (CARMSYS, ...)
. $CARMUSR/bin/carmenv.sh

exec python $CARMUSR/lib/python/adhoc/f36_account.py $command

echo "[$(date)] Script finished"

