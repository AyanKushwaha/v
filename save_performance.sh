DATE=$1
HOST=$2

if [ -z $DATE ]; then
  DATE=`date '+%Y%m%d'`
fi
grep -i "Save Plan Times" current_carmtmp_cct/logfiles/*$DATE*$HOST* -A 1 | grep -i "Total" | awk -F' ' '{sum+=$3} END {print "Average = ",sum/NR}'
