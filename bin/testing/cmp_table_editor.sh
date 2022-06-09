#!/bin/sh

if [ $# != 3 ]; then
  echo "Usage: bin/testing/cmp_table_editor.sh Modelserver Schema database" 
  echo "(modelserver ex: http://placerville:6714)"
  echo "(schema ex: manpower_nv_test)"
  echo "(database ex: oracle:manpower_nv_test/manpower_nv_test@flm/GPD01DEV)"
  exit 0
fi

#
# Assume that the start script is located in the carmusr get abolute path
# by assuming that a crc directory exist at the top level
#
cd `dirname $0`
while [ `pwd` != '/' -a ! -d "crc" ]
do
  cd ..
done

SERVER=$1
SCHEMA=$2
DB=$3

#
# Set the CARMUSR path.
#

CARMUSR=`pwd`

SK_APP=Manpower
export SK_APP

. $CARMUSR/etc/carmenv.sh

shift
echo "Starting system, directories:"
echo "CARMUSR:   $CARMUSR"
echo "CARMDATA:  $CARMUSR"
echo "CARMSYS:   $CARMSYS"
echo "CARMTMP:   $CARMTMP"
echo ""

java -jar $CARMSYS/lib/classes/tableeditor-all.jar -c $DB -s $SCHEMA -d $SERVER/RPC2 -P "forms.splash=false" -P "wave.baseuri=$SERVER/sys/manpower/forms/"

