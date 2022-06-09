#! /usr/bin/env bash

# Author: Mahdi Abdinejadi <mahdi.abdinejdi@hiq.se>
# This a simple script to dump list of process that uses more than 0.5 percent of cpu cores if 
# the system cpu usage reach the LIMIT (Default value for the limit is 90 percent)
# We have 90 as default for studio host and 95 as an argument on optimization and sysmond host
#

CPU_USAGE=$(grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print int(usage)}')
function list_proc ()
{
	echo "###`date +%F_%H-%M-%S`###pid ppid uname pcpu pmem comm cmd"
	ps -e -o pid,ppid,uname,pcpu,pmem,comm,cmd |sort -nr -k 4 | awk 'eval $4 > 0.5 {print}' | tr -s ' '
}

function list_proc_log ()
{
	if [ -d /var/carmtmp/logfiles ] ; then
		LOG_FOLDER="/var/carmtmp/logfiles/"
	else if [ -d /opt/Carmen/CARMUSR/PROD/current_carmtmp/logfiles ] ; then 
		LOG_FOLDER="/opt/Carmen/CARMUSR/PROD/current_carmtmp/logfiles/"
	else if [ -d /opt/Carmen/CARMUSR/PROD_TEST/current_carmtmp/logfiles ] ; then
		LOG_FOLDER="/opt/Carmen/CARMUSR/PROD_TEST/current_carmtmp/logfiles/"
	fi
	fi
	fi
	if [[ -z ${LOG_FOLDER:-} ]]; then
		echo "Log folder is not available..."
		exit 1
	else
		LOG_FILE="${LOG_FOLDER}cpu_usage.`hostname`.`date +%F`.log"
		echo "Trying to save the processes list to ${LOG_FILE}"
		list_proc 2>&1 | tee -a ${LOG_FILE}
	fi
}

if [[ -z $1 ]] ; then
	LIMIT="90"
else
	LIMIT=$1
fi
if [[ ${CPU_USAGE} -gt ${LIMIT} ]] ; then
	echo "cpu_usage is ${CPU_USAGE} and greater than ${LIMIT} percent at `date +%F_%H-%M-%S`"
	list_proc_log
else
	echo "cpu_usage is ${CPU_USAGE} and smaller than ${LIMIT} percent at `date +%F_%H-%M-%S`"
fi
