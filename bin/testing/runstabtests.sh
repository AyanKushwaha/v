#!/bin/sh
#
# Script to run Test suite
#
# Default number of test runs for each test including (first not used for auto tests)
no_of_pre_runs=0
no_of_auto_runs=1
no_of_manual_runs=1

usage_text () {
    echo "This file is depricated, please try to make it work using the python frame work" 
  echo "Usage: `basename $0`"
}

usage () { usage_text; exit 0; }

fatal () { echo $1; usage_text; exit $2; }

run_test () {
   # Run the test
   echo "********************** TEST START ****************************"
   echo "*** Running: $test_cmd $@   -   `date`"
   a=$1
   [ $a = none ] && a=
   b=$2
   [ $b = none ] && b=
   c=$3
   [ $c = none ] && c=
   $test_cmd "$a" "$b" "$c"
   echo "*** Finished: $test_cmd $@   -   `date`"
}

calc_mean () {

   # Input is a sorted list of values where we discard the lowest and the highest
   # and calculates the mean of the remaining values
   # Still a bit of a hack due to the hardcoded number of tests in thw awk command...
   _no_of_values=`expr $no_of_auto_runs - 1`
   _type=$1
   echo -n "${1}: "
   shift
   #if [ "$#" -eq "$no_of_auto_runs" ]; then
   echo "$@" | tr ' ' '\n' | sort -n | tr '\n' ' ' | awk '{ print ($2+$3+$4)/3 }'
   #else
   #   echo "*** Error ***"
   #fi
}

auto_run () {
   # $1 = Premacro
   # $2 = Macro
   # $3 = Posmacro
   # $4 = No of runs including first, default to $no_of_auto_runs
   premacro=${1:-""}
   macro=${2:-""}
   posmacro=${3:-""}
   runs_to_do=${4:-$no_of_auto_runs}

   (
      # An empty row is nice...
      echo ""
      echo "Running $test_cmd $premacro $macro $posmacro `expr $no_of_pre_runs + $runs_to_do` times, discarding $no_of_pre_runs runs..."
      # Preruns, result discarded since it is less natural
      i=1
      while [ "$i" -le "$no_of_pre_runs" ]; do
         run_test $premacro $macro $posmacro > /dev/null 2>&1
         i=`expr $i + 1`
      done

      # "Normal" runs
      i=1
      _testres=""
      _cpures=""
      _realres=""
      _sysres=""
      _rssres=""
      while [ "$i" -le "$runs_to_do" ]; do
         _res=`run_test "$premacro" "$macro" "$posmacro"`
         _newcpu=`echo "$_res" | sed -n 's/^.*[Cc][Pp][Uu]: \{0,3\}\([0-9\.]*\).s.*$/\1/p'`
         _newreal=`echo "$_res" | sed -n 's/^.*Real: \{0,3\}\([0-9\.]*\).s.*$/\1/p'`
         _newsys=`echo "$_res" | sed -n 's/^.*SYS: \{0,3\}\(-*[0-9]*\).m.*$/\1/p'`
         _newrss=`echo "$_res" | sed -n 's/^.*RSS: \{0,3\}\(-*[0-9]*\).m.*$/\1/p'`
         _newres=`echo "$_res" | sed 's/^.*Real:.\([0-9\.]*\).*s.*[Cc][Pp][Uu]: \{0,3\}\([0-9\.]*\).*s.*SYS:.\(-*[0-9]*\).*m.*RSS:.\(-*[0-9]*\).*m.*$/\2 \1 \3 \4 \n/'`
         # Append new result
         _testres="$_testres $_newres"
         _cpures="$_cpures $_newcpu"
         _realres="$_realres $_newreal"
         _sysres="$_sysres $_newsys"
         _rssres="$_rssres $_newrss"
         echo "Result of run no $i: $_newres" 
         i=`expr $i + 1`
      done
      echo "" 
      echo "" 
      echo "********** And the results for $macro are..." 
#      echo "${_testres}" 
      echo "CPU times  :$_cpures" 
      echo "Real times :$_realres" 
      echo "SYS memory :$_sysres" 
      echo "RSS memory :$_rssres" 
      calc_mean "CPU time, on average   " "$_cpures" 
      calc_mean "Real time, on average  " "$_realres" 
      calc_mean "SYS memory, on average " "$_sysres" 
      calc_mean "RSS memory, on average " "$_rssres" 
      echo "" 
   ) | tee -a $result_file
}

manual_run () {
   # $1 = Premacro
   # $2 = Macro
   # $3 = Posmacro
   # $4 = No of runs including first, default to $no_of_manual_runs
   premacro=${1:-""}
   macro=${2:-""}
   posmacro=${3:-""}
   runs_to_do=${4:-$no_of_manual_runs}
   run_test $premacro $macro $posmacro
}


# Main Function
# Setting environment according to usr
# Sets the CARMUSR variable, if it is not set

usage 
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

# Sets CARMDATA, CARMSYS, CARMTMP and variables
. $CARMUSR/etc/carmenv.sh

result_dir="${CARMTMP}/logfiles"
file_ts=`date '+%Y%m%d.%H%M.%S'`
result_file=${result_dir}/nf_testresults.`hostname`.${file_ts}.log
calc_file=${result_dir}/nf_figures.`hostname`.${file_ts}.log
test_cmd=`dirname $0`/TestStabMacro.sh

if [ $# -lt 0 ]
then
  usage
fi

test_set=$1

trap 'exit 1' 0 1 2 3 11 15

# Start test suite run
touch ${result_file}
echo "Logging to ${result_file}"

# Running correct testsuite for usr

auto_run 50RowsShowAllAndClear N2219.ShowRosters none
