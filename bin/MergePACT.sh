#!/bin/sh
# Script to merge PACTs of the same code that starts exactly when the previous one ends
# Script assumes it is located in CARMUSR/bin
# Author: Christoffer Sandberg, Jeppesen


usage_text() {
    echo "Usage: `basename $0` [-s schema_name] "
    echo "        -s: use this schema instead of the configured one"
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
while getopts s: option; do
    case "$option" in
        s) _schema="$OPTARG";;
        *) usage_text ;;
    esac
done

shift `expr $OPTIND - 1`

[ $# -gt 0 ] && usage_text

# change user
SCHEMA_CONNECT_STRING=`echo $DATABASE | sed "s%^\([^:]*\):\([^@]*\)@\(.*\)$%\1:$_schema/$_schema@\3%"`
PYTHONPATH=$CARMSYS/lib/python/carmensystems/mave/gm/compat:$PYTHONPATH
echo PYTHONPATH:$PYTHONPATH
$CARMSYS/bin/mirador -s adhoc.MergePACT $_schema $SCHEMA_CONNECT_STRING
