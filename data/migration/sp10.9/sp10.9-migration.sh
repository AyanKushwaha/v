#!/bin/sh
#
# This script performs migration related model changes for SP10.9
#
# Included migrations:
# SASCMS-2537 table dig_string patterns
#

script=`basename $0`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`

echo "********************************************"
echo "SP 10.9 Migration script"
echo "********************************************"

echo " - Setting up ..."

. $CARMUSR/etc/carmenv.sh

cd $CARMUSR/data/migration/sp10.9

echo " - Processing migration tasks"

. $CARMUSR/data/migration/sp10.9/SASCMS-3241.sh

echo ""
echo "Upgrade finished successfully!"
