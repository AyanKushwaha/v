#!/bin/sh

source `dirname $0`/../bin/carmenv.sh
$CARMUSR/current_carmsys_cct/bin/sysmondctl $@
