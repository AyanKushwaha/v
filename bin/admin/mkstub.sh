#!/bin/sh
#
# Script to generate a stub of a new filebased plan based on an existing plan
#
# (c) Copyright Jeppesen Systems AB
#
# $Header: /opt/Carmen/CVS_REPOSITORY/Customization/ay_cms_user/bin/admin/mkstub.sh,v 1.6.4.7 2011/04/12 09:49:33 granlund Exp $
#
# Script to create the (sadly) needed files in the CARMDATA structure
#

#
# Some nice functions for error and interrupt handling
#
usage() {
  echo "Creates stubs for a new file based plan"
  echo "Usage: "`basename $0`" [-d <directory>] <schema_name>"
  exit 1
}

bailout() {
  echo $1
  exit $2
}

_cwd=`pwd`
trap 'cd $_cwd' 0 1 2 3 11 15

# To avoid file permission problems...
umask 002

_tracecmd=""

# Option handling
while getopts d: opts
do
    case "$opts" in
        d) NEW_DIR=$OPTARG  ;;
        *) usage ;;
    esac
done

# Shift away options
shift `expr $OPTIND - 1`

if [ "$#" -ne 1 ]; then
   usage
fi

# This script is located in the CARMUSR, get absolute path
# Assume that the start script is located in the carmusr get abolute path
# by assuming that a crc directory exist at the top level
#
_origin=`pwd`
cd `dirname $0`
while [ `pwd` != '/' -a ! -d "crc" ]
do
  cd ..
done
CARMUSR=`pwd`
export CARMUSR
cd $_origin

# CARMUSR setup
. ${CARMUSR}/bin/carmenv.sh

#
# Retrieve DB sid and DB host from configuration
#
#getconf "db/host1" > /dev/null
_dbhost1=`xmlconfig db/host1 | awk '{ print $NF }' | head -n 1`
_dbhost2=`xmlconfig db/host2 | awk '{ print $NF }' | head -n 1`
_dbport1=`xmlconfig db/port1 | awk '{ print $NF }' | head -n 1`
_dbport2=`xmlconfig db/port2 | awk '{ print $NF }' | head -n 1`
_dbprefix=`xmlconfig db/prefix | awk '{ print $NF }' | head -n 1`
_dbservicename=`xmlconfig db/servicename | awk '{ print $NF }' | head -n 1`

_PLAN=$1

# This prefix defines the sub path under $CARMDATA/LOCAL_PLAN, where the stubs are placed.
# Finnair has this defined in the xmlconfig property %(data_model/file_prefix)
# SAS has it in %(data_model/plan_dir)
#
#getconf "data_model/plan_dir" > /dev/null
_defaultprefix=`xmlconfig  data_model/plan_dir | awk '{ print $NF }' | head -n 1`

# If a new directory was provided on the command line we use this
#
[ "X${NEW_DIR}" != "X" ] && _newprefix=TestPlans/CMS/${NEW_DIR}

_fileprefix=${_newprefix:-"${_defaultprefix}"}
_lplanpath="$CARMDATA/LOCAL_PLAN/${_fileprefix}/${_PLAN}"

# Check if the subplan file structure we're about to create already exists
if [ -f "${_lplanpath}/${_PLAN}/subplanHeader" ]; then
  echo ""
  echo "*** WARNING! The 'subplanHeader' file:"
  echo "${_lplanpath}/${_PLAN}/subplanHeader    already exists!!!"
  echo "*** If you continue, you will use brute force to try to update this with new contents."
  echo "*** Among other things, the Database Connection string"
  echo "*** in the current 'subplanHeader' file will be replaced with:"
  echo "${_dbprefix}:${_PLAN}/${_PLAN}@${_dbhost1}:${_dbport1}%${_dbhost2}:${_dbport2}/${_dbservicename}"
  echo -n "Are you REALLY sure you REALLY want to do this (n)? "
  read yorn
  [ "$yorn" != "y" -a "$yorn" != "Y" ] && bailout "Aborting!"
  echo ""
  echo "You've been warned..."
  echo ""
fi

