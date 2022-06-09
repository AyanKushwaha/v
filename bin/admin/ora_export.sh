#!/bin/sh
#
# Script to export a CMS DB schema using Oracle Data Pump's Export functionality 
#
# (c) Copyright Jeppesen Systems AB
#
# $Header: /opt/Carmen/CVS_REPOSITORY/Customization/ay_cms_user/bin/admin/ora_export.sh,v 1.5.4.2 2011/03/30 10:15:32 carmen Exp $
#
# Some nice functions for error and interrupt handling
#

_tracecmd="time"
_logfile=oradp_export_`date '+%Y%m%d_%H%M%S%Z'`.log
_cwd=`pwd`
_maxrecthreads=2
unset _use_exp _unsafe > /dev/null 2>&1

# Use FLASHBACK_TIME by default
_use_fbt=1

usage() {
  echo "Exports a schema using the Oracle Data Pump expdp or exp commands"
  echo "Usage: "`basename $0`" [-p n] [-b] [-a] [-c] [-n] [-o] [-u]" 
  echo "                     [-t <flashback_time>]"
  echo "                     [-d <dpump_directory>] [-C <ezconnect_string>]"
  echo "                     [<schema_name>]"
  echo ""
  echo "       -   <dpump_directory> is the Oracle name of the directory"
  echo "           where the dumpfile set is located, e.g. 'dpump_dir'"
  echo "       -   <ezconnect_string> is the Oracle Easy (EZ) Connect string"
  echo "           for the Oracle user owning the schema to export,"
  echo "           e.g. 'sk_blabla/tralala@orahost1:1621/gpd77dev'"
  echo "           or 'sk_blabla/blabla@orahost2/gtn99tst'"
  echo ""
  echo "  -p n Use n parallel threads for export job."
  echo "       The default is 2 for Oracle 10g Enterprise Edition," 
  echo "       otherwise 1. "
  echo "       Make sure you don't use anything higher"
  echo "       than 2 unless you're sure it won't affect a production"
  echo "       system's performance!"
  echo "  -b   Run export as batch job without user interaction."
  echo "  -a   Use alternative RAC node first"
  echo "  -c   Use FLASHBACK_TIME to ensure consistency (default)"
  echo "  -n   Don't use FLASHBACK_TIME, full consistency not ensured when system online"
  echo "  -o   Use old style 'export'"
  echo "  -u   Unsafe mode. Ignore all CARMUSR/CARMSYS/CARMUTIL dependencies and try to"
  echo "       run the script anyway. This requires that everything needed is correctly"
  echo "       specified on the command line."
  echo "  -t   Use <flashback_time> as the value of FLASHBACK_TIME."
  echo "       Overrides the '-n' option"
  echo "       <flashback_time> must be specified in the following format:"
  echo "         'YYYY-MM-DD%hh:mm:ss'" 
  echo "       Please note that snapshots aren't possible to"
  echo "       retrieve particularly far back in time"
  echo "  -d   Use the Oracle directory <dpump_directory>"
  echo "       This directory must exist in Oracle and" 
  echo "       be writable for the Oracle user (schema owner)"
  echo "  -C   Use <ezconnect_string> as (Easy) Connect string for expdp/exp"
  echo "       instead of default retrieved from configuration. If it isn't"
  echo "       possible to retrieve a default from the configuration this"
  echo "       is a *required* option."
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

handle_params() {
  # Get the command line options and take actions
  #
  while getopts p:baonct:d:C: opts
  do
    case "$opts" in
      p) _parallel=$OPTARG
         ;;
      b) _batch=1
         ;;
      a) _use_althost=1
         ;;
      o) _use_exp=1
         ;;
      u) _unsafe=1
         ;;
      n) unset _use_fbt > /dev/null 2>&1
         ;;
      c) _use_fbt=1
         ;;
      t) _arg_fbt_ts=$OPTARG
         _use_fbt=1
         ;;
      d) _arg_dpumpdir=$OPTARG
         ;;
      C) _arg_ezconnect=$OPTARG
         ;;
      *) usage
         ;;  
    esac
  done

  # Shift away options
  shift `expr $OPTIND - 1`

  if [ "$#" -gt 1 ]; then
    usage
  elif [ "$#" -eq 1 ]; then
    _selected_schema="$1"
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
  if [ -z "${_unsafe}" ] && rpm -V "${_carmutil}" >/dev/null 2>&1; then
    # CARMUSR setup
    . ${CARMUSR}/bin/carmenv.sh
  else
    if [ -h $CARMUSR/current_carmsys_cct ]; then 
      CARMSYS=${CARMUSR}/current_carmsys_cct
    elif [ -h $CARMUSR/current_carmsys ]; then 
      CARMSYS=${CARMUSR}/current_carmsys
    else
      echo "WARNING >>> No CARMSYS link found! Script is likely to fail if everything needed isn't specified on the command line!"
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

