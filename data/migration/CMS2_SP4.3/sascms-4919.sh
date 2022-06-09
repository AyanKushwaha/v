#!/bin/sh

. $CARMUSR/bin/carmenv.sh

SIZE=`$CARMUSR/bin/cmsshell sql "describe bid_leave_vacation" | grep 'AWARD_KEY'|tr ' (' '\n'|grep '^[0-9]'`
if [ $SIZE == "2000" ] ; then
    echo "The column already has the right size ($SIZE), no change necessary"
else
    echo "  * Setting the award_key column size in bid_leave_vacation as 2000"
    echo "  * Executing sql statements ..."
    $CARMUSR/bin/cmsshell sqladm <<EOF

ALTER TABLE $DB_SCHEMA.bid_leave_vacation        MODIFY (award_key VARCHAR(2000 CHAR));
ALTER TABLE $DB_SCHEMA.bid_leave_vacation_tmp    MODIFY (award_key VARCHAR(2000 CHAR));

/

COMMIT;

EOF
fi
