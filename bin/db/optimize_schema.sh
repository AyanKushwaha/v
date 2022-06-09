#!/bin/sh
# $Header: 
#
# Script to truncate the transient db tables listed in $CARMUSR/etc/truncate.xml
#

# This script is located in the CARMUSR, get absolute path
# Assume that the start script is located in the carmusr get abolute path
# by assuming that a crc directory exist at the top level
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

# CARMUSR setup
. ${CARMUSR}/bin/carmenv.sh

# Use xmlconfig to get values of connect string and schema.
XMLCONFIG=$CARMSYS/bin/xmlconfig
_dbconnect=`$XMLCONFIG --url database`
_schema=`$XMLCONFIG data_model/schema | sed 's/^[^=]\+ = //'`

echo "Optimizing $_schema using $_dbconnect"
carmrunner DMOptimize -c $_dbconnect  $_schema 