# Create CARMDATA directory structure
#
echo "Creating CARMDATA directory structure..."
mkdir -p "${_lplanpath}/${_PLAN}/etable/SpLocal/.BaseDefinitions" || bailout "Failed to create ${_lplanpath}/${_PLAN}/etable/SpLocal/.BaseDefinitions directory" 3
mkdir -p "${_lplanpath}/${_PLAN}/etable/SpLocal/.BaseConstraints" || bailout "Failed to create ${_lplanpath}/${_PLAN}/etable/SpLocal/.BaseConstraints directory" 4
mkdir -p "${_lplanpath}/etable/LpLocal" || bailout "Failed to create ${_lplanpath}/etable/LpLocal directory" 5

# Just now, we have gotten news that it is really important that this is correct. BS 20070817
echo "   Creating new localplan file..."
cat > "${_lplanpath}/localplan.tmp" << EOF
SECTION local_plan_header
557;LOCAL_PLAN_HEADER_KEY;LOCAL_PLAN_HEADER_CONNECTOR_KEY;LOCAL_PLAN_HEADER_NAME;LOCAL_PLAN_HEADER_COMMENT;LOCAL_PLAN_LAST_DB_READ;LOCAL_PLAN_LAST_LOG_READ;LOCAL_PLAN_STANDARD_OR_DATED;LOCAL_PLAN_RRL_VERSION;LOCAL_PLAN_SELECTION;LOCAL_PLAN_OAG_FPLN;LOCAL_PLAN_TRAFFICDAYTABLE;LOCAL_PLAN_HEADER_DB_PATH;
559;;;${_fileprefix}/${_PLAN};;05Apr2007 07:20;;DATED;70;Ctf2Rrl -i notused.ctf;;;${_PLAN}+${_dbprefix}:${_PLAN}/${_PLAN}@${_dbhost1}:${_dbport1}%${_dbhost2}:${_dbport2}/${_dbservicename};
SECTION net
124;NET_CODE;NET_FLIGHT_ID;NET_CREW_EMPLOYER;NET_GDOR;NET_START_TIME;NET_START_DATE;NET_END_TIME;NET_END_DATE;NET_ROTATION_NUM;NET_OPTION;NET_EMPNO_NO;NET_GROUP;NET_AREA;NET_DAY_NUM;NET_DEP_AIRP;NET_ARR_AIRP;NET_FREQ_ONLY;NET_ON_FREQ;NET_FIRST_CLASS_CAP;NET_BUSINESS_CLASS_CAP;NET_ECONOMY_CLASS_CAP;NET_REST_TIME_BV;NET_REST_TIME_LBA;NET_REST_TIME_MTV;NET_SPECIAL_REST_TIME;NET_SIS_VERSION_NUM;NET_STATUS;NET_AC_TYPE1;NET_AC_TYPE2;NET_AC_TYPE3;NET_AC_TYPE4;NET_FLEET1;NET_FLEET2;NET_FLEET3;NET_FLEET4;NET_IATA1;NET_IATA2;NET_IATA3;NET_IATA4;NET_IATA5;NET_QUAL1;NET_QUAL2;NET_MANUAL_CREW_COMP;NET_CALC_CREW_COMP;NET_CHANGED_CREW_COMP;NET_AC_OWNER;NET_CONFIG;NET_PBASE;NET_SIS_FP_ID;NET_USER_ID;NET_SIS_FP_ID_2;NET_SIS_VERSION_NUM_2;NET_START_TIME_2;NET_START_DATE_2;NET_END_TIME_2;NET_END_DATE_2;NET_AREA_TYPE;NET_CRR_TYPE;NET_MAIN_CAT;NET_REINF_CAB_CALC;NET_REINF_CAB_MAN;NET_REINF_COC_CALC;NET_REINF_COC_MAN;NET_SERVICE_TYPE;NET_SUFFIX;NET_TIME_BASE;NET_FILTER_DH;NET_GDP_VERSION_NUMBER;NET_GDP_ID;NET_GDP_VERSION_NUMBER_2;NET_GDP_ID_2;NET_GDP_START_TIME;NET_GDP_END_TIME;NET_GDP_START_TIME_2;NET_GDP_END_TIME_2;NET_GDP_START_DATE;NET_GDP_END_DATE;NET_GDP_START_DATE_2;NET_GDP_END_DATE_2;
125;;;;;0000;20070405;2359;20100405;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;GDOR;;;;;;;;;;;;;;
EOF
compress ${_lplanpath}/localplan.tmp
mv ${_lplanpath}/localplan.tmp.Z ${_lplanpath}/localplan

