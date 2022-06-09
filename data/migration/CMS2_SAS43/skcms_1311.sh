#!/bin/sh
echo "************************************************************"
echo "* SKCMS-1311: Inactivate all bids that should no longer be available *"
echo "************************************************************"
echo ""

source $CARMUSR/bin/carmenv.sh
result=`sqlcp "update bids
set invalid=SYSTIMESTAMP 
where bidtype in ('time_off','leg_duration','stop','pairing_length','check_in','check_out','combination','consecutive_days_off', 'string_of_days_off', 'f4_weekend_off_fd_crj', 'consecutive_days_at_work', 'f4_weekend_off_cc', 'f4_weekend_off_fd','flight') 
and invalid is null"`
echo $result


