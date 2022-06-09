#!/bin/sh
 
connstr=$1
if [ -z $connstr ] ; then
  connstr=$DATABASE
fi

schema=$2
if [ -z $schema ] ; then
  schema=sascms_t
fi
 
echo "Starting Table Manager"
mpid=`$CARMUSR/bin/testing/start-mirador.sh`
#echo "mpid=$mpid"
 
mport=""
cnt=0
while [ -z "$mport" -a "$cnt" -lt 3 ]; do
  sleep 5
  mport=`$CARMUSR/bin/testing/find-mirador-port.sh $mpid`
#  echo "mport=$mport"
  cnt=`expr 1 + $cnt`
#  echo "cnt=$cnt"
done
 
if [ -z "$mport" ] ; then
  echo "No table manager found"
  exit 1
fi
 
echo "Attaching to table manager (localhost:$mport)"
$CARMUSR/bin/testing/start-table.sh $mport $connstr $schema
 
echo "Terminating table manager"
kill $mpid
 
echo "Done."

