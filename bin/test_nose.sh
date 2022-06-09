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

# Set the CARMDATA, CARMSYS, CARMDATA, CARMTMP and CARMSYSTEMROOT variables. In
# OTS-products this is done by "print_sys_def.py"
script_dir=`dirname $0`
eval `$script_dir/print_sys_def.py -s`


# Redirections of stdout and stdin to filter output from studio
# Cannot redirect if run from 'behave'
if [ "$1" = "-r" ]; then 
    exec 6>&1
    exec 7>&2
    exec 1> stdout.txt
    exec 2> stderr.txt
fi;

# Start studio and launch the test driver script.
$CARMSYS/bin/studio \
    -d -pPythonRunFile'("$CARMSYSTEMROOT/nose_tests/test.py")'
exit_status=$?

# Restore redirections
if [ "$1" = "-r" ]; then 
    exec 1>&6
    exec 6>&-
    exec 2>&7
    exec 2>&-
fi;

# Exit with the exit status from the tests. If any tests fail the exit status
# will be nonezero
exit $exit_status