#!/bin/sh
#
# Script to import a CMS DB schema using Oracle Data Pump's Import functionality 
#
# (c) Copyright Jeppesen Systems AB
#
#
# Some nice functions for error and interrupt handling
#

_tracecmd="time"
_logfile=oradp_import_`date '+%Y%m%d_%H%M%S%Z'`.log
_cwd=`pwd`
unset _use_imp > /dev/null 2>&1

usage() {
  echo ""
  echo "Imports a schema using the Oracle Data Pump impdp command"
  echo "Usage: "`basename $0`" [-p n] [-b] [-a] [-o] [-s] [-f] [-O] [-D]"
  echo "                     [-d <dpump_directory>] [-C <ezconnect_string>] [-t]"
  echo "                     <exported_schema_name> <new_schema_name> <dumpname>"
  echo ""
  echo "       where:  "
  echo "       -   <exported_schema_name> is the name of the exported schema"
  echo "       -   <new_schema_name> is the new schema name for the import"
  echo "       -   <dumpname> is the name of the exported dumpfile set, "
  echo "           e.g. 'cms_production_1_20071120_095253UTC'"
  echo "       -   <dpump_directory> is the Oracle name of the directory"
  echo "           where the dumpfile set is located, e.g. 'dpump_dir'"
  echo "       -   <ezconnect_string> is the Oracle Easy (EZ) Connect string"
  echo "           for an Oracle user with privileges to create a Dave" 
  echo "           user/schema and to grant directory read/write privileges"
  echo "           on the Data Pump directory for the new Dave user/schema,"
  echo "           e.g. 'carmdba/tralala@orahost:1521/gpd77dev'"
  echo "           or 'system/blabla@orahost2/gtn99tst'"
  echo ""
  echo "  -p n Use n parallel threads for import job."
  echo "       The default is 2 for Oracle 10g Enterprise Edition,"
  echo "       otherwise 1, and the maximum is 6,"
  echo "       Make sure you don't use anything higher"
  echo "       than 2 unless you're sure it won't affect a production"
  echo "       system's performance!"
  echo "  -b   Run export as batch job without user interaction."
  echo "  -a   Use alternative RAC node first"
  echo "  -o   Use old style 'import'"
  echo "  -s   Gather statistics after import"
  echo "  -f   Force. Use this to allow <exported_schema_name>=<new_schema_name>"
  echo "  -O   Run DMOptimize to e.g. gather statistics after import."
  echo "       NB. Disabled for 'carmdba' user for Beta 4 and some"
  echo "       other old versions."
  echo "       Will run an ordinary statistics gathering job (as for -s)"
  echo "       if this is the case!"
  echo "  -D   Drop <new_schema_name> before importing."
  echo "  -d   Use the Oracle directory <dpump_directory>"
  echo "       This directory must exist in Oracle and"
  echo "       be readable for the Oracle user (schema owner)"
  echo "  -C   Use <ezconnect_string> as (Easy) Connect string for impdp/imp"
  echo "       instead of default retrieved from configuration. If it isn't"
  echo "       possible to retrieve a default from the configuration this"
  echo "       is a *required* option."
  echo "       NB: The connect string has to be for a user with privileges"
  echo "       to create new Dave/FLM_DATA users"
  echo "  -t   Import tables only, do not create new schema or indexes. Assumes that there is schema."
  exit 1
}

bailout() {
  cd $_cwd
  # Cleanup
  if [ -f "${CARMTMP}/logfiles/${_logfile}" -a ! -s "${CARMTMP}/logfiles/${_logfile}" ]; then
    rm "${CARMTMP}/logfiles/${_logfile}"
  fi
  echo $1
  exit $2
}

errbailout() {
  cd $_cwd
  # Cleanup
  if [ -f "${CARMTMP}/logfiles/${_logfile}" -a ! -s "${CARMTMP}/logfiles/${_logfile}" ]; then
    rm "${CARMTMP}/logfiles/${_logfile}"
  fi
  echo $1
  usage
  exit $2
}

