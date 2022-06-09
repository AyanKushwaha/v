#!/bin/bash
# Script to package recorded livefeed files from the SAS test system
#

function package {
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
if [ ${#tosend[@]} -eq 0 ] && [ ${#tosend2[@]} -eq 0 ]; then
  echo "No files to send..."
  exit
fi

echo $today > $DATESTAMP
}


package
exit
