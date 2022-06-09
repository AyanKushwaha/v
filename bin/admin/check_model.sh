#!/bin/sh
#
# Wrapper to the CARMSYS script dave_model_check to perform checks on the database
# 
# Usage: check_model.sh [constraint type ...] - Specify constraint types as arguments
# Usage: check_model.sh  - No args. Check all constraint types
#

ALL_AVAILABLE_CONSTRAINT_TYPES="domain \
                                ref \
                                unique \
                                validity_period \
                                check \
                                revision \
                                next_unique \
                                next_forward \
                                branch \
                                dave_up_tab \
                                data \
                                commitid \
                                prev_revid \
                                next_revid \
                                meta"

CONSTRAINT_TYPES_TO_CHECK=${@:-${ALL_AVAILABLE_CONSTRAINT_TYPES}}


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

. ${CARMUSR}/bin/carmenv.sh


umask 0002

XMLCONFIG=${CARMSYS}/bin/xmlconfig 
DB_CONN_STR=$(${XMLCONFIG} db/connect | cut -d ' ' -f 3 | head -1)
SCHEMA=$(${XMLCONFIG} db/schema | cut -d ' ' -f 3 | head -1)

LOGDIR=${CARMTMP}/logfiles/dave_model_check/$(date +'%Y%m%d')
mkdir -p ${LOGDIR}

for TYPE in ${CONSTRAINT_TYPES_TO_CHECK}
do
    LOGFILENAME=dave_model_check_${TYPE}_$(date +%Y%m%d.%H.%M.%S).log
    LOGFILE=${LOGDIR}/${LOGFILENAME}
  
    echo "---- $(date +'%Y-%m-%d %H:%M:%S') - Start checking type: ${TYPE} ----"
    echo "Running command: ${CARMSYS}/bin/carmrunner dave_model_check --verbose --connect=${DB_CONN_STR} --schema=${SCHEMA} --listmax=-1 --types=${TYPE}"
    echo "Output is stored in file ${LOGFILE}!"

    echo "Command: ${CARMSYS}/bin/carmrunner dave_model_check --verbose --connect=${DB_CONN_STR} --schema=${SCHEMA} --listmax=-1 --types=${TYPE}" >> ${LOGFILE} 2>&1
    echo "Date:    $(date +'%Y-%m-%d %H:%M:%S')"                      >> ${LOGFILE} 2>&1
    echo "Host:    $(hostname)"                                       >> ${LOGFILE} 2>&1
    echo "CARMUSR: ${CARMUSR}"                                        >> ${LOGFILE} 2>&1
    echo "----------------------------------------------------------" >> ${LOGFILE} 2>&1

    ${CARMSYS}/bin/carmrunner dave_model_check --verbose \
                                               --connect=${DB_CONN_STR} \
                                               --schema=${SCHEMA} \
                                               --listmax=-1 \
                                               --types=${TYPE}  >> ${LOGFILE} 2>&1

    echo "---- $(date +'%Y-%m-%d %H:%M:%S') - Done checking type: ${TYPE} ----"
    echo ""

done



#Usage: dave_model_check [options...]
#
#This script validates data in a DAVE database schema
#against a set of data integrity constraints.
#
#Version: DAVE.METADATA.MODELCHECK 61.02
#
#Note:
#The following options are ***NOT YET SUPPORTED***:
#[-M commitid]
#
#Options:
#  --version             show program's version number and exit
#  -h, --help            show this help message and exit
#  -v, --verbose         Verbose output
#  -c CONN, --connect=CONN
#                        Database connect string
#  -s SCHEMA, --schema=SCHEMA
#                        Database schema
#  -C CARMSYS, --carmsys=CARMSYS
#                        Location of CARMSYS [default: $CARMSYS]
#  -L LISTMAX, --listmax=LISTMAX
#                        How many items in lists to print; negative = no limit
#  -B BRANCH, --branch=BRANCH
#                        Which branch to use (default = 1). 0 implies check all
#                        branches.
#  -E ENTITIES, --entities=ENTITIES
#                        Which entities to check (comma-list, default = all)
#  -T TYPES, --types=TYPES
#                        Which constraint types to check (comma-list, default =
#                        validity_period,check,unique,revision,ref). Available
#                        types are (all,meta,revision,prev_revid,next_revid,nex
#                        t_unique,next_forward,branch,dave_up_tab,data,ref,chec
#                        k,domain,unique,validity_period,commitid)
#  -M COMMITID, --commitid=COMMITID
#                        Which revision (Max Commit ID) to check (default =
#                        latest)
#  -f FILENAME, --filename=FILENAME
#                        Additional constraints files (comma-list of relative
#                        or absolute file names, default = none)
#  -d DIRECTORIES, --directories=DIRECTORIES
#                        Additional constraints directories (comma-list of
#                        absolute paths, default = none)
#  -S, --SQL             Print SQL, don't execute
#