check_names() {
  if [ "${_expschema}" = "${_newschema}" -a -z "$1" ]; then
    # Not allowed to have identical names fithout '-f'
    bailout "Not allowed: Exported schema name and new schema name identical!" 8
  fi
}

handle_params() {
  # Get the command line options and take actions
  #
  while getopts p:boasfODd:C:t opts
  do
    case "$opts" in
      p) _parallel=$OPTARG 
         ;;
      b) _batch=1 
         ;;
      o) _use_imp=1 
         ;;
      a) _use_althost=1
         ;;
      s) _gather_stats=1
         ;;
      f) _force=1
         ;;
      O) _run_dmopt=1
         ;;
      D) _drop_schema=1
         ;;
      d) _arg_dpumpdir=$OPTARG
         ;;
      C) _arg_ezdbaconnect=$OPTARG
         ;;
      t) _tables_only=1
         ;;
      *) usage
         ;;
    esac
  done

  # Shift away options
  shift `expr $OPTIND - 1`

  if [ "$#" -ne 3 ]; then
    usage
  else
    _expschema=$1
    _newschema=$2
    _dumpname=$3
    check_names ${_force} 
  fi
}

check_valid_ora() {
  # Oracle server or Oracle client?
  #
  _uname=`uname -n`
  [ -r /etc/oratab -o `expr match $_uname 'csc7'` -ne 0 ] || bailout "No /etc/oratab found and no known Oracle client installation, quitting!" 1
}

setup_carmenv() {
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
  [ `pwd` = '/' ] && bailout "Error>>> No CARMUSR found!" 9
  CARMUSR=`pwd`
  export CARMUSR
  cd $_origin
  
  # Workaround to try to run on hosts without a properly installed
  # CARMUTIL
  _carmutil=carmutil17
  if rpm -V "${_carmutil}" >/dev/null 2>&1; then
    # CARMUSR setup
    . ${CARMUSR}/bin/carmenv.sh
  
  else
    if [ -h $CARMUSR/current_carmsys_cct ]; then
      CARMSYS=${CARMUSR}/current_carmsys_cct
    elif [ -h $CARMUSR/current_carmsys ]; then
      CARMSYS=${CARMUSR}/current_carmsys
    else
      errbailout "ERROR>>> No CARMSYS link found!" 12
    fi
    PATH=${CARMUSR}/bin:${CARMSYS}/bin:$PATH
    PYTHONPATH=${CARMUSR}/lib/python:${CARMSYS}/lib/python:$PYTHONPATH
    CARMTMP=/tmp
    if [ -z "$SITE" ] 
    then
      _domainname=`domainname`
      if [ "X$_domainname" = "Xypcarmen" ]; then
 	SITE=Carmen
      elif [ "X$_domainname" = "Xtestnet" ]; then
        SITE=Testnet
      elif [ "X$_domainname" = "Xypimpl" ]; then
        SITE=Implnet
      elif [ "X$_domainname" = "Xacademy" ]; then
        SITE=Academy
      elif [ "X${_domainname}" = "Xypsupport" ]; then 
        SITE=Support
      else
        SITE=SAS
        # SUBSITES are 'PROD', 'LIVETEST', 'TEST' and DLYTEST
        SUBSITE=MUST_BE_DEFINED
      fi
    fi
    export PATH PYTHONPATH CARMSYS CARMTMP SITE
    [ -d "${CARMTMP}/logfiles" ] || mkdir ${CARMTMP}/logfiles
  fi
}

