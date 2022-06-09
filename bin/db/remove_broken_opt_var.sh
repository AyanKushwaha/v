#!/bin/sh
# @(#) $Header: /opt/Carmen/CVS/sk_cms_user/bin/remove_broken_opt_var.sh,v 1.3 2009/06/29 14:28:47 sandberg Exp $
# This script will find and delete all optional base variants where the main kernel is missing.
# If the main kernel is missing studio will have severe stability issues.
#
# Author: Christoffer Sandberg, Jeppesen


usage_text() {
    echo "Usage: `basename $0` [-s schema_name] [-n] <fromdate> <todate> "
    echo "        -s: use this schema instead of the configured one"
    echo "        -n: no commit, nothing will be changed in the database"
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
_extras=""
while getopts s:n option; do
    case "$option" in
        s) _schema="$OPTARG";;
	n) _extras="$_extras --no-commit";;
        *) usage_text ;;
    esac
done

shift `expr $OPTIND - 1`

[ $# -ne 2 ] && usage_text

# change user
SCHEMA_CONNECT_STRING=`echo $DATABASE | sed "s%^\([^:]*\):\([^@]*\)@\(.*\)$%\1:$_schema/$_schema@\3%"`
timestamp=`date '+%Y%m%d.%H%M.%S'`
LOGDIR=$CARMTMP/logfiles
[ -d $LOGDIR ] || mkdir -m a+rwxt $LOGDIR
LOGFILE=$LOGDIR/$script.$USER.$HOSTNAME.$timestamp
$CARMSYS/bin/mirador -s carmusr.OptRemover -s $_schema -c $SCHEMA_CONNECT_STRING $_extras $1 $2  2>&1 | /usr/bin/tee $LOGFILE
