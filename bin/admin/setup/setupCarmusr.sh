#!/bin/sh
#
# Assume that the start script is located in the carmusr get abolute path
# by assuming that a crc directory exist at the top level
#


function usage(){
    echo "Set up carmusr"
    echo "Usage: setupCarmusr.py [CARMSYSTEMNAME] [OPTIONS]"
    echo "    -h, --help"
    echo "          print this message"
    echo "    -d"
    echo "          debug mode. wont do anyhting"
    echo "    -s"
    echo "          show system configuration configuration"
    echo "    --nocheck"
    echo "          No exit when initial checks fail"
}

ARGS=""

while test $# -gt 0; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        -d)
            ARGS="$ARGS $1"
            shift
            ;;
        -s)
            ARGS="$ARGS $1"
            shift
            ;;
        --nocheck)
            ARGS="$ARGS $1"
            shift
            ;;
        *)
            export CARMSYSTEMNAME=$1
            shift
            ;;
    esac
done

#
# Set the CARMUSR path.
#
while [ `pwd` != '/' -a ! -d "crc" ]
do
  cd ..
done

export CARMUSR=`pwd`
PYTHON_RUN="$CARMUSR/bin/admin/setup/setupCarmusr.py $ARGS"
LOGFILE="$CARMUSR/bin/admin/setup/setup.log"
# Check if logfile exists
test -f $LOGFILE || touch $LOGFILE 
python $PYTHON_RUN 2>&1 $LOGFILE

exit_code=$?

chmod a+wr $LOGFILE

if [ $exit_code != 0 ]; then
    echo
    echo "----------------------------------------------------------------------"
    echo "There was a problem when setting up the carmusr. Please see log file:"
    echo "$CARMUSR/bin/admin/setup/setup.log"
    echo "----------------------------------------------------------------------"
    exit $exit_code
fi
