#!/bin/sh
USAGE="Run \n>accumulateBaseline.sh new_date [recalc] [daily]\n to move baseline to new_date.\n 
       If recalc is given baseline will be recalculated to new_date and possibly\n
       conflicting baseline is removed!\n
       If daily option is given, daily baseline is moved if needed and also recalculated"
if [ $# -eq 0 ]; then
    echo -e $USAGE
    exit 1
fi

DATE=$1
RECALC=$2
MODE=$3

if [[ `echo "$MODE" | grep -i 'daily'` != "" ]]; then
    DATE=`date +%d%b%Y`
    RECALC="RECALC"
fi

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


SK_APP=Server
export SK_APP
echo SK_APP:: $SK_APP



. $CARMUSR/bin/carmenv.sh

$CARMSYS/bin/mirador -s carmusr.AccumulateBaseLine main $DATE $RECALC $MODE
