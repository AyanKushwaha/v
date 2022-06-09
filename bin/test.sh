#!/bin/sh
#
# Starts Studio in batch mode to run Nosetest.
#
# The framework is based on simple tests written in python
# https://nose.readthedocs.org/en/latest/
#
# Each single test is responsible for setting studio in the state needed for
# testing. Each test is also responsible to leave studio  in a "untouched"
# state.
#
# author: Joakim Moller, Jeppesen 2015-05-08

application=$1
testmodule=$2

# Set the system variables.
case $application in
    planning)
    export CARMUSR=`pwd`
    export CARMDATA=$CARMUSR/current_carmdata
    export CARMSYS=$CARMUSR/current_carmsys_cas
    export CARMTMP=$CARMUSR/current_carmtmp_cas
    export SK_APP=Planning
    export CARM_PROCESS_NAME=PlanningStudio
    ;;
    tracking)
    export CARMUSR=`pwd`
    export CARMDATA=$CARMUSR/current_carmdata
    export CARMSYS=$CARMUSR/current_carmsys_cct
    export CARMTMP=$CARMUSR/current_carmtmp_cct
    export SK_APP=Tracking
    export CARM_PROCESS_NAME=TrackingStudio
    ;;
esac    

# Redirections of stdout and stdin to filter output from studio
exec 6>&1
exec 7>&2
exec 1> stdout.txt
exec 2> stderr.txt

# Start studio and launch the test driver script.
SK_ARG="-d -p PythonRunFile(\"$CARMUSR/devtools/lib/test/test.py\",\"$application\",\"$testmodule\")"
$CARMSYS/bin/studio $SK_ARG
exit_status=$?

# Restore redirections
exec 1>&6 
exec 6>&-
exec 2>&7
exec 2>&-

# Exit with the exit status from the tests. If any tests fail the exit status
# will be nonezero
exit $exit_status
