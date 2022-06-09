#!/bin/sh

_PLAN_MONTH="MAY2012"

usage_text() {
    echo "Usage: `basename $0` [-p <cond> ...] <tests...>"
    echo "       `basename $0` [-s <t|p|r>] [-p <cond> ...] [-P <monYYYY>] [-c <connstr>]"
    echo "          [-f] -l [category]"
    echo "   Commands are:"
    echo "      -l [category]"
    echo "         List test categories, or if a category is specified, lists"
    echo "         tests in the specified category"
    echo "   Options are:"
    echo "      -f"
    echo "         Lists details"
    echo "      -n"
    echo "         Skip load plan (only a subset of tests available)"
    echo "      -p <cond>"
    echo "         Only tests matching precondition"
    echo "      -s <t|p|r>"
    echo "         Run test(s) in Studio:"
    echo "         t: Tracking Studio"
    echo "         p: Planning Studio"
    echo "         r: ReportWorker Studio"
    echo "      -P <monYYYY>"
    echo "         Open specific plan month (default is $_PLAN_MONTH)"
    exit 1
}

_ME=$0
_CMD="default"
_CMDARG=""
_DETAILS=""
_PRECONDS="-p"
_SKIPMEAS=False
_SKIPLOAD=False
_STARTSTUDIO=
PYTHON=`which python`

DEBUG_SCRIPT=1

while getopts fnlmp:s:P:T: option; do
    case "$option" in
        l) _CMD="list" ;;
	m) _SKIPMEAS=True ;;
        n) _SKIPLOAD=True ;;
        f) _DETAILS="_full" ;;
        p) _PRECONDS="$_PRECONDS $OPTARG" ;;
	T) _CMD="testrpc"
       _CMDARG=$OPTARG ;;
    s) _STARTSTUDIO=$OPTARG ;;
    *) usage_text ;;
        
    esac
done

shift `expr $OPTIND - 1`

exec_python() {
  PYTHONPATH=$CARMUSR/lib/python:$CARMUSR/lib/python/carmtest/framework:$PYTHONPATH
  _DEBUG=""
  if [ $DEBUG_SCRIPT ]; then
    _DEBUG="import traceback; traceback.print_exc()"
  fi
  SCRIPTFILE=`mktemp -u /tmp/XXXXXXXX`.py
  cat > $SCRIPTFILE << EOF
import sys
try:
  import carmtest.framework.TestFunctions as TestFunctions 
except:
  print >>sys.stderr, "$_ME: Unable to run Python counterpart"
  $_DEBUG
  sys.exit(-1)
try:
  TestFunctions.run_cmdline("$*")
except:
  print >>sys.stderr, "$_ME (from Python):", str(sys.exc_info()[1])
  $_DEBUG
  sys.exit(-1)
EOF
  #echo $SCRIPTFILE contains
  #cat $SCRIPTFILE
  $PYTHON $SCRIPTFILE || exit 1
  rm $SCRIPTFILE
}

start_rpc_studio() {
  $CARMUSR/bin/startStudio.sh -S $_STARTSTUDIO
}

exec_rpc_testcase() {
  $PYTHON -c "`cat <<EOF
print \"$2\"
from xmlrpclib import ServerProxy
P = ServerProxy('$1')

print P.RaveServer.evalPython('__import__(\"carmtest.framework.TestFunctions\").framework.TestFunctions.run(\"$2\",skipMeasurements=$_SKIPMEAS)')
EOF`" || exit 1
}

if [ $_CMD == "list" ]; then
  if [ "x$1" == "x" ]; then
    exec_python list_categories$_DETAILS $_PRECONDS
  else
    exec_python list_tests$_DETAILS $1 $_PRECONDS
  fi
  exit 0
fi
if [ $_CMD == "default" ]; then
  if [ $_STARTSTUDIO ]; then
    usage_text
  fi
  if [ "x$1" == "x" ]; then
    usage_text
  else
    export CARMTEST_LOG_DIR=$CARMTMP/logfiles/unittest
    mkdir -p $CARMTEST_LOG_DIR
    echo Carmpython is $PYTHON
    exec_python run_test $1 $_PRECONDS
  fi
  exit 0
fi
if [ $_CMD == "testrpc" ]; then
  exec_rpc_testcase "http://campos:6718" $_CMDARG
fi