set_db_params() {
  # Retrieve DB information from configuration
  #
  _dbauser=`xmlconfig db/adm/schema 2>/dev/null | head -n 1 | awk '{ print $NF }'`
  _dbapwd=`xmlconfig db/adm/password 2>/dev/null | head -n 1 | awk '{ print $NF }'`
  _dbschema=`xmlconfig db/schema 2>/dev/null | head -n 1 | awk '{ print $NF }'`
  # Used by DMOptimize
  _daveconnect=`xmlconfig db/adm/connect 2>/dev/null | awk '{ print $NF }'`
  # Use schema from config as placeholder/default
  _schema=${_dbschema}

  # The instance name in both lower- and uppercase is used
  # for lookup in /etc/oratab
  _dbsid=`xmlconfig db/servicename 2>/dev/null | awk '{ print $NF }'`
  # WA for missing servicename in config
  if [ "X${_dbsid}" = "X" ]; then
    _dbsid=`xmlconfig site/db/sid 2>/dev/null | awk -F= '{ print $NF }'`
  fi
  # Uppercase version of the instance/SID
  _dbsid_uc=`echo "${_dbsid}" | tr 'a-z' 'A-Z'`

  # Retrieve the hostname of the first RAC node
  _dbhost1=`xmlconfig db/host1 2>/dev/null | awk '{ print $NF }'`
  # Retrieve the hostname of second RAC node as well
  _dbhost2=`xmlconfig db/host2 2>/dev/null | awk '{ print $NF }'`

  # Workaround for variations in site-specific configuration
  if [ "X${_dbhost1}" = "X" ]; then
    _dbhost=`xmlconfig db/host 2>/dev/null | awk '{ print $NF }'`
    _dbhost1="${_dbhost}"
    _dbhost2="${_dbhost}"
  fi

  # For 'impdp'
  _conf_dpumpdir=`xmlconfig db/dpumpdir 2>/dev/null | awk '{ print $NF }' | head -1`
  _dpumpdir=${_arg_dpumpdir:-"$_conf_dpumpdir"}
  # For 'sqlplus' - use "DBA" user (need to create new user)
  _conf_ezdbaconnect=`xmlconfig db/ezdbaconnect 2>/dev/null | awk '{ print $NF }'`
  _dbconn=${_arg_ezdbaconnect:-"$_conf_ezdbaconnect"}
  # For 'impdp' - use Schema user (owner)
  _conf_ezconnect=`xmlconfig db/ezconnect 2>/dev/null | awk '{ print $NF }'`
  # Try to be smart...
  _argderived_ezconnect=`echo ${_arg_ezdbaconnect} | sed "s%^.*@\(.*\)%$1/$1@\1%"`
  if [ "X${_conf_ezconnect}" = "X" ]; then
    _conf_ezconnect=`echo ${_conf_ezdbaconnect} | sed "s%^.*@\(.*\)%$1/$1@\1%"`
  fi
  _dpconn=${_argderived_ezconnect:-"$_conf_ezconnect"}

  [ "X${_dpconn}" = "X" -o "X${_dbconn}" = "X" ] && errbailout "Error>>> No valid connect string found!" 10

  # The schema is specified on the command line and passed as $1
  #
  if [ "$#" -eq 1 -a "$1" != "${_schema}" ]; then
    # To handle the case when $_schema is an empty string, resulting in an empty connect string
    # when 'sed' fails...
    if [ "X${_schema}" != "X" ]; then
      _dpconn=`echo ${_dpconn} | sed "s%${_schema}\([/@]\)%$1\1%g"`
    fi
    _schema="$1"
  fi

  # If we should use alternative RAC node first
  #
  if [ -n "${_use_althost}" ]; then
    _dpconn=`echo ${_dpconn} | sed "s/${_dbhost1}/${_dbhost2}/"`
  fi

}

fix_dumpname() {
  if [ -n "${_use_imp}" ]; then
    _dmpname=`basename $1 | sed -e 's/\(.*\)\.dat/\1/'`
  else
    # Strip starting "dpexp_" and trailing "_*.dmp" from third argument (dumpname)
    #
    _dmpname=`basename $1 | sed -e 's/\(.*\)\.dmp/\1/' -e 's/^dpexp_\(.*\)/\1/' -e 's/\(.*\)_[0-9]*$/\1/'`
  fi
}

