#!/bin/sh
                                                                                
                                                                                
cpid=`ps -ef|awk  -v pid=$1 '{ if ($2==pid) { print $2} }' `
                                                                                
if [ -z "$cpid" ] ; then
  #echo "no Table Manager found"
#  echo "0"
  exit 1
fi
                                                                                
port=`netstat -anp 2>/dev/null|grep ${cpid}/mirador|grep LIST|awk '{print $4}'|sed 's/.*://'`
                                                                                
#echo "Table Manager port = $port"
echo $port
                                                                                
