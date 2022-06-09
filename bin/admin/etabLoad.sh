#!/bin/sh
# $Header$
#
# Script to load data from etables into an already existing schema. The data need to 
# match the existing sctructures in the database.
#
# Org: Björn Samuelsson, Jeppeson, 20060616
#

help_text() {
    echo "Loads data to DB"
    echo "Arguments:"
    echo "-i path to imput file(s) (required)"
    echo "Path can be just one file or dir if there is several input files"
    echo "-s schema (optional) if missing uses values from etc/global_SITE.xml"
    exit
}

while getopts s:i: opts
do
  case "$opts" in
      s) _schema=$OPTARG
          ;;
      i) _input=$OPTARG
          ;;
      *) help_text
          ;;
  esac
done

if [ -z "$_input" ];
then
    echo "ERROR: input do specified"
    help_text
fi



#
# Assume that the script is located in the carmusr get abolute path
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
# Source the carmenv configuration file. Will set
# all other CARMXXX variables
#
. $CARMUSR/bin/carmenv.sh

if [ -z "$_schema" ]
then
    _carm_db_conn=`xmlconfig db/connect | head -n 1 | awk '{ print $NF }'`
    _schema=`xmlconfig db/schema | head -n 1 | cut -d ' ' -f 3`
else
    _carm_db_conn=`xmlconfig db/connect | head -n 1 | awk '{ print $NF }'`
fi
#
# Import data
#
echo "Import etab data to schema ${_schema} in ${_carm_db_conn}... "

$CARMSYS/bin/carmrunner etabdiff -c ${_carm_db_conn} -s $_schema -a -n $_input

echo "...done. Imported etables found in ${_input} to database ${_schema}"