setup_oraenv() {
  # Set and export ORACLE_HOME, add $ORACLE_HOME/bin to PATH
  #
  # 2007-10-29: 'head -1' inserted to only get one result when there are several 
  #             matching rows in /etc/oratab
  #             Truncate FQDNs when necessary
  #
  _dbsid_trunc=`echo "${_dbsid}" | awk -F'.' '{ print $1 }'`
  _dbsid_uc_trunc=`echo "${_dbsid_uc}" | awk -F'.' '{ print $1 }'`
  ORACLE_HOME=`sed -ne "/^${_dbsid_trunc}/p" -ne "/^${_dbsid_uc_trunc}/p" /etc/oratab | awk -F':' '{ print $2 }' | head -1`
  # If no ORACLE_HOME can be found we try the following:
  # 1. Look for the instancename given in <connect_string>
  # 2. Take the last well-formatted row in /etc/oratab and set ORACLE_HOME 
  #    based on this
  if [ "X${ORACLE_HOME}" = "X" ]; then
    # Try to find the instance name in argument <connect_string>
    _wa_dbsid=`echo "${_arg_ezdbaconnect}" | awk -F'/' '{ print $NF }' |  awk -F'.' '{ print $1 }'`
    _wa_dbsid_uc=`echo "${_wa_dbsid}" | tr 'a-z' 'A-Z'`
    ORACLE_HOME=`sed -ne "/^${_wa_dbsid}/p" -ne "/^${_wa_dbsid_uc}/p" /etc/oratab | awk -F':' '{ print $2 }' | head -1`
    if  [ "X${_wa_dbsid}" = "X" -o  "X${ORACLE_HOME}" = "X" ]; then
      # Second ':'-separated field in last well-formed row
      ORACLE_HOME=`egrep "^.*:.*:.*$" /etc/oratab | awk -F':' '{ print $2 }'| tail -n1`
    fi
  fi
  [ "X${ORACLE_HOME}" = "X" ] && errbailout "ERROR>>> Cannot Set ORACLE_HOME! Try setting ORACLE_HOME before running the script" 13
  PATH=${ORACLE_HOME}/bin:${PATH}

  # Set LD_LIBRARY_PATH for DMOptimize
  if [ "${BITMODE}" = "32" -o "${ARCH}" = "i386_linux" ]; then
    LD_LIBRARY_PATH=${ORACLE_HOME}/lib32:${LD_LIBRARY_PATH}
  else
    LD_LIBRARY_PATH=${ORACLE_HOME}/lib:${LD_LIBRARY_PATH}
  fi
  export ORACLE_HOME PATH LD_LIBRARY_PATH
}

check_oracle_edition() {
  # Check whether we have an Oracle Enterprise Edition install
  #
  _oraed=`echo exit | sqlplus "${_dbconn}" | sed -n "s/^Oracle Database 1[0,1]g\(.*\)\ Edi.*$/\1/p" | sed 's/ //g'`

  if [ "${_oraed}" = "Enterprise" ]; then
    _maxrecthreads=6
    _threads=${_parallel:-$_maxrecthreads}
    _warnstring=""
  else
    _maxrecthreads=1
    _threads=1
    _warnstring="No Enterprise Edition - only single-thread Data Pump Exports/Imports allowed!"
  fi
}

drop_schema() {
  # Drop schema <new_schema_name>
  #
  echo "Dropping schema ${_newschema}"
  _uc_newschema=`echo "${_newschema}" | tr 'a-z' 'A-Z'`
  if [ "${_dbauser}" = "carmdba" ]; then
    # Limited privileges, use stored procedure:
    sqlplus "${_dbconn}" << EOF > /dev/null 2>&1
call sys.secured_drop_user('${_uc_newschema}');
exit
EOF
  else
    # Assume dba-like privileges
    sqlplus "${_dbconn}" << EOF > /dev/null 2>&1
drop user ${_newschema} cascade;
exit
EOF
  fi
}

