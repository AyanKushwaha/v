#!/bin/sh
#
# Wrapper script to prune a schema from the database
# using the CARMSYS PruneSchema python file.
#
# Org, Björn Samuelsson, Carmen Systems AB 20060522
#

usageText() {
  echo "Usage: "`basename $0`" [-f] <schema1> <revision>"
  echo "   -f   : force prune. No confirmation required."
  echo "Removes all data from revisions after <revision>"
  exit 0
}

interactive=true

while getopts f option
do
    case "$option" in
	f) interactive=false;;
	*) usageText;;
    esac
done

#
# Shift away all used commands.
#
shift `expr $OPTIND - 1`

[ $# -ne 2 ] && usageText

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

schema=$1
rev=$2

SCHEMA_CONNECT_STRING=oracle:$schema/$schema\@${DATABASE#*\@}

$CARMUSR/bin/admin/getMaxRevisionId.sh $schema

ASK_ANSWER=yes
if [ $interactive == true ] ; then
  echo -n "Prune schema: $schema to revid: $rev (yes/no)? "
  read ASK_ANSWER ASK_JUNK
  : ${ASK_ANSWER:=N}
fi

case "$ASK_ANSWER" in
  [yY]*)
    echo "Pruning ${schema} to revision ${rev}..."
    $CARMRUNNER dave_prune_schema -c $SCHEMA_CONNECT_STRING -s $schema -C $rev -R published_roster:pubcid
    echo "Pruning ${schema} to revision ${rev}...done."
    ;;
esac
