#!/bin/sh
#
# Wrapper script to prune a schema from the database
# using the python file in the same directory.
#
# Org, Björn Samuelsson, Carmen Systems AB 20060522
#

if [ $# -lt 1 ]
then
  echo "Usage: "`basename $0`" <schema>"
  echo "Get's the id for the latest revision in the database."
  exit 0
fi

#
# Assume that the start script is located in the carmusr, get abolute path
# by assuming that a crc directory exist at the top level
#
cd `dirname $0`
while [ `pwd` != '/' -a ! -d "crc" ]
do
  cd ..
done

#
# Set the CARMUSR path.
#
CARMUSR=`pwd`

#
# Source the carmenv configuration file. Will set all other
# CARMXXX variables and sourch the CONFIG_extension files.
#
. $CARMUSR/bin/carmenv.sh

echo "CARMSYS=$CARMSYS"

schema=$1
SCHEMA_CONNECT_STRING=oracle:$schema/$schema\@${DATABASE#*\@}
echo $SCHEMA_CONNECT_STRING

echo "Running getMaxRevisionId..." 
$CARMSYS/bin/carmpython carmensystems/dave/tools/MaxCommitId.py -c $SCHEMA_CONNECT_STRING -s $schema
echo "Running getMaxRevisionId...done." 