create_schema() {
  # Create (temporary) sqlplus input file to create new user/schema
  #
  # 

  _tmpfile="/tmp/create_${_newschema}"
  cat > ${_tmpfile} << EOF
CREATE USER ${_newschema} IDENTIFIED BY ${_newschema}
DEFAULT TABLESPACE flm_data
QUOTA UNLIMITED ON flm_data
TEMPORARY TABLESPACE flm_temp;

GRANT CREATE SESSION,  
      CREATE TABLE,  
      CREATE VIEW,
      CREATE SEQUENCE, 
      CREATE PROCEDURE
TO ${_newschema};

GRANT READ, WRITE ON DIRECTORY ${_dpumpdir} to ${_newschema};

exit
EOF

  (
    echo "About to create a new user on ${_dbconn} with the following SQL"
    echo '******************************************************************************'
    cat ${_tmpfile}
    echo ""
    echo '******************************************************************************'
    echo -n "Continue (Y)es/(N)o/(I)gnore/(S)kip (y)?"
  ) 2>&1 | tee -a "${CARMTMP}/logfiles/${_logfile}"

  if [ -z "$_batch" ]; then
    read yorn
  fi
  if [ "$yorn" = "i" -o "$yorn" = "I" -o "$yorn" = "s" -o "$yorn" = "S" ]; then
    # Skip/Ignore this step
    continue
  elif [ "X$yorn" != "X" -a "$yorn" != "y" -a "$yorn" != "Y" ]; then
    bailout "Import aborted" 0
  else
    ( 
      # Create user/schema
      #
      echo ""
      echo "Creating ${_newschema} user... "
      sqlplus "${_dbconn}" < "${_tmpfile}"
    ) 2>&1 | tee -a "${CARMTMP}/logfiles/${_logfile}"
  fi
  echo "$?"
}

set_jobname() {
  # Nice to have a timestamp in the filenames of the impdp logs...
  _ts=`date '+%Y%m%d_%H%M%S%Z'`
  _jobname="dpimp_${_dmpname}_to_${_newschema}_at_${_ts}"
}

mk_param_file() {
  if [ -n "$_tables_only" ]; then
      _tbl_action="REPLACE"
      _excludes="STATISTICS,INDEX"
  else
      _tbl_action="TRUNCATE"
      _excludes="STATISTICS"
  fi
  echo "Creating parameter file for Oracle Data Pump Import..." | tee -a "${CARMTMP}/logfiles/${_logfile}"
  cat > "/tmp/dpimp_${_dmpname}_to_${_newschema}.par" << EOF
SCHEMAS=${_expschema}
REMAP_SCHEMA=${_expschema}:${_newschema}
DIRECTORY=${_dpumpdir}
DUMPFILE=dpexp_${_dmpname}_%U.dmp
LOGFILE=${_jobname}.log
PARALLEL=${_threads}
JOB_NAME=dpimp_${_ts}_${_expschema}
TABLE_EXISTS_ACTION=${_tbl_action}
EOF
}

