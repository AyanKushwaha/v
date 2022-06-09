#!/bin/sh
# @(#) $Header: /opt/Carmen/CVS/sk_cms_user/bin/salary_batch.sh,v 1.3 2007/11/28 11:42:17 gronlund Exp $

# Start batch jobs for "Bought days and compensation days".

echo "[$(date)] Starting script batch.sh"

wherami=`dirname $0`
_CARMUSR=`(cd $wherami/../..; pwd)`


error ( ) {
    echo "$*" 2>&1
    exit 2
}


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

exec $CARMSYS/bin/mirador -s salary.batch --connect "$database" --schema "$schema" compdays ${1+"$@"}
# This was the last line to be executed...

# exec python $CARMUSR/lib/python/salary/batch.py --connect "$database" --schema "$schema" --nocommit --debug compdays ${1+"$@"}


echo "[$(date)] Script finished"

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
