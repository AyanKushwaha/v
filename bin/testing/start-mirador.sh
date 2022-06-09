#!/bin/sh 
  
if [ -z "$CARMUSR" ] ; then
  echo "error: CARMUSR not set"
  exit 1
fi
 
#CARMUSR=$HOME/work/Customization/sk_cms_user
CARMSYS=$CARMUSR/current_carmsys
CARMDATA=$CARMUSR/current_carmdata
CARMTMP=$CARMUSR/current_carmtmp
#SITE=SAS
BITMODE=32
  
if [ -h $CARMUSR/current_carmtmp ]
then
  CARMTMP=$CARMUSR/current_carmtmp
else
  CARMTMP=$CARMUSR/${USER}_CARMTMP
  mkdir -p $CARMTMP
fi
  
export CARMSYS CARMUSR CARMTMP CARMDATA SITE BITMODE
  
#echo "Starting system, directories:"
#echo "CARMUSR:   $CARMUSR"
#echo "CARMDATA: `ls -l $CARMUSR/current_carmdata | sed 's/.*->//g'`"
#echo "CARMSYS:  `ls -l $CARMSYS | sed 's/.*->//g'`"
#echo "CARMTMP:   $CARMTMP"
#echo "SITE:      $SITE"
  
mkdir -p $CARMTMP/logfiles
  
#echo
#echo "Mirador root pid=$$"
 
$CARMSYS/bin/mirador > $CARMTMP/logfiles/mirador.log 2> $CARMTMP/logfiles/mirador.err &
 
jobs -l | awk '{ print $2 }'
 