import_schema() {
  if [ -n "${_use_imp}" ]; then
    # Use old style 'imp'...
    _dumpdir=/opt/Carmen/oradpump
    _cmdline="imp ${_dpconn} fromuser=${_expschema} touser=${_newschema} log=${_dumpdir}/imp_${_dmpname}_to_${_newschema}_at_${_ts}.log file=${_dumpdir}/${_dmpname}.dat"
    (
      echo "About to run: " "${_cmdline}"
      echo ""
      echo -n "Is this OK? (y) "
    ) 2>&1 | tee -a "${CARMTMP}/logfiles/${_logfile}"
    if [ -z "$_batch" ]; then
      read yorn
      [ "X$yorn" != "X" -a "$yorn" != "y" -a "$yorn" != "Y" ] && bailout "Import aborted" 0
    fi
    (
      echo ""
      echo "Running Oracle Import (imp)..."
      ${_tracecmd} ${_cmdline}
    ) 2>& 1 | tee -a "${CARMTMP}/logfiles/${_logfile}"
  else
    _cmdline="impdp ${_dpconn} PARFILE=\"/tmp/dpimp_${_dmpname}_to_${_newschema}.par\""

    (
      echo "About to run: " "${_cmdline}"
      echo ""
      echo "Contents of /tmp/dpimp_${_dmpname}_to_${_newschema}.par:"
      echo '**********************************************************'
      cat "/tmp/dpimp_${_dmpname}_to_${_newschema}.par"
      echo '**********************************************************'
      echo "${_warnstring}"
      if [ "${_threads}" -gt "${_maxrecthreads}" ]; then
        echo "NOTE! IT IS NOT RECOMMENDED TO USE MORE THAN ${_maxrecthreads} PROCESSES/THREADS IN A PRODUCTIION ENVIRONMENT!"
      fi
      echo ""
      echo -n "Is this OK? (y) "
    ) 2>&1 | tee -a "${CARMTMP}/logfiles/${_logfile}"

    if [ -z "$_batch" ]; then
      read yorn
      [ "X$yorn" != "X" -a "$yorn" != "y" -a "$yorn" != "Y" ] && bailout "Import aborted" 0
    fi
    (
      echo ""
      echo "Running Oracle Data Pump Import..."
      ${_tracecmd} ${_cmdline}
    ) 2>& 1 | tee -a "${CARMTMP}/logfiles/${_logfile}"
  fi
}

gather_stats() {
  _uc_newschema=`echo ${_newschema} | tr '[a-z]' '[A-Z]'`
  # Run SQL*Plus to gather statistics
  echo "Gathering statistics..."
  sqlplus "${_dbconn}" << EOF
exec dbms_stats.gather_schema_stats('${_uc_newschema}',10);
exit
EOF
}
 
run_dmopt() {
  _is_beta4=`grep "beta-4" ${CARMSYS}/data/config/release_info 2>/dev/null`
  if [ "${_dbauser}" = "carmdba" -a -n "${_is_beta4}" ]; then
    echo "Warning Cannot run the following with carmdba for Beta 4: "
    echo carmrunner DMOptimize -c ${_daveconnect} ${_newschema}
    echo "Running an ordinary statistics job as the schema owner instead"
    gather_stats
  else
    _optdaveconnect=`echo "${_daveconnect}" | sed "s%oracle:\(.*\)%oracle:$_dbconn%"`
    ${_tracecmd} carmrunner DMOptimize -v -c ${_optdaveconnect} ${_newschema}
  fi
}

trap 'bailout "Exiting..." $?' 0 1 2 3 11 15

# To avoid file permission problems...
umask 002

_parallel=${_parallel:-2}

# Main

handle_params $*
check_valid_ora
setup_carmenv

touch "${CARMTMP}/logfiles/${_logfile}"

set_db_params ${_newschema}
fix_dumpname ${_dumpname}

# Setup ORACLE_HOME if not already set correctly.
if [ -z "${ORACLE_HOME}" -o ! -d "${ORACLE_HOME}" -o ! -x "${ORACLE_HOME}/bin/sqlplus" ]; then
  setup_oraenv
else
  PATH=${ORACLE_HOME}/bin:${PATH}
  export PATH
fi
check_oracle_edition

if [ -n "${_drop_schema}" ]; then
  drop_schema
fi

create_schema

set_jobname
if [ -z "${_use_imp}" ]; then
  mk_param_file
fi

import_schema

if [ -n "${_gather_stats}" ]; then
  gather_stats
fi

if [ -n "${_run_dmopt}" ]; then
  run_dmopt
fi
