#!/bin/bash
# Start batch jobs accounts reset

wherami=`dirname $0`
_CARMUSR=`(cd $wherami/../..; pwd)`

logdir="$CARMTMP/logfiles/salary/account"
[ ! -d $logdir ] && mkdir -p $logdir
logfile="$logdir/account.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"

exec &> >(tee -i $logfile)


error ( ) {
    echo "$*" 2>&1
    exit 2
}

usage ( ) {
    echo "Usage: $0 reset [--help] [--lastdate date] [--reason text]" 2>&1
    echo "          [--region <rgn>] [--base <base>] [--maincat {F|C} [--subcat RP]]" 2>&1
    echo "          <account1> [<account2>...]" 2>&1
    echo "   " 2>&1
    echo "       $0 undo [--help] --date date [--source <source>]" 2>&1
    echo "          <account1> [<account2>...]" 2>&1
    echo "       <account1> [<account2>...]" 2>&1
    echo "   " 2>&1
    echo "Where:" 2>&1
    echo "   reset" 2>&1
    echo "      resets the account(s) to zero at the given date." 2>&1
    echo "   undo" 2>&1
    echo "      nullifies the run on a specific date with a" 2>&1
    echo "      specific source." 2>&1
    exit 1
}

command=
case $1 in
 reset)
   command=reset ;;
 undo)
   command=undo ;;
 *)
   usage ;;
esac
shift 1


echo "[$(date)] Starting script account.sh"

SK_APP=Tracking
export SK_APP

# If CARMUSR not set, use current directory as reference point.
CARMUSR=${CARMUSR-"${_CARMUSR}"}
export CARMUSR

# Get other environment (CARMSYS, ...)
. $CARMUSR/bin/carmenv.sh

# Use xmlconfig to get values of connect string and schema.
XMLCONFIG=$CARMSYS/bin/xmlconfig
database=`$XMLCONFIG --url database`
schema=`$XMLCONFIG data_model/schema | sed 's/^[^=]\+ = //'`

[ -z "$database" ] && error "Could not get database. Check config.xml."
[ -z "$schema" ] && error "Could not get schema. Check config.xml."

exec $CARMSYS/bin/mirador -s salary.batch --connect "$database" --schema "$schema" $command ${2+"$@"}

echo "[$(date)] Script finished"

