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

echo "RUNNING UNITTEST LOAD TESTSUITE"


################ TRACKING TEST CASES ################

for i in `seq 1 $runs`; do
    $CARMUSR/bin/testing/run_testcases.sh Tracking  "LoadTests.Tracking.$i" 1  LOAD_PLAN
    $CARMUSR/bin/testing/run_testcases.sh Tracking  "LoadPublishedRostersTests.$i"  1  LOAD_PUBLISHED_ROSTERS
    $CARMUSR/bin/testing/run_testcases.sh Tracking "Load100kPublishedTest.$i"   1 LOAD_100_PUBLISHED_ROSTERS
    $CARMUSR/bin/testing/run_testcases.sh Tracking "LoadChunkPublishedTest.$i"   1 LOAD_CHUNK_PUBLISHED_ROSTERS
done
############# END TRACKING ##########################
################ PLANNING TEST CASES ################
for i in `seq 1 $runs`; do
    $CARMUSR/bin/testing/run_testcases.sh Planning  "LoadTests.Planning.$i" 1  LOAD_PLAN
    $CARMUSR/bin/testing/run_testcases.sh Planning "Load100kPublishedTest.$i"   1 LOAD_100_PUBLISHED_ROSTERS
    $CARMUSR/bin/testing/run_testcases.sh Planning "LoadChunkPublishedTest.$i"   1 LOAD_CHUNK_PUBLISHED_ROSTERS
done

############# END PLANNING ##########################

