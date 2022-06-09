#!/bin/sh
# @(#) $Header: /opt/Carmen/CVS/sk_cms_user/bin/nightly_cleanups.sh,v 1.2 2009/04/03 15:18:15 sandberg Exp $
#
# This script will launch the nightly cleanup script
#
# Author: Christoffer Sandberg, Jeppesen


echo "[$(date)] Starting script nightly_cleanups.sh"

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
cd $whereami

. $CARMUSR/bin/carmenv.sh

#PYTHONPATH=$CARMSYS/lib/python/carmensystems/mave/gm/compat:$PYTHONPATH
#echo PYTHONPATH:$PYTHONPATH

$CARMSYS/bin/mirador -s carmusr.NightlyCleanups -c $DB_URL -s $DB_SCHEMA 


echo "[$(date)] Script finished"