check_oracle_edition() {
  # Check whether we have an Oracle Enterprise Edition install
  #
  echo -n "Checking for Enterprise edition... "
  _oraed=`echo exit | sqlplus "${_dbconn}" | sed -n "s/^Oracle Database 1.g\(.*\)\ Edi.*$/\1/p" | sed 's/ //g'`

  if [ "${_oraed}" = "Enterprise" ]; then
    _maxrecthreads=2
    _threads=${_parallel:-$_maxrecthreads}
    _warnstring=""
    echo "[done - Enterprise]"
  else
    _maxrecthreads=1
    _threads=1
    _warnstring="No Enterprise Edition - only single-thread Data Pump Exports/Imports allowed!"
    echo "[done - not Enterprise]"
  fi
}

set_db_params() {
  # Retrieve DB information from configuration
  #
  _schema=`xmlconfig db/schema 2>/dev/null | awk '{ print $NF }'`
  # The instance name in both lower- and uppercase is used 
  # for lookup in /etc/oratab
  _dbsid=`xmlconfig db/servicename 2>/dev/null | awk '{ print $NF }'` 
  # WA for missing servicename in config
  if [ "X${_dbsid}" = "X" ]; then
    _dbsid=`xmlconfig db/sid 2>/dev/null | awk -F= '{ print $NF }'`
  fi
  # Uppercase version of the SID
  _dbsid_uc=`echo "${_dbsid}" | tr 'a-z' 'A-Z'`

  # Retrieve the hostname of the first RAC node
  _dbhost1=`xmlconfig db/host1 2>/dev/null | awk '{ print $NF }'`
  # Retrieve the hostname of second RAC node as well
  _dbhost2=`xmlconfig db/host2 2>/dev/null | awk '{ print $NF }'`

  # Workaround for variations in site-specific configuration
  if [ "X${_dbhost1}" = "X" ]; then
    _dbhost=`xmlconfig site/db/host 2>/dev/null | awk '{ print $NF }'`
    _dbhost1="${_dbhost}"
    _dbhost2="${_dbhost}"
  fi

  # For 'expdp'
  _conf_dpumpdir=`xmlconfig db/dpumpdir 2>/dev/null | awk '{ print $NF }' | head -1`
  _dpumpdir=${_arg_dpumpdir:-"$_conf_dpumpdir"}
  # For 'expdp' - use Schema user (owner)
  _conf_ezconnect=`xmlconfig db/ezconnect 2>/dev/null | awk '{ print $NF }'`
  _dpconn=${_arg_ezconnect:-"$_conf_ezconnect"}
  # For 'sqlplus' - use "DBA" user or schema owner
  _conf_ezdbaconnect=`xmlconfig db/ezdbaconnect 2>/dev/null | awk '{ print $NF }'`
  # Try to be smart...
  if [ "X${_conf_ezdbaconnect}" = "X" ]; then
    _conf_ezdbaconnect="${_conf_ezconnect}"
  fi
  _dbconn=${_arg_ezconnect:-"$_conf_ezdbaconnect"}
  
  [ "X${_dpconn}" = "X" -o "X${_dbconn}" = "X" ] && errbailout "Error>>> No valid connect string found!" 10

  # If schema is specified on the command line
  #
  if [ "$#" -eq 1 -a "$1" != "${_schema}" ]; then
    if [ -n "${_schema}" ]; then
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

setup_oraenv() {
  # Set and export ORACLE_SID and ORACLE_HOME, add $ORACLE_HOME/bin to PATH
  # Only works if /etc/oratab exists and are configured for ${_dbsid}
  # See workaround for Finnair clients below
  #
  ORACLE_HOME=`sed -ne "/^${_dbsid}/p" -ne "/^${_dbsid_uc}/p" /etc/oratab | awk -F':' '{ print $2 }' | head -1`
  # If no ORACLE_HOME can be found we try the following:
  # 1. Look for the instance name given in <connect_string>
  # 2. Take the last well-formatted row in /etc/oratab and set ORACLE_HOME
  #    based on this
  if [ "X${ORACLE_HOME}" = "X" ]; then
    # Try to find the instance name in argument <connect_string>
    _wa_dbsid=`echo "${_arg_ezdbaconnect}" | awk -F'/' '{ print $NF }' |  awk -F'.' '{ print $1 }'` 
    _wa_dbsid_uc=`echo "${_wa_dbsid}" | tr 'a-z' 'A-Z'`
    ORACLE_HOME=`sed -ne "/^${_wa_dbsid}/p" -ne "/^${_wa_dbsid_uc}/p" /etc/oratab | awk -F':' '{ print $2 }' | head -1`
    if  [ "X${_wa_dbsid}" = "X" -o  "X${ORACLE_HOME}" = "X" ]; then
      # Second ':'-separated field in last wellformed row
      ORACLE_HOME=`egrep "^.*:.*:.*$" /etc/oratab | awk -F':' '{ print $2 }'| tail -n1`
    fi
  fi
  [ "X${ORACLE_HOME}" = "X" ] && errbailout "ERROR>>> Cannot Set ORACLE_HOME! Try setting ORACLE_HOME before running the script." 13
  PATH=${ORACLE_HOME}/bin:${PATH}
  export ORACLE_HOME PATH
}

set_jobname() {
  # Nice to have a timestamp in the filenames of the expdp dumps...
  _ts=`date '+%Y%m%d_%H%M%S%Z'`
  _jobname="dpexp_${_schema}_${_ts}"
  # Better uniqueness with this string...
  _jobname2="dpexp_${_ts}"
}

dump_schema() {
  if [ -n "${_use_exp}" ]; then
    # Use old style 'exp' for export (workaround for some problems)
    echo "Running old style export..."
    _expdir=/opt/Carmen/dptemp
    _expfile=exp_${_schema}_${_ts}.dat
    _cmdline="exp ${_dpconn} owner=${_schema} consistent=Y log=${_expdir}/${_logfile} file=${_expdir}/${_expfile}"
  else
    # Oracle Data Pump export (preferred)
    echo "Creating parameter file for Oracle Data Pump Export..." | tee -a "${CARMTMP}/logfiles/${_logfile}"
    if [ -n "${_use_fbt}" ]; then
      # Use FLASHBACK_TIME
      _now_ts=`unset TZ; date '+%Y-%m-%d %H:%M:%S'`
      if [ -n "${_arg_fbt_ts}" ]; then
        _fbt_ts=`echo "${_arg_fbt_ts}" | tr '%' ' '`
        [ `expr length "${_fbt_ts}"` -ne 19 -o `expr index "${_arg_fbt_ts}" "%"` -ne 11 ] && errbailout "Error>>> Invalid timestamp: ${_arg_fbt_ts} " 25
      else
        _fbt_ts=${_now_ts}
      fi
      ${_tracecmd} cat > /tmp/${_schema}_${_ts}.par << EOF
SCHEMAS=${_schema}
DIRECTORY=${_dpumpdir}
DUMPFILE=${_jobname}_%U.dmp
LOGFILE=${_jobname}.log
PARALLEL=${_threads}
JOB_NAME=${_jobname2}
FLASHBACK_TIME="TO_TIMESTAMP('${_fbt_ts}', 'YYYY-MM-DD HH24:MI:SS')"
EOF
    else
      ${_tracecmd} cat > /tmp/${_schema}_${_ts}.par << EOF
SCHEMAS=${_schema}
DIRECTORY=${_dpumpdir}
DUMPFILE=${_jobname}_%U.dmp
LOGFILE=${_jobname}.log
PARALLEL=${_threads}
JOB_NAME=${_jobname2}
EOF
    fi
    _cmdline="expdp ${_dpconn} PARFILE=\"/tmp/${_schema}_${_ts}.par\""
  fi

  {
    echo ""
    echo "About to run: " "${_cmdline}"
    echo ""
    if [ -z "${_use_exp}" ]; then
      echo "Contents of /tmp/${_schema}_${_ts}.par:"
      echo '**********************************************************'
      cat "/tmp/${_schema}_${_ts}.par"
      echo '**********************************************************'
      echo ORACLE_HOME=${ORACLE_HOME}
      echo "${_warnstring}"
      if [ "${_threads}" -gt "${_maxrecthreads}" ]; then
        echo "NOTE! IT IS NOT RECOMMENDED TO USE MORE THAN ${_maxrecthreads} PROCESSES/THREADS IN A PRODUCTIION ENVIRONMENT!"
      fi
      echo ""
    fi
    echo -n "Is this OK (y)? "
    if [ -z "$_batch" ]; then
      read yorn
      [ "X$yorn" != "X" -a "$yorn" != "y" -a "$yorn" != "Y" ] && bailout "Export aborted" 9
    fi

    if [ -n "${_use_exp}" ]; then
      echo "Starting old style export..."
    else
      echo "Starting Oracle Data Pump Export..."
    fi  
    ${_tracecmd} ${_cmdline}
    # Store exit code
    _exp_exit="$?"
    [ -n "${_use_exp}" -a "${_exp_exit}" -eq 0 ] && echo "Export terminated successfully, file is ${_expdir}/${_expfile}"
    #exit ${_exp_exit}
  } 2>&1 | tee -a "${CARMTMP}/logfiles/${_logfile}"
}

verify_dump() {
  echo -n "Verifying that the dumpfile set really exists... " | tee -a "${CARMTMP}/logfiles/${_logfile}" 

  # We look at the logfile since it is most likely to be readable
  #
  _export_log=`grep -A1 "Dump file set for" "${CARMTMP}/logfiles/${_logfile}" | tail -n 1 | sed 's/^ *\(.*\)_[0-9]*\.dmp/\1.log/'`

  # Test if export log exists. We're finished if it does so then we exit.
  #
  [ -s "${_export_log}" ] && echo "[OK]" && exit 0

  # Problem: No files created even if everything else looks fine.
  # Reason: Files probably created on alternative node with mirrored
  # disk area.
  # What can we do? rsync with alternative node
    {
    echo "[FAILED]"
    echo ""
    echo "Trying to 'rsync' with the other RAC node, i.e. ${_dbhost2}..."
    echo ""
    _dumpdir=`dirname "${_export_log}"`
    ${_tracecmd} rsync -vr --ignore-existing "${_dbhost2}:${_dumpdir}/*${_ts}*" "${_dumpdir}"
  } | tee -a "${CARMTMP}/logfiles/${_logfile}"

}

# Main

trap 'bailout "Exiting..." $?' 0 1 2 3 11 15

# To avoid file permission problems...
umask 002

handle_params $*
check_valid_ora
setup_carmenv

# Create logfile
touch "${CARMTMP}/logfiles/${_logfile}"

set_db_params ${_selected_schema}

# Setup ORACLE_HOME if not already set.
if [ -z "${ORACLE_HOME}" -o ! -d "${ORACLE_HOME}" -o ! -x "${ORACLE_HOME}/bin/sqlplus" ]; then
  setup_oraenv
else
  PATH=${ORACLE_HOME}/bin:${PATH}
  export PATH
fi

check_oracle_edition
set_jobname

dump_schema
_dump_result=`grep "successfully" ${CARMTMP}/logfiles/${_logfile} > /dev/null 2>&1 ; echo $?` 

grep "aborted" ${CARMTMP}/logfiles/${_logfile} > /dev/null && exit 0

if [ -n "${_use_exp}" -o "${_dump_result}" -ne 0 ]; then
  exit ${_dump_result}
else
  verify_dump
fi

# Verification obviously failed, but should be recovered now...

echo "Dump file set should now be visible on this host (and ${_dbhost1})"
