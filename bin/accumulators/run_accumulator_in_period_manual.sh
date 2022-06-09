#!/bin/sh
#
# Run a single accumulator over a period of time. 
# accumulator.sh only runs prev month and + 2 months 
# for any given month. This script will run accumulators.sh
# with a specific accumulator in mind over a specified per
#

FROM="20200801"
TO="20220302"

# Validation of dates
FROM_DATE=$(date "+%Y%m%d" -d "$FROM")
TO_DATE=$(date "+%Y%m%d" -d "$TO")


while [[ "$FROM_DATE" -le "$TO_DATE" ]];
do 
   echo "$FROM_DATE is lower than $TO_DATE"
   echo "Running $ACCNAME with date $FROM_DATE"
   `bin/accumulators/accumulator_manual.sh -t $FROM_DATE -s accumulators.sh_all_fc_flight_acc specific` || true  
   FROM_DATE=$(date "+%Y%m%d" -d "$FROM_DATE +90 days")
done

 
