#!/bin/bash

LOG=${CARMTMP}/logfiles/`basename $0 .sh`.${USER}.$(date +%Y%m%d.%H%M.%S).`hostname -s`.log
{
echo $LOG

_DB_LOC="`echo $DB_CP_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

FROM='validity_period_no_ufn'
TO='validity_period_days_for_prod'

echo "===== Bids to change bidpropertytype from $FROM to $TO"
sqlplus -S $_DB_LOC <<EOF ;
set linesize 2000
select bp.bidpropertyid from bidproperties bp, bids b where bp.bidpropertytype like '$FROM' and b.bidtype = 'days_for_production' and bp.BIDSEQUENCEID = b.BIDSEQUENCEID;
EOF
echo "====="

echo "===== Updating"
sqlplus -S $_DB_LOC <<EOF ;
update bidproperties bp set bp.BIDPROPERTYTYPE = '$TO' where exists (select * from bids b where bp.bidpropertytype = '$FROM' and b.bidtype = 'days_for_production' and bp.BIDSEQUENCEID = b.BIDSEQUENCEID);
EOF
echo "====="
} | tee -a ${LOG}
