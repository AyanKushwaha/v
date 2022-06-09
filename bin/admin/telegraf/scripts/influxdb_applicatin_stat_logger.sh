#! /usr/bin/env bash

# echo $USER
if [[ $1 ]]; then 
	# echo "some input $1"
	ps -u carmadm -o %mem,%cpu,cmd | grep -v grep | grep -i $1 | awk -v tag=$1 '{memory+=$1;cpu+=$2} END {print "cms_apps,application="tag,"memory="memory",cpu="cpu}'
	#echo 'example,tag1=a,tag2=b i=42i,j=43i,k=44i'
else 
	echo "Error: no input"
fi
