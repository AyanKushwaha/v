#!/bin/bash
echo "    * Running `basename $BASH_SOURCE`"
echo "    ************************************"
echo "     This script will migrate the table"
echo "     apt_restriction by copying a model"
echo "     to drop the current version and"
echo "     running updateschema, then copying"
echo "     back the correct version and"
echo "     run updateschema again. This will"
echo "     add the new version of the table."
echo "    ************************************"

source `dirname $0`/migrate_single_table.sh

migrate_table apt_restrictions