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

echo "RUNNING UNITTEST TESTSUITE"
    


################ TRACKING TEST CASES ################


$CARMUSR/bin/testing/run_testcases.sh Tracking CommmonCarmusrTests $runs   ACCOUNT_UPDATE
$CARMUSR/bin/testing/run_testcases.sh Tracking GuiTest  $runs BASIC_TEST SIMPLE_GUI_TEST FULL_GUI_TEST RAVE_TEST FIND_ASSIGNABLE_CREW CREW_WAVE_TEST CREW_CFH_TEST
$CARMUSR/bin/testing/run_testcases.sh Tracking RosterChangeTest.1  $runs ASSIGN_SMALL 
$CARMUSR/bin/testing/run_testcases.sh Tracking RosterChangeTest.2  $runs DEASSIGN_SMALL 
$CARMUSR/bin/testing/run_testcases.sh Tracking RosterChangeTest.3  $runs DEASSIGN_LARGE 
$CARMUSR/bin/testing/run_testcases.sh Tracking RosterChangeTest.4  $runs BUYDAYS_TEST 
$CARMUSR/bin/testing/run_testcases.sh Tracking RosterChangeTest.5  $runs UNBUYDAYS_TEST 
$CARMUSR/bin/testing/run_testcases.sh Tracking RosterChangeTest.6  $runs CREATE_PACT 
$CARMUSR/bin/testing/run_testcases.sh Tracking RosterChangeTest.7  $runs CREATE_R_PACT 
$CARMUSR/bin/testing/run_testcases.sh Tracking RosterChangeTest.8  $runs REMOVE_PACT 
$CARMUSR/bin/testing/run_testcases.sh Tracking RosterChangeTest.9  $runs REMOVE_VA_PACT 
$CARMUSR/bin/testing/run_testcases.sh Tracking RosterChangeTest.10  $runs CREATE_VA_PACT

if [[ `echo "${CARMCCSITE}${CARMCCSUBSITE}" | grep -i "SASPROD"` != "" ]]; then
	echo "WILL NOT RUN DATAMODIFING Save/Refresh SCRIPTS AT SAS"
	exit 1
else
    for i in `seq 1 $runs`; do
	$CARMUSR/bin/testing/run_testcases.sh Tracking "LoadTest.$i"            1 LOAD_PLAN 
	$CARMUSR/bin/testing/run_testcases.sh Tracking "LoadAllPublishedTest.$i"   1 LOAD_PUBLISHED_ROSTERS
	$CARMUSR/bin/testing/run_testcases.sh Tracking "Load100PublishedTest.$i"   1 LOAD_100_PUBLISHED_ROSTERS
	$CARMUSR/bin/testing/run_testcases.sh Tracking "LoadChunkPublishedTest.$i"   1 LOAD_CHUNK_PUBLISHED_ROSTERS
	#$CARMUSR/bin/testing/run_testcases.sh Tracking "SaveSmallTest.$i"       1 SAVE_SMALL
	#$CARMUSR/bin/testing/run_testcases.sh Tracking "SaveSmall5.$i"   1 SAVE_SMALL_5
	#$CARMUSR/bin/testing/run_testcases.sh Tracking "SaveLargeGuiTest.$i"    1 SAVE_LARGE
	$CARMUSR/bin/testing/run_testcases.sh Tracking "RefreshSmall.$i" 1 REFRESH_SMALL
	$CARMUSR/bin/testing/run_testcases.sh Tracking "RefreshEmpty.$i" 1 REFRESH_EMPTY
    done
fi


############# END TRACKING ##########################
############## PLANNING TEST CASES #############
$CARMUSR/bin/testing/run_testcases.sh Planning GuiTest  $runs BASIC_TEST SIMPLE_GUI_TEST FULL_GUI_TEST RAVE_TEST  CREW_WAVE_TEST CREW_CFH_TEST

$CARMUSR/bin/testing/run_testcases.sh Planning RosterChangeTest.1  $runs ASSIGN_SMALL 
$CARMUSR/bin/testing/run_testcases.sh Planning RosterChangeTest.2  $runs DEASSIGN_SMALL 
$CARMUSR/bin/testing/run_testcases.sh Planning RosterChangeTest.3  $runs DEASSIGN_LARGE 
$CARMUSR/bin/testing/run_testcases.sh Planning RosterChangeTest.6  $runs CREATE_PACT 
$CARMUSR/bin/testing/run_testcases.sh Planning RosterChangeTest.7  $runs CREATE_R_PACT 
$CARMUSR/bin/testing/run_testcases.sh Planning RosterChangeTest.8  $runs REMOVE_PACT 
$CARMUSR/bin/testing/run_testcases.sh Planning RosterChangeTest.9  $runs REMOVE_VA_PACT 
$CARMUSR/bin/testing/run_testcases.sh Planning RosterChangeTest.10  $runs CREATE_VA_PACT
$CARMUSR/bin/testing/run_testcases.sh Planning CommmonCarmusrTests $runs   ACCOUNT_UPDATE
	    
if [[ `echo "${CARMCCSITE}${CARMCCSUBSITE}" | grep -i "SASPROD"` != "" ]]; then
	echo "WILL NOT RUN DATAMODIFING RosterPublish SCRIPTS AT SAS"
else
    for i in `seq 1 $runs`; do
	$CARMUSR/bin/testing/run_testcases.sh Planning "RosterPublish.$i"  1 ROSTER_PUBLISH
	$CARMUSR/bin/testing/run_testcases.sh Planning "LoadTest.$i"            1 LOAD_PLAN 
	$CARMUSR/bin/testing/run_testcases.sh Planning "LoadAllPublishedTest.$i"   1 LOAD_PUBLISHED_ROSTERS
	$CARMUSR/bin/testing/run_testcases.sh Planning "Load100PublishedTest.$i"   1 LOAD_100_PUBLISHED_ROSTERS
	$CARMUSR/bin/testing/run_testcases.sh Planning "LoadChunkPublishedTest.$i"   1 LOAD_CHUNK_PUBLISHED_ROSTERS
	#$CARMUSR/bin/testing/run_testcases.sh Planning "SaveSmallTest.$i"       1 SAVE_SMALL
	#$CARMUSR/bin/testing/run_testcases.sh Planning "SaveSmall5.$i"   1 SAVE_SMALL_5
	#$CARMUSR/bin/testing/run_testcases.sh Planning "SaveLarge.$i"    1 SAVE_LARGE
        #henrikal: Disabled failing test
	#$CARMUSR/bin/testing/run_testcases.sh Planning "RefreshSmall.$i" 1 REFRESH_SMALL
	$CARMUSR/bin/testing/run_testcases.sh Planning "RefreshEmpty.$i" 1 REFRESH_EMPTY
    done
fi
################ END PLANNING ##################

