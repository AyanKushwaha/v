#!/bin/sh

script=`basename $0`
whereami=`dirname $0`
#usage="usage: $script [-h] -c for create, -C for Compare, -d for delete"
usage="usage: $script [-h] -c for create, -o for Compare"


delete=0
create=0
compare=0
num_opts=0
del_missing=0
etabdiff_extra_arguments=()
while getopts hdco flag
do
    case "$flag" in
        h) echo $usage; exit 0;;
        c) create=1;num_opts=$(($num_opts+1));;
        d) del_missing=1;;
        o) compare=1;num_opts=$(($num_opts+1));;
        '?') echo $usage; exit 2;;
    esac
done
shift `expr $OPTIND - 1`

echo "num_opts: $num_opts"
    if [[ $num_opts -gt 1 ]]
    then
        echo "Only allowed to do one operation at a time"
        exit
    fi
# Sets the CARMUSR variable, if it is not set
if [ -z "$CARMUSR" ]; then
    a=`pwd`
    cd `dirname $0`
    while [ `pwd` != '/' -a ! -d "crc" ]; do
	cd ..
    done
    CARMUSR=`pwd`
    export CARMUSR
    cd $a
fi


# Set CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
. $CARMUSR/bin/carmenv.sh


if [[ $schema == "" ]]
then
  schema=$DB_SCHEMA
  custconnect="$DB_URL"
else
  custconnect="oracle:${schema}/${schema}@$DB_NODE_URL"
fi

export LOG_FILE=${CARMTMP}/logfiles/mirador.${USER}.$(date '+'%Y%m%d.%H%M.%S).${HOSTNAME}
#if [[ $delete -gt 0 ]]
#then
#    exec $CARMSYS/bin/mirador -s carmusr.filter_tables.setup_filters delete_the_dave_filters 2>&1| tee -a $LOG_FILE
#    #exec $CARMSYS/bin/mirador -s carmusr.filter_tables.delete_filters 2>&1| tee -a $LOG_FILE
#fi

ETABS_PATH="$CARMUSR/crc/etable/dave_filter/*.etab"

if [[ $create -gt 0 ]]
then
    if [[ $del_missing == 1 ]]; then
        etabdiff_extra_arguments+=(-f "$CARMUSR/bin/admin/setup/etabdiff_delmissing_config.xml")
    fi

    etabdiff -na -c $custconnect -s $schema "${etabdiff_extra_arguments[@]}" $ETABS_PATH

fi
if [[ $compare -gt 0 ]]
then
    etabdiff -c $custconnect -s $schema $ETABS_PATH 2>&1
fi

