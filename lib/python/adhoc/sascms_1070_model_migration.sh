#!/bin/sh
# @(#) $Header$


# This script will attempt to change the length of a text field in the database to 150 charachters.

script=`basename $0`
whereami=`pwd`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
cd $whereami

. $CARMUSR/etc/carmenv.sh

fix_model () {
    $CARMSYS/bin/carmpython <<__end_index__
from carmensystems.dave import dmf 

def run_sql(sql_statement):
   try:
      conn = dmf.Connection("${conn}")
      conn.begin()
      conn.rexec(sql_statement, None)
      conn.commit()    
      conn.endQuery()
      conn.close()
      print "Executed sql:", sql_statement
   except RuntimeError, e:
      if "Reader::vstmt OCIStmtExecute(...)=OCI_ERROR: ORA-00955: name is already used by an existing object" in str(e):
         print "Index %s already exists in the database" % (index_name)
      else:
         raise e

maintable_sql = 'alter table ${_schema}.crew_training_need modify si VARCHAR2(150 CHAR)'
temptable_sql = 'alter table ${_schema}.crew_training_need_tmp modify si VARCHAR2(150 CHAR)'

run_sql(maintable_sql)
run_sql(temptable_sql)

__end_index__
}

_schema=$DB_SCHEMA
while getopts s:h flag
do
    case "$flag" in
        s) _schema="$OPTARG";;
        h) print_usage; exit 0;;
    esac
done

shift `expr $OPTIND - 1`
conn=`echo $DATABASE | sed "s%^\([^:]*\):\([^@]*\)@\(.*\)$%\1:$_schema/$_schema@\3%"`

echo "Connection string: $conn"
echo "Schema: $_schema"
# Run the actuall fixing
fix_model

