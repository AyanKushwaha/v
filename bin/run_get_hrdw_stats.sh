#!/bin/sh
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/run_get_hrdw_stats.sh,v 1.1 2008/10/29 14:12:23 antonio Exp $
#
# runs the get_hrdw_stats a specified number of times with a time interval
# 

usage_text() {
    echo "Usage: `basename $0` <time between runs in sec> [number of runs]"
    echo "To run indefinitely do not set [number of runs]"
    exit
}

# Test if it has at least one argument
if [ $# -lt 1 ]; then
  usage_text
fi  

nTime=$1
if [ $# -eq 1 ]; then
  while [ 1 -eq 1 ]; do
      bin/get_hrdw_stats.sh current_carmtmp/logfiles
      sleep ${nTime}
  done
else
  nRuns=$2
  for (( i=0 ; i<${nRuns} ; i++ )); do
    bin/get_hrdw_stats.sh current_carmtmp/logfiles
    sleep ${nTime}
  done
fi

exit 0
