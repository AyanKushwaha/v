#!/bin/sh
# RunTestCase.sh <premacro> <macro> <posmacro>

usage() {
  echo " Usage:" 
  echo "   command [premacro] [macro] [posmacro]"
  exit 1
}

if [ "x$1" = "x-h" -o "$#" -gt 3 ]; then
  usage
fi
if [ "$#" -eq 0 ]; then
  premacro=""
  macro=""
  posmacro=""
  testcase="LOAD"
fi
if [ "$#" -eq 1 ]; then
  premacro=""
  macro=$1
  posmacro=""
  shift 1 
  testcase=$macro
fi
if [ "$#" -eq 2 ]; then
  premacro=$1
  macro=$2
  posmacro=""
  shift 2
  testcase=$macro
fi
if [ "$#" -eq 3 ]; then
  premacro=$1
  macro=$2
  posmacro=$3
  shift 3
  testcase=$macro
fi

# Ok, we have read the arguments, let's setup the environment

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
SK_APP=Tracking
export SK_APP
#CARMUSINGAM=YES
#export CARMUSINGAM

# Sets CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
. $CARMUSR/etc/carmenv.sh

# Why SERVER MODE? I think we shall skip this?
#SERVER_MODE=1
#export SERVER_MODE


p_arg="PythonRunFile(\"carmtest/Stabtest.py\",\"$premacro\",\"$macro\",\"$posmacro\")"
logfile=$CARMTMP/logfiles/TestCase.$testcase.$HOSTNAME.txt

echo "PERFTEST === Starting test $premacro / $testcase / $posmacro `date` "
display_param=
if [ "x$DISPLAY" == "x" ]; then
    display_param=-d
fi
$CARMSYS/bin/studio $display_param -w -p "PythonRunFile(\"carmensystems/studio/webserver/InitWebServer.py\")" -l $logfile -p $p_arg $*

echo "PERFTEST $premacro / $testcase / $posmacro COMPLETE"
echo "PERFTEST logfile:$logfile"
grep "PERFTEST" $logfile
echo "PERFTEST ========================================= `date` "
