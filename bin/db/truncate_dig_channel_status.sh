#!/bin/bash
# Script to truncate dig_channel_status.
#

function check_num_rows() {
    TABLE_NAME=$1
    echo "[$(date)] - Checking size of table $TABLE_NAME ..."
    $CARMUSR/bin/cmsshell sql "select count\(*\) from $TABLE_NAME"
}

DUMP_DIR=$CARMTMP/dig_channel_truncate_$(date +%Y%m%d_%H%M)
DUMP_LOG=$DUMP_DIR/dump.log
DUMP_FILE=$DUMP_DIR/dig_channel_status.etab
DIFF_LOG=$DUMP_DIR/diff.log

echo "[$(date)] - Starting script truncate_dig_channel_status.sh"

echo "***************************************************************"
echo "* Truncate script for dig_channel_status                      *"
echo "*                                                             *"
echo "* Make sure that Sysmond is stopped when running this script! *"
echo "*                                                             *"
echo "***************************************************************"
echo " Logs and data will be saved in:"
echo "    $DUMP_DIR"
echo ""
echo "[$(date)] - Setting up environment"

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

echo "This script will truncate the table 'dig_channel_status' on database $_schema using $_dbconnect"
read -n1 -p "Continue (y/n)"
[[ $REPLY = [yY] ]] && echo "" || { echo "Aborting ..."; exit 1; }

echo "[$(date)] - Checking size of table $TABLE_NAME ..."
check_num_rows dig_channel_status

echo "[$(date)] - Creating dir $DUMP_DIR ..."
mkdir $DUMP_DIR

echo "[$(date)] - Dumping table 'dig_channel_status' to $DUMP_DIR ..."
$CARMSYS/bin/carmrunner etabdump -v -c "${_dbconnect}" -s "${_schema}" -f - ${DUMP_DIR} > $DUMP_LOG 2>&1 << EOF
<?xml version="1.0" ?>
<etabdump version="0.1" defmode="ignore" missmode="ignore">
<map entity="dig_channel_status" etab="dig_channel_status" defmode="copy">
</map>
</etabdump>
EOF

if [ $? != "0" ]; then
    echo "********************************************"
    echo "Failed to dump table, check $DUMP_LOG"
    echo "Truncate task FAILED"
    echo "********************************************"
    exit 1
fi

echo "[$(date)] - Checking dumpfile ..."

DUMP_FILE_EXISTS=0

if [ -f $DUMP_FILE ]; then

    DUMP_FILE_EXISTS=1
    echo "[$(date)] - Dumpfile exists"

else
    echo "[$(date)] - Error: Table seems to be empty (no dumpfile exists), exiting!"
    exit 1
fi

# SQL truncate table
echo "[$(date)] - Truncating table ..."
$CARMUSR/bin/cmsshell sqladm "truncate table $_schema.dig_channel_status"

echo "[$(date)] - Checking size of table dig_channel_status after truncate ..."
check_num_rows dig_channel_status

# etabdiff data back
echo "[$(date)] - Loading dumped data back to table ..."
$CARMSYS/bin/carmrunner etabdiff -a -v -c "${DB_URL}" -s "${DB_SCHEMA}" -f - $DUMP_FILE > $DIFF_LOG 2>&1 << EOF
<?xml version="1.0" ?>
<etabdiff version="0.1" defmode="ignore" missmode="error">
<map entity="dig_channel_status" etab="dig_channel_status" defmode="copy">
</map>
</etabdiff>
EOF

if [ $? != "1" ]; then
    echo "********************************************"
    echo "Failed to put data back in truncated table,"
    echo "check $DIFF_LOG"
    echo "Table data is stored in $DUMP_FILE"
    echo ""
    echo "Migration task FAILED"
    echo "********************************************"
    exit 1
fi

echo "[$(date)] - Checking size of table dig_channel_status after data has been reverted  ..."
check_num_rows dig_channel_status
