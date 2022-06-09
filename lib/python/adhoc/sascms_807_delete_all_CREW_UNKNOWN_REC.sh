#!/bin/sh
# $Header$
# Script for deleting all records in crew_unknown_rec
#

_origin=`pwd`
cd `dirname $0`
while [ `pwd` != '/' -a ! -d "crc" ]
do
  cd ..
done
CARMUSR=`pwd`
export CARMUSR
cd $_origin

# Sets all variables needed for running the scripts (and some more)
. $CARMUSR/etc/carmenv.sh

# Use xmlconfig to get values of connect string and schema.
XMLCONFIG=$CARMSYS/bin/xmlconfig
_dbconnect=`$XMLCONFIG --url database`
_schema=`$XMLCONFIG data_model/schema | sed 's/^[^=]\+ = //'`

echo "Deleting from CREW_UNKNOWN_REC..."
carmpython adhoc/sascms_807_delete_all_CREW_UNKNOWN_REC.py -c $_dbconnect -s $_schema
echo "Truncating CREW_UNKNOWN and CREW_UNKNOWN_REC..."
carmrunner dave_truncate_history -c $_dbconnect -s $_schema -g ${CARMUSR}/lib/python/adhoc/sascms_807_truncate.xml

