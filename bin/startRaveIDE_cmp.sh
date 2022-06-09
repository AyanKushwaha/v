#!/bin/sh
#
# Script to start a standalone Rave IDE for Manpower
#

# This script is located in the CARMUSR, get absolute path
# Assume that the start script is located in the carmusr get abolute path
# by assuming that a crc directory exist at the top level
#
_origin=`pwd`
cd `dirname $0`
while [ `pwd` != '/' -a ! -d "crc" ]
do
  cd ..
done
CARMUSR=`pwd`
export CARMUSR
cd $_origin

SK_APP=Manpower
export SK_APP

# CARMUSR setup
. ${CARMUSR}/bin/carmenv.sh

LOGFILE=$CARMTMP/logfiles/raveide.$USER.$HOSTNAME

if [ -e $LOGFILE ]; then 
    mv -f $LOGFILE $LOGFILE.old
fi

$CARMSYS/bin/raveide > $LOGFILE 2>&1 &
