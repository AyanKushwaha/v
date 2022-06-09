#! /bin/sh

function usage() {
    echo "Compiles the ruleset for given application"
    echo "Usage: `basename $0` [-e|-p] [-l] [-r suffix] application...|all"
    echo "      -h             : print this help text"
    echo "      -e             : compile with -explorer"
    echo "      -p             : compile with -profiler"
    echo "      -l             : compile on local machine"
    echo "      -r suffix      : compile rulset with suffix in name"
    echo "      application    : rot, ccp (or pfc|pcc), ccr (or rfc|rcc), cct, cmp and pre"
    echo "      all            : alias for applications rot, ccp, ccr, cct, pre and cmp"
}

compiler_flag=" --explorer=False"
local_flag=" --local=False"
suffix=""
suffix_option=" --suffix="${suffix}
while getopts heplr: option 
do
    case "$option" in
    h) usage && exit 0
        ;;
    e) compiler_flag=" --explorer=True"
	    ;;
	p) compiler_flag=" --profiler=True"
	    ;;
	l) # Used by CARMSYS/bin/rave_compile to compile locally
        local_flag=" --local=True"
	    ;;
	r)  suffix=${OPTARG}
	    suffix_option=" --suffix=${suffix} "
	    ;;
    *) usage && exit 1
	    ;;
    esac
done

shift `expr $OPTIND - 1`

if [ $# = 0 ]; then 
    usage
    exit 1
fi

# Sets the CARMUSR variable. 
if [ -z "$CARMUSR" ]; then
    cd `dirname $0`
    a=`pwd`
    while [ `pwd` != '/' -a ! -d "crc" ]; do
	cd ..
    done
    CARMUSR=`pwd`
    export CARMUSR
    cd $a
fi

    rule_types=$*
        echo $CARMUSR"/bin/cmsshell rave compile" ${rule_types}${compiler_flag}${local_flag}${suffix_option}
        "$CARMUSR/bin/cmsshell" rave compile ${rule_types}${compiler_flag}${local_flag}${suffix_option}