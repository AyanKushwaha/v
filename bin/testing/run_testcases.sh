#!/bin/sh
# function to run test
function run_tests()
{
    
    logfile=$CARMTMP/logfiles/TestCase.$1.$HOSTNAME.txt
    
    echo "TESTCASE === Starting test $1  `date`  ==="
    echo "TESTCASE === Logging to $logfile ==="
    rm -rf $logfile 2>/dev/null

    display_param=
    if [ "x$DISPLAY" == "x" ]; then
        display_param=-d
    fi

    $CARMSYS/bin/studio $display_param -w -p "PythonRunFile(\"carmensystems/studio/webserver/InitWebServer.py\")" -l $logfile -p $2
    grep 'TESTCASE' $logfile 2>/dev/null
    echo "TESTCASE === $1 COMPLETE `date` ==="
    
}
# function to change apps
function set_app()
{
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

    unset CARMSYS
    unset CARMTMP
    unset CARMDATA
    SK_APP=$1
    export SK_APP
    . $CARMUSR/bin/carmenv.sh
    if [ -z "$TEST_ENV_SOURCED" ]; then
	. $CARMUSR/bin/testing/test_env.sh
    fi
}



args=$#

if [[ $args -eq 0 ]]; then
    echo "Usage: run_testcases SK_APP logname runs TEST1 TEST2 .."
    exit 1
fi

set_app $1
name=$2
runs=$3
p_arg="PythonRunFile(\"carmtest/Perftest.py\",\"$runs\",\""

tests=($@)

for i in `seq 3 $args`; do
    new=${tests[$i]}
    if [[ -n "$new" ]]; then
	p_arg=$p_arg"|$new"
	echo "ADDED CASE $new"
    fi
done
p_arg=$p_arg"\",\"\")"
echo "BUILT COMMAND STRING : "$p_arg
run_tests $name $p_arg
