#!/bin/sh
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/installBids.sh,v 1.3 2009/08/19 13:01:41 adg347 Exp $ 
# 
# Command to install a new default bid file
# 

usageText() {
  echo "Script to install a new default bid file"
  echo "Usage: "`basename $0`" bidfile period" 
  echo "  bidfile     : required argument specifying which bid file to install"
  echo "  period      : required argument specifying which bid period to use,"
  echo "              : specified as the first date of the period."
  echo "              : Example: '01May2007'"
  echo "  -h          : help"
}

# Read options
while getopts h option
do
    case "$option" in
        h) usageText
             exit 0 ;;
    esac
done

bids=$1
period=$2

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

SK_APP=Planning
export SK_APP

# Unset CARMTMP and CARMSYS. This needs to be done if started by Desmond
# since we then need to switch environment from Tracking to Planning
unset CARMSYS
unset CARMTMP

# Sets CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
. $CARMUSR/bin/carmenv.sh

LOG_ID=$SK_APP

timestamp=`date '+%Y%m%d.%H%M.%S'`

# Start studio with -d for (daemon) virtual display
SK_ARG="-d -p PythonEvalExpr(\"carmusr.rostering.Bids.installBids('$bids','$period')\")"
  echo "`date +'%Y%m%d %H:%M:%S'` INFO: Running $CARMSYS/bin/studio $SK_ARG"
$CARMSYS/bin/studio $SK_ARG | /usr/bin/tee $CARMTMP/logfiles/studio.$LOG_ID.$USER.$timestamp.$HOSTNAME

