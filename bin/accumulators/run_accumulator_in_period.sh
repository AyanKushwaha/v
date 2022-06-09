#!/bin/sh
#
# Run a single accumulator over a period of time. 
# accumulator.sh only runs prev month and + 2 months 
# for any given month. This script will run accumulators.sh
# with a specific accumulator in mind over a specified period
#

script=`basename $0`
whereami=`dirname $0`
usage="usage: $script [-f] [-t] [accumulator_name]"

error ( )
{
    echo "$script: ERROR: $*" 1>&2
    echo "'$script -h' for help" 1>&2
    exit 2
}

get_carmusr ( )
{
    (
        cd "$whereami"
        while [ `pwd` != '/' -a ! -d "crc" ]
        do 
           cd ..
        done
        pwd 
    )
}

print_usage ( )
{
    cat <<__tac__
$usage

OPTIONS
    -h              Print this help

    -f              Required: Accumulate from this date. Works with formats 1Jan2018 , 20180101, 2018-01-01 etc

    -t              Required: Accumulate until this date. Works with formats 1Jan2018 , 20180101, 2018-01-01 etc

    -n              Required: Name of the accumulator to use. name needs to formatted as 'accumulators.your_accumulator_name'

All arguments are required for the script to work. Given date arguments and name this script will then call
'accumulators.sh -t FROM_DATE -s ACCNAME specific' multiple times to accumulate values over a longer period.
__tac__
}

# OPTIONS
FROM=
TO=
ACCNAME=

while getopts hf:t:n: flag
do
    case "$flag" in
         h) print_usage; exit 1;;
         f) FROM=$OPTARG;;
         t) TO=$OPTARG;;
         n) ACCNAME=$OPTARG;;
    esac
done
shift `expr $OPTIND - 1`

if [[ -z "$FROM" ]]; then
    error "From date must be specified (format '20180110')"
    exit 1
elif [[ -z "$TO" ]]; then
    error "To date must be specified (format '20180110')"
    exit 1
elif [[ -z "$ACCNAME" ]]; then
    error "An accumulator must be specified in order to run the script"
    exit 1
fi

: ${CARMUSR:="`get_carmusr`"}
export CARMUSR

validate_date ( ) 
{
   if [[ -z "$1"  ]] || [[ $1 =~ ^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]  ]]; then
      error "Date '$1' was not specified correctly (i.e '20180110')"
      exit 2
   else 
      echo "'$1' was correctly specified. " 
   fi
} 

# Validation of dates
FROM_DATE=$(date "+%Y%m%d" -d "$FROM")
validate_date "$FROM_DATE"
TO_DATE=$(date "+%Y%m%d" -d "$TO")
validate_date "$TO_DATE"


while [[ "$FROM_DATE" -le "$TO_DATE" ]];
do 
   echo "$FROM_DATE is lower than $TO_DATE"
   echo "Running $ACCNAME with date $FROM_DATE"
   . `$CARMUSR/bin/accumulators/accumulator.sh -t $FROM_DATE -s $ACCNAME specific`  
   FROM_DATE=$(date "+%Y%m%d" -d "$FROM_DATE +90 days")
done

 
