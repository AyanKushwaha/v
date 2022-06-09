#!/bin/sh
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/cleanup_schema.sh,v 1.3 2009/07/31 12:50:37 adg348 Exp $
#
# Script to cleanup various db tables listed in $CARMUSR/etc/programs/dave_cleanup.xml
#


echo "[$(date)] Starting script cleanup_schema.sh"

# Use xmlconfig to get values of connect string and schema.
XMLCONFIG=$CARMSYS/bin/xmlconfig
_dbconnect=`$XMLCONFIG --url database`
_schema=`$XMLCONFIG data_model/schema | sed 's/^[^=]\+ = //'`

CLEANUP_XML="${CARMUSR}/etc/programs/dave_cleanup_archiving.xml" # TODO: change name to archiving
LOGFILE="${CARMTMP}/logfiles/cleanup_schema_archiving.$USER.`date '+%Y%m%d.%H%M.%S'`.$HOSTNAME"

echo "Cleaning up $_schema using $_dbconnect with:"
echo " ${CLEANUP_XML} as cleanup specification"
carmrunner dave_cleanup -c "${_dbconnect}" -v -s "${_schema}" -g ${CLEANUP_XML} -L ${LOGFILE}

echo "[$(date)] Script finished"
