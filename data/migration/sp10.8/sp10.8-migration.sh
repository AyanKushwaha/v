#!/bin/sh
#
# This script performs migration related model changes for SP10.8
#
# Included migrations:
# SASCMS-3314 table meal_airport
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`

echo "********************************************"
echo "SP 10.8 Migration script"
echo "********************************************"

echo " - Setting up ..."

. $CARMUSR/bin/carmenv.sh

cd $CARMUSR/data/migration/sp10.8

echo " - Processing migration tasks"

. $CARMUSR/data/migration/sp10.8/SASCMS-3314.sh
. $CARMUSR/data/migration/sp10.8/SASCMS-3367.sh

echo ""
echo "Upgrade finished successfully!"

