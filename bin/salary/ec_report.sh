#! /usr/bin/bash
# path: bin/salary/ec_report.sh
# to run for specifice period run it with studio environment variables:
##  PERIOD_START=01Dec2020 PERIOD_END=01Jan2021 PLANNING_AREA=ALL RELEASE_RUN=TRUE bin/salary/ec_report.sh 


SSCRIPT="'salary.ec.ECSalaryReportRunner'" 

# Sets the PERIOD_START variable, if it is not set
if [ -z "$PERIOD_START" ]; then
    # last month first day
    PSTART=`date --date="$(date +%Y-%m-15) -2 month" +01%b%Y`
else
    PSTART=`date --date="$PERIOD_START - 1 month" +01%b%Y`
fi

# Sets the PERIOD_END variable, if it is not set
if [ -z "$PERIOD_END" ]; then
    # currnet month first day
    PEND=$(date +01%b%Y)
else
    PEND=$PERIOD_END
fi

# Sets the RELEASE_RUN variable, if it is not set. It is set in task.xml, passed as True when Release true else dont pass anything

if [ -z "$1" ]; then
    RRUN="FALSE"
else
    RRUN="TRUE"
fi

# Sets the PLANNING_AREA variable, if it is not set
if [ -z "$PLANNING_AREA" ]; then
    PAREA="ALL"
else
    PAREA=$PLANNING_AREA
fi

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

echo CARMUSR: $CARMUSR

SK_APP=Tracking
export SK_APP

# Unset CARMTMP and CARMSYS. This needs to be done if started by Deamond
# since we then need to switch environment from Tracking to Planning
unset CARMSYS
unset CARMTMP

# Sets CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
. $CARMUSR/bin/carmenv.sh


timestamp=`date '+%Y%m%d.%H%M.%S'`


echo "PERIOD_START=$PSTART PERIOD_END=$PEND PLANNING_AREA=$PAREA START_SCRIPT=$SSCRIPT RELEASE_RUN=$RRUN RUN_AND_EXIT=TRUE $CARMUSR/bin/studio.sh -S t -d"
PERIOD_START=$PSTART PERIOD_END=$PEND \
PLANNING_AREA=$PAREA START_SCRIPT=$SSCRIPT \
RUN_EC_AND_EXIT=TRUE RELEASE_RUN=$RRUN \
$CARMUSR/bin/studio.sh -S t -d | \
/usr/bin/tee $CARMTMP/logfiles/ec_report.$timestamp.log
