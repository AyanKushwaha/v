#!/bin/sh
echo "************************************************************"
echo "* SKCMS-1385 Inactivate all bids that should no longer be available *"
echo "************************************************************"
echo ""

source $CARMUSR/bin/carmenv.sh
result=`sqlcp "update bids
set invalid=SYSTIMESTAMP 
where bidtype='stop' and invalid is null and createdby in (select userid from usergroups where groupid=5)"`
echo $result


