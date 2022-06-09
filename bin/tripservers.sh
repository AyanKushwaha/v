#!/bin/sh 
#
#	Script to manage the trip servers. 
#

usageText() {
    myname=`basename $0`
    echo "Script to start and stop trip servers
Usage: $myname [-n \"port...\"] [-k num] [stop|start]
    or $myname -h
       -h         prints this message and exit
       -n lst     give a list of port numbers to use
       -k num     do change on num port numbers starting with the first number in -n list
       -m host    run command on host, only effective together with the stop command
"
    exit 0
}

# Sets default values on host and ports
host=
ports=8000

# Parse all arguments. 
while getopts hn:k:m: option
do
  case "$option" in
  k)	k=0
  	if [ -n "$ports" ]; then
	    port1=$ports
	else
	    port1=8000
	fi
  	ports=
  	while [ $k -lt "$OPTARG" ] ; do
	    ports="$ports `expr $port1 + $k`"
	    k=`expr $k + 1`
  	done
	;;
  h)	usageText ;;
  n)	ports="$OPTARG";;
  m)	host="$OPTARG";;
  *)	echo "$myname: unknown option: $option"; exit 1;;
  esac
done
shift `expr $OPTIND - 1`

# Makes sure there is a stop/start argument given
if [[ $# == 1 ]] && [[ $1 == "stop" ]] || [[ $1 == "start" ]]; then 
    # Sets the CARMUSR variable, if it is not set
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

    # Sets SK_APP
    SK_APP=Planning
    export SK_APP
    
    # Sets all needed variables
    . $CARMUSR/bin/carmenv.sh

else usageText
fi

if [ -z "$host" ]; then
    host=`hostname`
fi
if [ -z "$host" ]; then
    echo "$myname: host not specified, please use -m option"
    exit 1
fi

if [ -z "$ports" ]; then
    echo "$myname: port not specified, please use -n option"
    exit 1
fi

if [[ $1 == "stop" ]]; then 
    for port in $ports; do
	python $CARMUSR/lib/python/interbids/StopAnyServer.py "$host" $port
    done
elif [[ $1 == "start" ]]; then

    # Get rid of start argument
    shift
 
    for port in $ports; do
	timestamp=`date '+%Y%m%d.%H%M.%S'`
	LOG_FILE=$CARMTMP/logfiles/tripservers/BidInfoServer.$USER.$timestamp.$HOSTNAME${port:+.$port}.log
	
	echo "Starting Trip server on $host:$port"
	SK_ARG="-d -p PythonRunFile(\"interbids/BidInfoServer.py\",\"${port:+-n}\",\"$port\",\"-h\",\"$host\")"
	$CARMSYS/bin/studio $SK_ARG -l $LOG_FILE & 
    done
fi
