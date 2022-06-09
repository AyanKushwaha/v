#!/bin/sh
# $Header$
#
#  Sometimes it is useful to create etables on file from database content.
#  This might be needed when you want to move information, look at it using
#  text edtors or other tools etc.
#
#  The core functionality exists in the CARMSYS used, and this script will
#  fetch all the additional needed information from the configuration.
#
#  The user is required to specify the schema to be used as well as the output
#  directory. All tables will be written to the directory specified.
# 
#  The tool can also be used standalone.
#
# Org: Bj�rn Samuelsson, Jeppeson, 20060616
#

help_text() {
    echo "Dumps schema to etables"
    echo "Arguments:"
    echo "-t table name (required)"
    echo "If schema name is not spcified uses value from etc configuration file"
    exit
}

while getopts s:o:t: opts
do
  case "$opts" in
      t) _table=$OPTARG
	  ;;
      s) _schema=$OPTARG
    ;;
      *) help_text
	  ;;
  esac
done

if [ -z "${_table}" ];
then
    echo "ERROR: table name missing"
    help_text
fi

if [ -z "${_schema}"];
then
    echo "No schema specified... defaulting to ${DB_SCHEMA}"
    _schema=$DB_SCHEMA
    _url=$DB_URL
else
    echo "Schema specfied : ${_schema}..."
    _url=$DB_URL
    _url="$(echo $_url | sed "s/$DB_SCHEMA/$_schema/g")"
    echo "Url set to ${_url}"
fi
#
# Assume that the script is located in the carmusr get abolute path
# by assuming that a crc directory exist at the top level
#
_origpath=`pwd`
cd `dirname $0`
while [ `pwd` != '/' -a ! -d "crc" ]
do
  cd ..
done

#
# Set the CARMUSR path.
#
CARMUSR=`pwd`
cd $_origpath

#
if  [ -z "$CARMSYS" ]; then
	echo "CARMSYS is not defined. please run bin/cmsshell"
	exit 1
fi


config_file=$(mktemp)
cat > ${config_file} <<EOF
<?xml version="1.0" ?>
<etabdump version="0.7" defmode="ignore">
<map entity="${_table}" etab="${_table}"></map>
</etabdump>
EOF

echo "Export data from schema ${_schema} in ${_url}"
# echo "$(cat ${config_file})"
$CARMSYS/bin/carmrunner etabdump -c ${_url} -s ${_schema} -f ${config_file} .

