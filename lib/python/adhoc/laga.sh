#!/bin/sh

CARMUSR=/opt/Carmen/CARMUSR/sp4_sync_user
export CARMUSR

CARMUTIL=/opt/carmutil/util/14/x86_64_linux

LD_LIBRARY_PATH=$CARMUTIL/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH

PATH=$CARMUTIL/bin:$PATH
TNS_ADMIN=$HOME/dat/network/admin
export TNS_ADMIN

. $CARMUSR/etc/carmenv.sh


$CARMSYS/bin/carmpython laga.py ${1+"$@"}
