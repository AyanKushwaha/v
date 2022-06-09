#!/bin/sh
# @(#) $Header$

# Run Python file from within Studio using PythonRunFile.
#
# The advantage of this method is that the Python module does not have to be
# pre-loaded (using StudioCustom etc.)
#
# Note: Give the full path to the Python script.
#
# Note: The called Python script must immediately save sys.argv, if arguments
# are used.
#
# Note: For an example, see e.g. batchstudio.py


script=`basename $0`
_dirname=`dirname $0`
whereami=`(cd $_dirname; pwd)`


build_python_args ( )
{
    # Build string like: PythonRunFile("python_file.py", "arg1", "arg2", ...)
    x="PythonRunFile(\"$1\""
    shift
    z=","
    for a in ${1+"$@"}
    do
        x="$x$z\"$a\""
    done
    echo "$x)"
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


if [ -z "$1" ]
then
    echo "usage: $script python_file.py [arg(s)]" 1>&2
    echo "Runs Python file from within Studio." 1>&2
    exit 2
fi

: ${SK_APP:="Server"}
export SK_APP

# Calculate value of CARMUSR if not set
: ${CARMUSR:="`get_carmusr`"}
export CARMUSR

# Set CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
. $CARMUSR/etc/carmenv.sh

logfile="$CARMTMP/logfiles/`basename $0 .sh`.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"
args="`build_python_args ${1+"$@"}`"
cat <<tac | tee $logfile
******************************************************************************
$script `date '+%Y-%m-%dT%H:%M:%S'`

Running the following command:
$args

Log file : $logfile

SK_APP   : $SK_APP
CARMUSR  : $CARMUSR
CARMSYS  : $CARMSYS

******************************************************************************
tac

# Start studio with -d for (daemon) virtual display
exec $CARMSYS/bin/studio '-d' '-p' "$args" | /usr/bin/tee -a $logfile

# End of file (will never reach this far because of exec above)
