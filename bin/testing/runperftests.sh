#!/bin/sh
#
# Script to run Test suite
#
# Default number of test runs for each test including (first not used for auto tests)
no_of_auto_runs=1
no_of_manual_runs=1


usage_text () {
  echo "This file is depricated, please try to make it work using the python frame work"
  echo "Usage: `basename $0` <test>"
  echo "Run selected test: all, load, gui, db, save, refresh, alert, ravekpi, sas"
}

usage () { usage_text; exit 0; }



fatal () { echo $1; usage_text; exit $2; }

run_test () {
   # Run the test
   echo "********************** TEST START ****************************"
   echo "*** Running: $test_cmd $@   -   `date`"
   a=$1
   [ $a = N2201b ] && a=
   b=$2
   [ $b = N2201b ] && b=
   c=$3
   [ $c = none ] && c=
   $test_cmd "$a" "$b" "$c"
   echo "*** Finished: $test_cmd $@   -   `date`"
}

run_test_ag () {
   # Run the Alert Generator test
   echo "Result of run no 1: ********************** TEST START ****************************"
   echo "*** Running: $test_cmd_ag $@   -   `date`"
   $test_cmd_ag $1 $2 > $result_dir/ptest
   echo "*** Finished: $test_cmd_ag $@   -   `date`"
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
      echo "Running $test_cmd $premacro $macro $posmacro `expr $runs_to_do + 1` times, discarding first run..."
      # First run, result discarded since it is less natural
   
      run_test $premacro $macro $posmacro > /dev/null 2>&1

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

auto_run_ag () {
   # $1 = Time to run the AG in minutes
   # $2 = Macro
   sleep_minutes=$1
   macro=${2:-""}

   (
      # An empty row is nice...
      echo ""
      echo "Running $test_cmd_ag ${macro} 1 time..."

      # Alert Generator Test only runs once
      run_test_ag $sleep_minutes $macro
      _newres=`head -3 $result_dir/ptest`
      echo "$_newres" 

      for i in `seq 1 3`;
	do
        _resi=`grep "DONE" $result_dir/ptest | head -$i | tail -1`
        _testname=`echo $_resi | cut -d " " -f 5`
        _cpures=`echo $_resi | cut -d " " -f 11`
        _realres=`echo $_resi | cut -d " " -f 8`
        _sysres=`echo $_resi | cut -d " " -f 17`
        _rssres=`echo $_resi | cut -d " " -f 21`
        echo "" 
        echo "" 
        echo "********** And the results for ${macro}_${_testname} are..." 
        echo "CPU times  : $_cpures " 
        echo "Real times : $_realres " 
        echo "SYS memory : $_sysres " 
        echo "RSS memory : $_rssres " 
        echo "CPU time, on average   : 0" 
        echo "Real time, on average  : 0" 
        echo "SYS memory, on average : 0" 
        echo "RSS memory, on average : 0" 
      done
      echo "" 
   ) | tee -a $result_file
   rm $result_dir/ptest
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

CARM_PERF_TEST='YES'
export CARM_PERF_TEST

result_dir="${CARMTMP}/logfiles"
file_ts=`date '+%Y%m%d.%H%M.%S'`
result_file=${result_dir}/nf_testresults.`hostname`.${file_ts}.log
calc_file=${result_dir}/nf_figures.`hostname`.${file_ts}.log
test_cmd=`dirname $0`/TestMacro.sh
test_cmd_ag=`dirname $0`/TestAG.sh

if [ $# -lt 1 ]
then
  usage
fi

test_set="$*"

trap 'exit 1' 0 1 2 3 11 15

# Start test suite run
touch ${result_file}
echo "Logging to ${result_file}"

# Running correct testsuite for usr
if [[ $test_set == *"all"* ]] || [[ $test_set == *"db"* ]] || [[ $test_set == *"load"* ]]; then
  auto_run N2201b N2201b none
  auto_run PYTHON_TESTCASE N2201c.LoadPublishedRosters LOAD_PUBLISHED_ROSTERS
fi

if [[ $test_set == *"all"* ]] || [[ $test_set == *"gui"* ]]; then
  auto_run 50RowsShowAllAndClear N2219.ShowRosters none
  auto_run 50RowsRudobsOffShowAllAndClear N2219b.ShowRosters none
  auto_run 50RowsShowAllAndClearShowRosters N2221.Scroll50Rows none
  auto_run 50RowsShowAllAndClear N2222.ShowTrips none
  auto_run 50RowsShowAllAndClear N2223.ShowRotations none
  auto_run 50RowsShowAllAndClear N2224.MarkAll none
  auto_run 50RowsShowAllAndClear N2225.SelectCrewCommandLine.25000 none
  auto_run 50RowsShowAllAndClear N2226.SelectCrewFromForm.25000 none
  auto_run 50RowsShowAllAndClear N2227.SelectStandbysCommandLine none
  auto_run 50RowsShowAllAndClear N2228.SelectStandbysMiniSelection none
  auto_run 50RowsShowAllAndClear N2229.ShowIllegalCrew none
  auto_run 50RowsShowAllAndClear N2230.MarkTouchAirportLegs.BKK none
  auto_run 50RowsShowAllAndClear N2231.SelectTaskCode.VA none
  auto_run PYTHON_TESTCASE N2232.AssignTripToCrew ASSIGN_SMALL
  auto_run PYTHON_TESTCASE N2233.DeassignTripFromCrew DEASSIGN_SMALL
  auto_run PYTHON_TESTCASE FindAssignableCrew FIND_ASSIGNABLE_CREW
fi

if [[ $test_set == *"all"* ]] || [[ $test_set == *"db"* ]] || [[ $test_set == *"save"* ]]; then
  auto_run PYTHON_TESTCASE  N2215.SaveSmallChange SAVE_SMALL
  auto_run PYTHON_TESTCASE  N2216.SaveLargeChange SAVE_LARGE
fi

if [[ $test_set == *"all"* ]] || [[ $test_set == *"db"* ]] || [[ $test_set == *"refresh"* ]]; then
  auto_run PYTHON_TESTCASE  N2217.RefreshSmallChange REFRESH_SMALL
  auto_run PYTHON_TESTCASE  N2217.RefreshSmallChange REFRESH_EMPTY
fi

if [[ $test_set == *"all"* ]] || [[ $test_set == *"alert"* ]]; then
  auto_run_ag 20 SKCMS_AG_loop
fi

if [[ $test_set == *"all"* ]] || [[ $test_set == *"ravekpi"* ]]; then
  auto_run 50RowsShowAllAndClear RaveKPI.RuleFailures none
  auto_run 50RowsShowAllAndClear RaveKPI.Rules none
  auto_run 50RowsShowAllAndClear RaveKPI.Levels none
  auto_run 50RowsShowAllAndClear RaveKPI.Colors none
  auto_run 50RowsShowAllAndClear RaveKPI.Rudobs none
fi

if [[ $test_set == *"sas"* ]]; then
  auto_run_ag sulaco SKCMS_AG_SAS_loop
  auto_run 50RowsShowAllAndClearSavePreSAS N2215.SaveSmallChange none
fi
