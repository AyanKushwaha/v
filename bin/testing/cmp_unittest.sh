#!/bin/sh

#
# Assume that the start script is located in the carmusr get abolute path
# by assuming that a crc directory exist at the top level
#

if [ "$1" != "-" ]; then
    SCHEMA=${SCHEMA:-$1}
    DATABASE=oracle:$SCHEMA/$SCHEMA@flm/GPD01DEV
    SYSTEM_DB=oracle:carmdba/hemligt@flm/GPD01DEV
    export SCHEMA DATABASE SYSTEM_DB
fi

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
echo "SCHEMA:    $SCHEMA"
echo "DATABASE:  $DATABASE"
echo "SYSTEM_DB: $SYSTEM_DB"
echo ""

$CARMSYS/bin/mirador -s carmensystems.manpower.private.util.TestRunner $@
