#!/bin/sh
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/truncate_schema.sh,v 1.6 2010/06/01 14:41:11 ADU396 Exp $
#
# Script to truncate the transient db tables listed in $CARMUSR/etc/truncate.xml
#

# This script is located in the CARMUSR, get absolute path
# Assume that the start script is located in the carmusr get abolute path
# by assuming that a crc directory exist at the top level
#

echo "[$(date)] Starting script truncate_schema.sh"


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
XMLCONFIG=$CARMSYS/etc/scripts/xmlconfig
_dbconnect=`$XMLCONFIG --url database`
_schema=`$XMLCONFIG data_model/schema | sed 's/^[^=]\+ = //'`

echo "Truncating $_schema using $_dbconnect with:"
echo " ${CARMUSR}/etc/programs/dave_truncate_alert_history.xml as truncation specification"
carmrunner dave_truncate_history -c "${_dbconnect}" -v -s "${_schema}" -g ${CARMUSR}/etc/programs/dave_truncate_alert_history.xml


echo "[$(date)] Script finished"