# Copy BaseConstraints and BaseDefinitions from CARMUSR
#
echo "   Copying BaseConstraints and BaseDefinitions..."
cp -r ${CARMUSR}/crc/etable/.BaseConstraints/* "${_lplanpath}/${_PLAN}/etable/SpLocal/.BaseConstraints/" 
cp -r ${CARMUSR}/crc/etable/.BaseDefinitions/* "${_lplanpath}/${_PLAN}/etable/SpLocal/.BaseDefinitions/" 

# Create subplanRules file
#
echo "   Creating subplanRules file..."
cat > "${_lplanpath}/${_PLAN}/subplanRules" << EOF
SECTION rules
_builtin.MasterRule on #D> on
<PARAMETERS>
<END>






EOF

# Create subplanHeader file
#
echo "   Creating subplanHeader file... "
cat > "${_lplanpath}/${_PLAN}/subplanHeader" << EOF
SECTION sub_plan_header
552;SUB_PLAN_HEADER_KEY;SUB_PLAN_HEADER_CONNECTOR_KEY;SUB_PLAN_HEADER_NAME;SUB_PLAN_HEADER_AGREEMENT;SUB_PLAN_HEADER_COMMENT;SUB_PLAN_HEADER_AREA;SUB_PLAN_HEADER_AIRLINE;SUB_PLAN_HEADER_CREW_COMPLEMENT;SUB_PLAN_HEADER_ASSIGN_COMPLEMENT;SUB_PLAN_HEADER_DUTY_TYPE;SUB_PLAN_HEADER_CITY;SUB_PLAN_HEADER_PLANNER;SUB_PLAN_HEADER_PREVIOUS_NAME;SUB_PLAN_HEADER_STATUS;SUB_PLAN_HEADER_PERIOD_START_1;SUB_PLAN_HEADER_PERIOD_END_1;SUB_PLAN_HEADER_PERIOD_START_2;SUB_PLAN_HEADER_PERIOD_END_2;SUB_PLAN_HEADER_PERIOD_START_3;SUB_PLAN_HEADER_PERIOD_END_3;SUB_PLAN_HEADER_START_PLANNING;SUB_PLAN_HEADER_RULE_SET_NAME;SUB_PLAN_HEADED_PPP_START;SUB_PLAN_HEADER_PPP_START;SUB_PLAN_HEADER_PPP_END;SUB_PLAN_HEADER_CREW_FILTER;SUB_PLAN_HEADER_RRL_VERSION;SUB_PLAN_HEADER_CRR_NO;SUB_PLAN_HEADER_CREW_PLAN;SUB_PLAN_HEADER_TAG_INFO;SUB_PLAN_HEADER_TAG_LEVEL_INFO;SUB_PLAN_HEADER_CREW_TAG_INFO;SUB_PLAN_HEADER_BASE_DEF_FILE_NAME;SUB_PLAN_HEADER_BASE_CONSTR_FILE_NAME;SUB_PLAN_HEADER_DB_PATH;
554;;;${_fileprefix}/${_PLAN}/${_PLAN};;;;;;;;HEL+;${USER};${_fileprefix}/${_PLAN}/${_PLAN};;20060814;20061019;;;;;07Sep2006 07:21;;20060814;20060814;20061019;5;210;8817;crew_data.etab;#0#USER_TAG_0#1#USER_TAG_1#2#USER_TAG_2#3#USER_TAG_3#4#USER_TAG_4#5#USER_TAG_5#6#USER_TAG_6#7#USER_TAG_7#8#USER_TAG_8#9#USER_TAG_9;#0#Default#1#Default#2#Default#3#Default#4#Default#5#Default#6#Default#7#Default#8#Default#9#Default;#0#USER_TAG_0#1#USER_TAG_1#2#USER_TAG_2#3#USER_TAG_3#4#USER_TAG_4#5#USER_TAG_5#6#USER_TAG_6#7#USER_TAG_7#8#USER_TAG_8#9#USER_TAG_9;DefaultBaseDefinitions;DefaultBaseConstraints;${_PLAN}+${_dbprefix}:${_PLAN}/${_PLAN}@${_dbhost1}:${_dbport1}%${_dbhost2}:${_dbport2}/${_dbservicename};
EOF

echo "Done"
