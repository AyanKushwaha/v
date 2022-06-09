#!/bin/sh
# @(#) $Header: /opt/Carmen/CVS/sk_cms_user/bin/populateFilterTabs.sh,v 1.8 2010/01/27 10:58:17 ade407 Exp $
# Script to load all DaveFilters
# Script assumes it is located in CARMUSR/bin

usage_text() {
    echo "Usage: `basename $0` schema_name schema_password"
    exit
}

[ $# -ne 2 ] && usage_text

script=`basename $0`
whereami=`pwd`

cd `dirname $0`/..
while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
done
CARMUSR=`pwd`
cd $whereami

plan_name=$1
plan_passwd=$2
shift;shift

. $CARMUSR/bin/carmenv.sh
# change user
SCHEMA_CONNECT_STRING=`echo $DATABASE | sed "s%^\([^:]*\):\([^@]*\)@\(.*\)$%\1:$plan_name/$plan_passwd@\3%"`

populate ( ) {
    $CARMSYS/bin/carmrunner etabdiff -c $SCHEMA_CONNECT_STRING -s $plan_name $2 -a -n $1
}

populate_if_match ( ) {
    while read line flag
    do
        pop_arg=""
        [ -z "$flag" ] && pop_arg="-f $CARMUSR/bin/etabconfig.xml"

        if [ $# -gt 0 ]
        then
            for etab in ${1+"$@"}
            do
                [ `basename $line .etab` = $etab ] && populate $line "$pop_arg"
            done
        else
            populate $line "$pop_arg"
        fi
    done
}

# Everything added to this section will make the databse entry
# look exactly the same as the etab stated here
cat <<__END_OF_LIST__ | sed 's/#.*$//;/^[ 	]*$/d' | populate_if_match ${1+"$@"}
#######################################################
# INSTRUCTIONS:                                       #
# Fill in new tables, one per row with absolute path. #
# DO NOT REMOVE THE '__END_OF_LIST__' marker!         #
#######################################################

##################
# UDM core etabs #
##################
$CARMUSR/current_carmsys_cmp/data/config/models/udmAirManpower/master/dave_entity_filter.etab
$CARMUSR/current_carmsys_cmp/data/config/models/udmAirManpower/master/dave_filter_ref.etab
$CARMUSR/current_carmsys_cmp/data/config/models/udmAirManpower/dave_selection.etab
$CARMUSR/current_carmsys_cmp/data/config/models/udmAirManpower/dave_selparam.etab

$CARMSYS/data/config/models/udm_air1/dave_selection.etab ONLY_ADD
$CARMSYS/data/config/models/udm_air1/dave_selparam.etab ONLY_ADD
$CARMSYS/data/config/models/udm_air1/dave_entity_filter.etab ONLY_ADD

##################
#  DAVE filters  #
##################
$CARMUSR/crc/etable/initial_load/dave_selection.etab ONLY_ADD
$CARMUSR/crc/etable/initial_load/dave_selparam.etab ONLY_ADD
$CARMUSR/crc/etable/initial_load/dave_entity_filter.etab ONLY_ADD
$CARMUSR/crc/etable/initial_load/dave_filter_ref.etab ONLY_ADD

__END_OF_LIST__
PYTHONPATH=$CARMSYS/lib/python/carmensystems/mave/gm/compat:$PYTHONPATH
echo PYTHONPATH:$PYTHONPATH

$CARMUSR/bin/startMirador.sh --script -s carmdata.SetupSingleEntityFilters -s $plan_name -c $SCHEMA_CONNECT_STRING 

$CARMUSR/bin/updateCrewUserFilter.sh "cmp" $plan_name $SCHEMA_CONNECT_STRING #Update cmp-filter defs


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
