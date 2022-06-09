#! /usr/bin/env bash
{
if [[ -f /opt/Carmen/CARMUSR/LIVEFEED/bin/carmenv.sh ]]; then
	. /opt/Carmen/CARMUSR/LIVEFEED/bin/carmenv.sh 
	# /opt/Carmen/CARMUSR/LIVEFEED/bin/cmsshell "/etc/telegraf/scripts/rpc_test.py portal_publish"
else
	. /opt/Carmen/CARMUSR/PROD_TEST/bin/carmenv.sh
	# /opt/Carmen/CARMUSR/PROD_TEST/bin/cmsshell "/etc/telegraf/scripts/rpc_test.py portal_publish"
fi
TERM="vt100"
# cd $CARMUSR/bin/shell
if [[ $1 ]]; then 
	python -c "import rpc; rpc.python('"$1"','2+2') "
else
	# exec /etc/telegraf/scripts/rpc_test.py "portal_publish"
	exec /etc/telegraf/scripts/rpc_test.py
	
fi
} 2>&1 
exit 0
