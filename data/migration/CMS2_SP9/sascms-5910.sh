#!/bin/sh

echo ******** Update data into minimum_connection *******
etabdiff -s $SCHEMA -c $DATABASE $CARMUSR/data/migration/CMS2_SP9/minimum_connection.etab -a
