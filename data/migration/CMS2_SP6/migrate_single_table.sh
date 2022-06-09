
function migrate_table() {
TABLE_NAME=$1

echo "############################################"
echo "# Migrating $TABLE_NAME"
echo "############################################"

MIGRATION_DIR=`dirname $0`
LOG_DIR="$MIGRATION_DIR/${TABLE_NAME}_logs"
HANDLE_SCHEMA_LOG="$LOG_DIR/database_update.log"
MODEL_DROP="$MIGRATION_DIR/sas_legality_drop.xml"
MODEL_OLD="$MIGRATION_DIR/sas_legality_old.xml"
MODEL_PATH="$CARMUSR/data/config/models/sas_legality.xml"

echo " - Setting up ..."

if [ ! -e $LOG_DIR ]; then
    echo "    - Creating log dir ..."
    mkdir $LOG_DIR
fi

if [ ! -f $MODEL_PATH ]; then
    echo "********************************************"
    echo "Failed to set find sas_legality.xml"
    echo "Migration task FAILED"
    echo "********************************************"
    exit 1
fi

if [ ! -f $MODEL_DROP ]; then
    echo "********************************************"
    echo "Failed to set find sas_legality_drop.xml"
    echo "Migration task FAILED"
    echo "********************************************"
    exit 1
fi

echo " - Copying current model"
cp $MODEL_PATH $MODEL_OLD

if [ $? != "0" ]; then
    echo "********************************************"
    echo "Failed to copy current model!"
    echo "Migration task FAILED"
    echo "********************************************"
    exit 1
fi

echo " - Copying the drop model"
cp $MODEL_DROP $MODEL_PATH

echo " - Updating database definition by droppping apt_restriction..."
$CARMUSR/bin/db/handle_schemas.sh -u $DB_SCHEMA $DB_SCHEMA > $HANDLE_SCHEMA_LOG 2>&1

if [ $? != "0" ]; then
    echo "********************************************"
    echo "Failed the 1st update database definition, check $HANDLE_SCHEMA_LOG"
    echo "Migration task FAILED"
    echo "********************************************"
    cp $MODEL_OLD $MODEL_PATH
    exit 1
fi

echo " - Copying back current model"
cp $MODEL_OLD $MODEL_PATH

echo " - Updating database definition by adding new def. of apt_restriction..."
$CARMUSR/bin/db/handle_schemas.sh -u $DB_SCHEMA $DB_SCHEMA > $HANDLE_SCHEMA_LOG 2>&1

if [ $? != "0" ]; then
    echo "********************************************"
    echo "Failed the 2nd update database definition, check $HANDLE_SCHEMA_LOG"
    echo "Migration task FAILED"
    echo "********************************************"
    exit 1
fi


echo "********************************************"
echo "$TABLE_NAME migrated successfully!"
echo ""
echo " Log files:"
echo "  - $HANDLE_SCHEMA_LOG"
echo "********************************************"
}
