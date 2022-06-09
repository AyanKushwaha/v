#! /usr/bin/env bash

## Author: Mahdi Abdinjadi mahdi.abdinejadi@hiq.se
## This script should be run periodically with crontab on nfs server.
{
echo "Start to gzip the log files at: `date`"

# Create a list of log file that are not gziped nor modified in last 7 days
LOGS=(`find /var/carmtmp/logfiles/DIG/ -mtime +7 | tail -n +2 | grep -v '.gz'`)

for log in ${LOGS[@]}; do
	(`/usr/sbin/lsof $log > /dev/null` && echo -e "\e[1;31m$log\e[0m is ignored.")  || (gzip $log && echo -e "\e[1;32m$log\e[0m is gziped")
done

echo "Finished to gzip the log files at: `date`"

# Create a list of old log file which have been modified before N days ago.
PROD_LOG_AGE=+365
OLD_LOGS=(`find /var/carmtmp/logfiles/DIG/ -mtime ${PROD_LOG_AGE} | tail -n +2 | grep '.gz'`)

for olog in ${OLD_LOGS[@]}; do
	# (`lsof $olog > /dev/null` && echo -e "\e[1;31m$olog is ignored.\e[0m")  || (echo -e "\e[1;32m$olog is removed\e[0m")
	(`/usr/sbin/lsof $olog > /dev/null` && echo -e "\e[1;31m$olog\e[0m is ignored.")  || (rm -f $olog && echo -e "\e[1;32m$olog\e[0m is removed")
done

echo "Finished to remove old log files at: `date`"

} | tee -a /var/carmtmp/logfiles/dig_log_archiver_prod.log.$(date +%Y-%m)
