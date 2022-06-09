#!/bin/sh
# @(#) $Header: /opt/Carmen/CVS/sk_cms_user/bin/admin/fix_oracle_index.sh,v 1.1 2009/05/28 06:34:30 sandberg Exp $

script=`basename $0`
whereami=`pwd`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
cd $whereami

. $CARMUSR/etc/carmenv.sh


fix_index () {
    $CARMSYS/bin/carmpython <<__end_index__
from carmensystems.dave import DMF
def add_index(index_sql, index_name):
    try:
       conn = DMF.Connection("${conn}")
       conn.begin()
       conn.rexec(index_sql, None)
       conn.commit()    
       conn.endQuery()
       conn.close()
       print "\nCreated index %s" % (index_name)
    except RuntimeError, e:
       if "Reader::vstmt OCIStmtExecute(...)=OCI_ERROR: ORA-00955: name is already used by an existing object" in str(e):
           print "Index %s already exists in the database" % (index_name)
       else:
           raise e

afd_index_name = 'IDX_CARMUSR_ROTSEARCH'
afd_index = 'create index %s on ${_schema}.aircraft_flight_duty(rot_udor, ac)' % (afd_index_name)

cuf_index_name = 'IDX_CARMUSR_CREWUSERFILTER'
cuf_index = 'create index %s on ${_schema}.crew_user_filter(filter, val)' % (cuf_index_name)

add_index(afd_index, afd_index_name)
add_index(cuf_index, cuf_index_name)

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


fix_index
