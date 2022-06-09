#!/bin/sh 
                                                                                
curdir=`dirname $0`
#CARMUSR=`cd $curdir|pwd`
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
                                                                                
port=$1
connstr=$2
schema=$3
                                                                                
#echo "Starting system, directories:"
#echo "CARMUSR:   $CARMUSR"
#echo "CARMDATA: `ls -l $CARMUSR/current_carmdata | sed 's/.*->//g'`"
#echo "CARMSYS:  `ls -l $CARMSYS | sed 's/.*->//g'`"
#echo "CARMTMP:   $CARMTMP"
#echo "SITE:      $SITE"
                                                                                
$CARMSYS/bin/carmrunner java -jar $CARMSYS/lib/classes/tableeditor-all.jar -c "$connstr" -s $schema -d "http://localhost:$port/RPC2"
#$CARMSYS/bin/carmrunner java -jar $CARMSYS/lib/classes/tableeditor-all.jar -c "$DATABASE" -s $schema -d "http://localhost:$port/RPC2"
#$CARMSYS/bin/carmrunner java -jar $CARMSYS/lib/classes/tableeditor-all.jar -c "oracle:ara_sk_all_6mths/ara_sk_all_6mths@flm/flm1010"  -s $schema -d "http://localhost:$port/RPC2"
