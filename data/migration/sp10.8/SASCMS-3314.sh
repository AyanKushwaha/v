#!/bin/bash
echo "    * Running `basename $BASH_SOURCE`"
source `dirname $0`/migrate_single_table.sh

migrate_table meal_airport 8