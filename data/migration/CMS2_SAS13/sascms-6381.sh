#!/bin/sh

echo ******* Updating patch_type_set table with data required for run of course unrelease feature *******
etabdiff -s $SCHEMA -c $DATABASE $CARMUSR/data/manpower/migration/settings/patch_type_set.etab -a 
