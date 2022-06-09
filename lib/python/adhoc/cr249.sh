#!/bin/sh

CARMUSR=${1-"/opt/Carmen/CARMUSR/sp4_livefeed_user"}
export CARMUSR

CARMUTIL=/opt/carmutil/util/14/x86_64_linux

LD_LIBRARY_PATH=$CARMUTIL/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH

PATH=$CARMUTIL/bin:$PATH
TNS_ADMIN=$HOME/dat/network/admin
export TNS_ADMIN

. $CARMUSR/etc/carmenv.sh

$CARMSYS/bin/carmpython `basename $0 .sh`.py ${1+"$@"}
