#This migration script updates the baseline for crew accounts to 31Dec2010.

echo "* SASCMS-5353: Updating baseline for crew accounts to 31Dec2010"

DATE="31Dec2010"

$CARMSYS/bin/mirador -s carmusr.AccumulateBaseLine main $DATE
