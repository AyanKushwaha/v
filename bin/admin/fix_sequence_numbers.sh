#!/bin/sh
# @(#) $Header: /opt/Carmen/CVS/sk_cms_user/bin/admin/fix_sequence_numbers.sh,v 1.5 2009/05/28 06:34:30 sandberg Exp $

script=`basename $0`
whereami=`pwd`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
cd $whereami

. $CARMUSR/etc/carmenv.sh

# One per line
sequences='seq_salary_run seq_meal_order seq_meal_forecast'  

error ( ) {
    echo "$script: ERROR: $*" 1>&2
    exit 2
}


print_usage ( ) {
    cat <<__tac__
usage: $script [-s schema_name]

This script will adjust the sequences so that next number
will be greater than the max value in the referring tables.

The following sequences will be fixed
$sequences

__tac__
}



fix_seq ( ) {
    case "$1" in
        'seq_salary_run')
            sql="select nvl(max(runid),0) from ${_schema}.salary_run_id"
            ;;
	'seq_meal_order')
	    sql="select nvl(max(order_number),0) from ${_schema}.meal_order where forecast='N'"
	    ;;
	'seq_meal_forecast')
	    sql="select nvl(max(order_number),0) from ${_schema}.meal_order where forecast='Y'"
	    ;;
        *)
            error "The sequence $1 is not supported."
            ;;
    esac
    $CARMSYS/bin/carmpython  <<__end_python__
from carmensystems.dave import DMF
def reset_seqno():
    conn = DMF.Connection("${conn}")
    conn.rquery("${sql}", None)
    max, = conn.readRow().valuesAsList()
    conn.endQuery() 
    if max == 0:
       print"\nNo values found, skipping sequence '%s'" % ("$1")
    else:
       print "\nSetting value of sequence '%s' to '%d'." % ("$1", max)
       conn.setSeqValue("$1", max)
    conn.close()

reset_seqno()
__end_python__
}

_schema=$DB_SCHEMA
while getopts s:h flag
do
    case "$flag" in
        s) _schema="$OPTARG";;
        h) print_usage; exit 0;;
    esac
done

shift `expr $OPTIND - 1`
conn=`echo $DATABASE | sed "s%^\([^:]*\):\([^@]*\)@\(.*\)$%\1:$_schema/$_schema@\3%"`

for seq in $sequences
do
    fix_seq $seq
done

# eof
