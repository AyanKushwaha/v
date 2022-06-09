#!/bin/sh
echo "************************************************************"
echo "* SASCMS-5923: Inactivate all bids that should no longer be available for crew group FD LH          *"
echo "************************************************************"
echo ""

source $CARMUSR/bin/carmenv.sh
result=`sqlcp "update bids
set invalid=SYSTIMESTAMP
where bidsequenceid in (select bids.bidsequenceid from bids, bidgroups, usergroups, groups
where bids.bidgroupid = bidgroups.bidgroupid
and groups.groupid = usergroups.groupid
and usergroups.userid = bidgroups.userid
and bidgroups.bidgroupid = bids.bidgroupid
and groups.groupname='FD LH' and bids.invalid is NULL and bids.bidtype in 
('consecutive_days_off', 'consecutive_days_at_work', 'check_in', 'check_out', 'combination', 'compensation_days_fd', 'flight', 'leg_duration', 'string_of_days_off'))"`
echo $result


