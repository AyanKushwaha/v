#!/bin/sh
# start accumulation of data

script=`basename $0`
whereami=`dirname $0`
usage="usage: $script [-h] [-p plan] [-t date] [-x extractdate] [-s] [accumulator]"


build_python_eval ( )
{
    # Build string like: PythonEvalExpr("accumulators_manual.start('arg1', 'arg2', ...)")
    x="PythonEvalExpr(\"accumulators_manual.start("
    z=""
    for a in ${1+"$@"}
    do
        x="$x$z'$a'"
        z="," # Second and subsequent arguments will be prepended by ", "
    done
    echo "$x)\")"
}


error ( )
{
    echo "$script: ERROR: $*" 1>&2
    echo "'$script -h' for help" 1>&2
    exit 2
}


get_carmusr ( )
{
    # Return estimated value of CARMUSR based on the location of this script.
    (
        cd "$whereami"
        while [ `pwd` != '/' -a ! -d "crc" ]
        do
            cd ..
        done
        pwd # Echo the current directory
    )
}


print_usage ( )
{
    cat <<__tac__
$usage

OPTIONS
    -h              This help text

    -m              Optional: only handle crew of this main category, can be
                    'F' or 'C'.

    -r              Optional: only handle crew belonging to this region, can
                    be any of {'SKD', 'SKI', 'SKN', 'SKL', 'SKS'}.

    -s              Optional: only run specified accumulator. This flag is required
                    when script is run with 'specific' accumulator argument. Prefix
                    accumulatorname with 'accumulators.accumulator_name'

    -t to_date      Accumulate until this date (optional argument). Default is
                    today. The date format is '12Aug2007' or '20070812'.

    -x extractdate  Only used with accumulator option 'installation'.

accumulator can be one of:
    'account'       Update crew accounts.
    'airport'       Update airport qualifications.
    'ctl'           Update crew training log.
    'rave'          Rave accumulators
    'ravepub'       Rave publish-accumulators
    'rec'           Update recurrent documents' due date.
    'trip'          Recreate Rave trips.
    'lifeblockhrs'  Update lifetime block hours per ac family
    'new-hire'      Update new_hire_follow_up table
    'specific'      Run a specific accumulator only

    'installation'  All above including 'trip', to be run at installation.
    'all'           All above excluding 'trip', to be run nightly.

If no accumulator is given, 'all' is assumed.
__tac__
}


# Default options
: ${TODAY="`date '+%d%b%Y'`"}
FILTERMAINCAT=None
FILTERREGION=None
PLANPATH=
EXTRACTDATE=None
SPECIFICACCUMULATOR=

while getopts hm:p:r:t:x:s: flag
do
    case "$flag" in
        h) print_usage; exit 0;;
        m) FILTERMAINCAT=$OPTARG;;
        p) PLANPATH=$OPTARG;;
        r) FILTERREGION=$OPTARG;;
        t) TODAY=$OPTARG;;
        x) EXTRACTDATE=$OPTARG;;
        s) SPECIFICACCUMULATOR=$OPTARG;;
        '?') echo $usage; exit 2;;
    esac
done
shift `expr $OPTIND - 1`


SK_APP=Server
SK_APP_NAME=accumulators_manual
export SK_APP SK_APP_NAME

CARMUSECRSTMPFILE=True
export CARMUSECRSTMPFILE

# Calculate value of CARMUSR if not set
: ${CARMUSR:="`get_carmusr`"}
export CARMUSR

# Set CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
. $CARMUSR/bin/carmenv.sh

# Fetch the main plan from the config.xml file
XMLCONFIG=$CARMSYS/bin/xmlconfig
: ${PLANPATH:="`$XMLCONFIG $CARMUSR/etc/config.xml data_model/plan_path | awk '{print $3}'`"}

ACCUMULATOR="specific"
SPECIFICACCUMULATOR="accumulators.sh_all_fc_flight_acc"

echo "CARMUSR              : $CARMUSR"
echo "PLANPATH             : $PLANPATH"
echo "TODAY                : $TODAY"
echo "ACCUMULATOR          : $ACCUMULATOR"
echo "EXTRACTDATE          : $EXTRACTDATE"
echo "FILTERMAINCAT        : $FILTERMAINCAT"
echo "FILTERREGION         : $FILTERREGION"
echo "SPECIFICACCUMULATOR" : "$SPECIFICACCUMULATOR"
echo

logfile="$CARMTMP/logfiles/accumulator.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"
echo "logfile       : $logfile"
echo

build_python_eval_str="`build_python_eval $PLANPATH $TODAY $ACCUMULATOR $EXTRACTDATE $FILTERMAINCAT $FILTERREGION $SPECIFICACCUMULATOR`"
echo "build_python_eval_str  : $build_python_eval_str"
echo

# Start studio with -d for (daemon) virtual display
exec $CARMSYS/bin/studio '-d' '-p' $build_python_eval_str | \
    /usr/bin/tee $logfile || true

# End of file (will never reach this far because of exec above)
