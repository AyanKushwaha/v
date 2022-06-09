#!/bin/bash

{
echo "$(date +%FT%T) Starting crew data export..."
${CARMUSR}/bin/bids/generateCrewDataExport.sh

echo "$(date +%FT%T) Removing future bid periods..."
_DB_LOC="`echo $DB_CP_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";
sqlplus -S $_DB_LOC <<EOF ;
DELETE FROM periods
WHERE opendate > CURRENT_DATE ;
EOF

echo "$(date +%FT%T) Starting RP carryover preassignment generation..."
${CARMUSR}/bin/bids/generatePreassignmentFiles.sh


echo "$(date +%FT%T) Crew Portal export finished."
} | tee -a ${CARMTMP}/logfiles/cmd_crew_portal_export.log.$(date +%FT%T)
