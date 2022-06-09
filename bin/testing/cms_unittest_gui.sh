#!/bin/sh

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
# Source test env variables
. $CARMUSR/bin/testing/test_env.sh
runs=$TEST_NR_OF_RUNS

echo "RUNNING UNITTEST GUI TESTSUITE"

################ TRACKING TEST CASES ################
$CARMUSR/bin/testing/run_testcases.sh Tracking CommmonCarmusrTests $runs   ACCOUNT_UPDATE
$CARMUSR/bin/testing/run_testcases.sh Tracking "GuiTest.Tracking"  $runs BASIC_TEST SIMPLE_GUI_TEST FULL_GUI_TEST RAVE_TEST FIND_ASSIGNABLE_CREW CREW_CFH_TEST CREW_WAVE_TEST
$CARMUSR/bin/testing/run_testcases.sh Tracking "RosterChangeTest.Tracking"  $runs ASSIGN_SMALL DEASSIGN_SMALL DEASSIGN_LARGE BUYDAYS_TEST UNBUYDAYS_TEST

############# END TRACKING ##########################
################ PLANNING TEST CASES ################
$CARMUSR/bin/testing/run_testcases.sh Planning CommmonCarmusrTests $runs   ACCOUNT_UPDATE
$CARMUSR/bin/testing/run_testcases.sh Planning "GuiTest.Planning"  $runs BASIC_TEST SIMPLE_GUI_TEST FULL_GUI_TEST RAVE_TEST FIND_ASSIGNABLE_CREW CREW_CFH_TEST CREW_WAVE_TEST
$CARMUSR/bin/testing/run_testcases.sh Planning "RosterChangeTest.Planning"  $runs ASSIGN_SMALL DEASSIGN_SMALL DEASSIGN_LARGE BUYDAYS_TEST UNBUYDAYS_TEST
############# END PLANNING ##########################
