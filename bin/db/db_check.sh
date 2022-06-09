#!/bin/sh
# Script to verify schema integrety
# Script assumes it is located in CARMUSR/bin/db

usage_text() {
    echo "Usage: `basename $0` [-s schema_name] "
    echo "        -s: Use this schema instead of the configured one"
    echo "        -t: Comma separated list of tables to scan"
    echo "        -e: Comma separated list of tables to exclude from scan"
    echo "        -q: Quiet output (no statistics)"
    echo "        -h: This help text"
    exit
}

script=`basename $0`
whereami=`pwd`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
cd $whereami

. $CARMUSR/bin/carmenv.sh

_schema=$SCHEMA
_opts=""
while getopts hqs:t:e: option; do
    case "$option" in
        s) _schema="$OPTARGS";;
	t) _opts="$_opts -t $OPTARG";;
        e) _opts="$_opts -e $OPTARG";;
        q) _opts="$_opts -q";;
	h) usage_text;exit;;
        *) usage_text ;;
    esac
done

shift `expr $OPTIND - 1`

[ $# -gt 0 ] && usage_text

# change user
SCHEMA_CONNECT_STRING=`echo $DATABASE | sed "s%^\([^:]*\):\([^@]*\)@\(.*\)$%\1:$_schema/$_schema@\3%"`

# echo $CARMSYS/bin/mirador -s adhoc.db_status -s $_schema -c $SCHEMA_CONNECT_STRING $_opts
$CARMSYS/bin/mirador -s adhoc.db_status -s $_schema -c $SCHEMA_CONNECT_STRING $_opts
