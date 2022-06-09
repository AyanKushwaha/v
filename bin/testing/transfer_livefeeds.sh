#!/bin/bash
# Script to transfer recorded livefeed files from the SAS test system
#
# Options:
#   -s		- Send files from SAS test system. Run on SAS
#		  system, e.g. h1crm93a
#   -r          - Receive the previously sent files. Run on vpn.
#

HOST='159.195.78.113'

function send {
if [ X$CARMTMP = X ]; then
  echo "Environment variable CARMTMP not defined, bailing out..."
  exit
fi

DATESTAMP=/users/carmadm/livefeed_transfer.dat
if [ -f $DATESTAMP ]; then
  LASTRUN=`cat $DATESTAMP`
else
  LASTRUN=20080101
fi
echo "Last run: $LASTRUN"
today=`date +'%Y%m%d'`

#
# Handle files recorded from MQ
#
tosend=()
cd $CARMTMP/logfiles/DIG
for queue in CQFREQ CQFTITA CQFMVTD CQF402 UCTI3 CQF436 CQFDIGX
do
  pattern=$queue\_LIVE\*log
  for file in $( find . -type f -maxdepth 1 -name "$pattern" )
  do
    noext=${file%.*}
    datum=${noext#*LIVE}
    if [ $datum -lt $today ] && [ $datum -ge $LASTRUN ]; then
      echo "Sending: $file"
      tosend=(${tosend[@]} $file)
    fi
  done
done
tar cvzf $CARMTMP/latest.tgz ${tosend[@]}
#
# Handle files transfered from external systems (ftp)
# Assume format e.g. FIA080312.TXT
#
tosend2=()
cd $CARMTMP
for ttype in ucTI1 FIA CUR OAA_IN
do
  pattern=$ttype\*TXT
  for file in $( find ftp/imported/ -type f -name "$pattern" )
  do
    noext=${file%.*}
    fn=${noext##*/}
    if [ ${#fn} -eq $((${#ttype}+6)) ]; then
      datum=20${noext:(-6)}
      if [ $datum -lt $today ] && [ $datum -ge $LASTRUN ]; then
        echo "Sending: $file"
        tosend2=(${tosend2[@]} $file)
      fi
    fi
  done
done
tar cvzf ftpfiles.tgz ${tosend2[@]}
#
# Send files
#
if [ ${#tosend[@]} -eq 0 ] && [ ${#tosend2[@]} -eq 0 ]; then
  echo "No files to send..."
  exit
fi
read -p "Enter ftp username: " USER
read -p "Enter $USER password (prefix): " PWDPREFIX
read -p "Enter securID: " SECURID
PASSWD=$PWDPREFIX$SECURID
ftp -n $HOST << END
quote USER $USER
quote PASS $PASSWD
bin
cd livefeeds
put latest.tgz
put ftpfiles.tgz
quit
END

echo $today > $DATESTAMP
}

function receive {
cd /carm/proj/skcms/migration/livefeeds
read -p "Enter ftp username: " USER
read -p "Enter $USER password (prefix): " PWDPREFIX
read -p "Enter securID: " SECURID
PASSWD=$PWDPREFIX$SECURID
ftp -n $HOST << END
quote USER $USER
quote PASS $PASSWD
bin
cd livefeeds
get latest.tgz
get ftpfiles.tgz
quit
END
tar xvzf latest.tgz
rm latest.tgz
tar xvzf ftpfiles.tgz
rm ftpfiles.tgz
}

if [ "$1" == "-s" ]; then
  send
elif [ "$1" == "-r" ]; then
  receive
else
  echo "Invalid argument $1"
fi
exit
