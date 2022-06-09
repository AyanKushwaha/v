
function migrate_table() {
TABLE_NAME=$1
PRE_NUM_COLUMNS=$2
# Migration script for SASCMS-3314
#

echo "############################################"
echo "# Migrating $TABLE_NAME"
echo "############################################"

MIGRATION_DIR=`dirname $0`
DUMP_DIR="$MIGRATION_DIR/${TABLE_NAME}_dump"
LOG_DIR="$MIGRATION_DIR/${TABLE_NAME}_logs"
DUMP_LOG="$LOG_DIR/dump.log"
REDUMP_LOG="$LOG_DIR/redump.log"
HANDLE_SCHEMA_LOG="$LOG_DIR/database_update.log"
DIFF_LOG="$LOG_DIR/diff.log"
DUMP_FILE="$DUMP_DIR/${TABLE_NAME}.etab"
DUMP_FILE_PRE_MODIFICATION="$DUMP_DIR/${TABLE_NAME}_pre_modification.etab"
DUMP_FILE_AFTER_MODIFICATION="$DUMP_DIR/${TABLE_NAME}_post_modification.etab"

echo " - Setting up ..."

if [ ! -e $LOG_DIR ]; then
    echo "    - Creating log dir ..."
    mkdir $LOG_DIR
fi

if [ ! -e $DUMP_DIR ]; then
    echo "    - Creating dump dir ..."
    mkdir $DUMP_DIR
fi

echo " - Dumping table '${TABLE_NAME}' to $DUMP_DIR ..."

$CARMSYS/bin/carmrunner etabdump -v -c "${DB_URL}" -s "${DB_SCHEMA}" -f - ${DUMP_DIR} > $DUMP_LOG 2>&1 << EOF
<?xml version="1.0" ?>
<etabdump version="0.1" defmode="ignore" missmode="ignore">
<map entity="${TABLE_NAME}" etab="${TABLE_NAME}" defmode="copy">
</map>
</etabdump>
EOF

if [ $? != "0" ]; then
    echo "********************************************"
    echo "Failed to dump table, check $DUMP_LOG"
    echo "Migration task FAILED"
    echo "********************************************"
    exit 1
fi

echo " - Checking state of current database ..."

DUMP_FILE_EXISTS=0

if [ -f $DUMP_FILE ]; then

    DUMP_FILE_EXISTS=1

else
    echo "    WARNING: Table seems to be empty!"
fi

echo " - Updating database definition ..."
$CARMUSR/bin/db/handle_schemas.sh -u $DB_SCHEMA $DB_SCHEMA > $HANDLE_SCHEMA_LOG 2>&1

if [ $? != "0" ]; then
    echo "********************************************"
    echo "Failed to update database definition, check $HANDLE_SCHEMA_LOG"
    echo "Migration task FAILED"
    echo "********************************************"
    exit 1
fi

echo "Updating data"

if [ $DUMP_FILE_EXISTS == "1" ]; then
    $CARMSYS/bin/carmrunner etabdiff -a -v -c "${DB_URL}" -s "${DB_SCHEMA}" -f - $DUMP_FILE > $DIFF_LOG 2>&1 << EOF
<?xml version="1.0" ?>
<etabdiff version="0.1" defmode="ignore" missmode="error">
<map entity="${TABLE_NAME}" etab="${TABLE_NAME}" defmode="copy">
</map>
</etabdiff>
EOF

    if [ $? != "0" ]; then
        echo "********************************************"
        echo "Failed to set defualt values, check $DIFF_LOG"
        echo "Migration task FAILED"
        echo "********************************************"
        exit 1
    fi

    if [ -f $DUMP_FILE ]; then
        mv $DUMP_FILE $DUMP_FILE_PRE_MODIFICATION
    fi

fi

echo " - Re-dumping table '${TABLE_NAME}' to $DUMP_DIR ..."

$CARMSYS/bin/carmrunner etabdump -v -c "${DB_URL}" -s "${DB_SCHEMA}" -f - ${DUMP_DIR} > $REDUMP_LOG 2>&1 << EOF
<?xml version="1.0" ?>
<etabdump version="0.1" defmode="ignore" missmode="ignore">
<map entity="${TABLE_NAME}" etab="${TABLE_NAME}" defmode="copy">
</map>
</etabdump>
EOF

if [ $? != "0" ]; then
    echo "********************************************"
    echo "Failed to dump table, check $REDUMP_LOG"
    echo "Migration task FAILED"
    echo "********************************************"
    exit 1
fi

if [ -f $DUMP_FILE ]; then
    mv $DUMP_FILE $DUMP_FILE_AFTER_MODIFICATION
fi

echo "********************************************"
echo "$TABLE_NAME migrated successfully!"
echo ""
echo " Log files:"
echo "  - $DUMP_LOG"
echo "  - $HANDLE_SCHEMA_LOG"
echo "  - $DIFF_LOG"
echo "  - $REDUMP_LOG"
echo ""
echo " Etab files:"
echo "  - $DUMP_FILE_PRE_MODIFICATION"
echo "  - $DUMP_FILE_AFTER_MODIFICATION"
echo "********************************************"
}
