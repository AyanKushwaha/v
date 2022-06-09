#!/usr/bin/env bash

# Script is meant to be run as a crontab on the 16:th of each month
# It will Update the published column to TRUE for all that are FALSE, detailed instructions on why can be found in SKCMS-1590

CARMUSR="/opt/Carmen/CARMUSR/LIVEFEED"
LOG_DIR="$CARMUSR/data/migration/VAVA1F7/update_logs_data_`date +%Y%m%d_%H.%M.%S.log`"

echo "********************************************"
echo " Update Database Data VA/VA1/F7 script"
echo "********************************************"
echo $CARMUSR
echo $LOG_DIR
echo "********************************************"

. $CARMUSR/bin/carmenv.sh

echo 'update account_entry set published ='"'"'Y'"'"' where published = '"'"'N'"'"' and deleted = '"'"'N'"'"' and next_revid = 0 and (account='"'"'VA'"'"' or account='"'"'VA1'"'"' or account='"'"'F7'"'"') and (source like '"'"'VA%'"'"' or source like '"'"'F7%'"'"' or source like '"'"'Bought Days%'"'"') and tim >= carmdate.date2min((select to_char((SELECT add_months(trunc(sysdate) - (to_number(to_char(sysdate,'"'"'DD'"'"')) - 1), -1) FROM dual), '"'"'YYYY-MM-DD'"'"') from dual)) and tim < carmdate.date2min((select to_char((SELECT add_months(trunc(sysdate) - (to_number(to_char(sysdate,'"'"'DD'"'"')) - 1), 12) FROM dual), '"'"'YYYY-MM-DD'"'"') from dual));' | sql | tee $LOG_DIR

echo "********************************************"
echo " Update completed "
echo "********************************************"
echo " Logfile:" $LOG_DIR
echo "********************************************"
