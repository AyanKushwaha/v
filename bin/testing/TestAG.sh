#!/bin/bash
# TestAG.sh
# Provides the time the Alert Generator takes to complete a full cycle

usage_text () {
  echo "Usage: `basename $0` <time_to_run_AG_minutes> <test_case>"
}

usage () { usage_text; exit 0; }

stopServers()
{
  echo "Caught termination signal, please wait... stopping servers."
  bin/desmond.sh stop
  echo "Please verify if the server processes are still running:"
  echo "bin/desmond.sh status"
  echo "If the server processes are running stop them:"
  echo -e "bin/desmond.sh stop\n"
  exit 1
}

printStats()
{
  ag_name=$1

  logfile=$CARMTMP/logfiles/alertgenerator.$ag_name.$USER.$HOSTNAME

  #Memory consumption
  rss=`ps -u $USER -o "rss command" | grep $logfile | grep "batch" | cut -d" " -f1`
  vsz=`ps -u $USER -o "vsz command" | grep $logfile | grep "batch" | cut -d" " -f1`
  if [ $rss ] && [ $vsz ]; then
    rssMb=$(($rss/1024))
    vszMb=$(($vsz/1024))
  else
    rssMb=0
    vszMb=0
  fi

  times_to_use=`grep sp_crew $logfile | tail -2 | cut -d " " -f 5`

  # count the number of results
  n=0
  for t in $times_to_use; do
    let n=n+1
  done

  sum=0
  # check if there are at least 2 results
  if [ $n -eq 2 ]; then
    for t in $times_to_use; do
      hrs=`echo $t|cut -d ":" -f1`
      hrs=${hrs##0}
      mins=`echo $t|cut -d ":" -f2`
      mins=${mins##0}
      secs=`echo $t|cut -d ":" -f3`
      secs=${secs##0}
      sum=$(($hrs*60*60+$mins*60+$secs-$sum))
    done
  fi

  echo "PERFTEST logfile:$logfile"

  if [ $sum -ne 0 ]; then
    echo "PERFTEST === macro $testcase $ag_name DONE Real: $sum.000 s  cpu: $sum.000 s (pre.macro = '$sleep_minutes')=======mem SYS: $vszMb m, mem RSS: $rssMb m==========="
  fi
}

if [ $# -lt 2 ]
then
  usage
fi

testcase=$2

# Sets CARMUSR if not set
if [ -z "$CARMUSR" ]; then
  a=`pwd`
  cd `dirname $0`/../..
  CARMUSR=`pwd`
  export CARMUSR
  cd $a
fi
. $CARMUSR/etc/carmenv.sh

SERVER_MODE=1
PRODUCT=CctServer
APPLICATION=AlertGenerator
export SERVER_MODE PRODUCT APPLICATION

if [ $testcase == "SKCMS_AG_loop" ]; then
  sleep_minutes=$1
  trap stopServers SIGINT SIGKILL SIGTERM
  echo "PERFTEST === Starting test $sleep_minutes / $testcase `date` "
  bin/desmond.sh start

  echo "Running the Alert Generator during $sleep_minutes minutes"
  sleep $(($sleep_minutes*60))
  echo "PERFTEST $sleep_minutes / $testcase COMPLETE"

  printStats "SAS_ALERT_1"
  printStats "SAS_ALERT_2"
  printStats "SAS_ALERT_3"

  bin/desmond.sh stop
else
  HOSTNAME=$1
  printStats "SAS_ALERT_1"
  printStats "SAS_ALERT_2"
  printStats "SAS_ALERT_3" 
fi

echo "PERFTEST ========================================= `date` "
