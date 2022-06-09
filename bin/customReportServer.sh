#!/bin/sh
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/customReportServer.sh,v 1.4 2010/05/05 08:53:05 adg348 Exp $
#
# Script to start/stop a report server worker process with a custom
# (dynamically calculated) plan period.
# Sets the CARMUSR variable, if it is not set
#

default_node="dig_node"

get_node ( ) {
    # Find the node that runs SAS_RS_PORTAL_<...> and run the worker on the same node.
    portal_name=`echo $1 | sed 's/WORKER/PORTAL/'`
    node_name=`$CARMUSR/bin/xmlconfig.sh --srv | sed -n "/${portal_name}/s/^.*@\([^ ]\+\).*$/\1/p"`
    # If no match in config, use default_node.
    echo ${node_name:-"${default_node}"}
}


usage ( ) {
	echo "Script to start/stop a Custom reportserver instance"
	echo "Usage: "`basename $0`" [start|stop] worker nDaysFrom nDaysTo" 
	echo "  worker          : Name of worker process to start"
	echo "  nDaysFrom       : Load period start relative from now"
	echo "  nDaysTo         : Load period end relative from now"
	echo "Note that nDays* params must be prefixed with [+|-] "
	exit 0
}

[ $# -lt 2 ] && usage

if [ -z "$CARMUSR" ]; then
    a=`pwd`
    cd `dirname $0`
    while [ `pwd` != '/' -a ! -d "crc" ]; do
	cd ..
    done
    CARMUSR=`pwd`
    export CARMUSR
    cd $a
fi

# Sets CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
. $CARMUSR/bin/carmenv.sh

cmd=$1
worker=$2
export REL_START=$3
export REL_END=$4

node=`get_node $worker`
echo "Running command $cmd on $worker and node $node..."
$CARMSYS/etc/scripts/reportworkerStudio $cmd $node $worker
echo "...finished running command $cmd on $worker and node $node"
