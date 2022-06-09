#!/bin/sh
# @(#) $Header: /opt/Carmen/CVS/sk_cms_user/bin/admin/mcl.sh,v 1.1 2009/10/08 10:06:21 adg348 Exp $
# Script to force ADD/DELETE of Master Crewlist (SASCMS-689)

if [ -z "$CARMUSR" ]
then
    echo "`basename $0`: ERROR: Environment \$CARMUSR is not set." 1>&2
    exit 2
fi

. $CARMUSR/bin/carmenv.sh

LD_LIBRARY_PATH=$CARMUTIL/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH
PATH=$CARMUTIL/bin:$PATH

exec $CARMSYS/bin/carmpython $CARMUSR/lib/python/adhoc/mcl.py ${1+"$@"}
