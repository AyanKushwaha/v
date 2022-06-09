#
# Wrapper script for use with configuration. If a script need to set
# CARMXXX variables, this file should be used.
#
# Note: this file is located in the CARMUSR
# if CARMUSR wasn't known it would never be
# found by the carmsys scripts.
#
#

if [ -n "$CMSSHELL" ]; then
  if [ -f ~/.bashrc ]; then
    _OLDPS=$PS1
    _OLDPROMPTCMD="$PROMPT_COMMAND"
    source ~/.bashrc
    export PS1=$_OLDPS
    export PROMPT_COMMAND="$_OLDPROMPTCMD"
  fi
  unset CMSSHELL
fi

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/mqm/lib64

# A private portbase must conform to the following: unlikely to overlap for 
# concurrent users, no value lower  than 10k, no value larger than 65k. We
# achive this by multiplying the current UID with five (so that UID 10 gets
# five ports free before UID 11), moduloing the result with 55000 (so that 
# larger values "wrap") and then adding 10k to it, so that we never get a 
# portbase smaller than 10k, if the previous steps yield zero.
USER_PRIVATE_PORT=`expr $((5*\`id -u\`)) % 55000 + 10000`
export USER_PRIVATE_PORT

#echo "Entering bin/carmenv.sh..."
_SRC=$BASH_SOURCE
if [ -z $CARMUSR ]; then
    CARMUSR=`readlink -f \`dirname $_SRC\`/..`
fi

if [ -e ".git/HEAD" ]; then
  _STARTBRANCH=`cat .git/HEAD | grep -o '[^/]*$'`
  function _gitbranch() {
    _CURRENTBRANCH=`cat .git/HEAD | grep -o '[^/]*$'`
    echo -n $_CURRENTBRANCH
    if [ "x$_CURRENTBRANCH" != "x$_STARTBRANCH" ]; then
      echo -n " [SWITCHED BRANCH!]"
    fi
  }
fi





function _carmpwd() {
# A function returning the current working directory with 
# "environment reverse substitution".
# The function is designed to replace \w in the Bash PS variables.
# E.g. if environment contains CARMUSR=/opt/Carmen/CARMUSR/PROD, then
# /opt/Carmen/CARMUSR/PROD/lib/python will be substituted with
# $CARMUSR/lib/python
# The special variable HOME will be replaced with ~ just like \w does.

python <<EOF
import os

def liststartswith(xs, ys):
    return xs[:len(ys)] == ys

cwd = os.environ["PWD"].split("/")
for (x,y) in sorted(os.environ.items(), key=lambda (x,y): (-len(y), x)):
    if x not in ("PWD","OLDPWD","CARMSTD") and y <> "" and liststartswith(cwd, y.split("/")):
        if x == "HOME":
            print r"\[\033[93;01m\]~%s\[\033[0m\]"%(os.environ["PWD"][len(y):])
	elif x == "CARMUSR":
            print r'\[\033[32m\]%s%s\[\033[0m\]' %(y.split('/')[-1],os.environ["PWD"][len(y):])
        else:
            print "$%s%s"%(x,os.environ["PWD"][len(y):])
        break
else:
    print r'\[\033[93;01m\]%s\[\033[0m\]' %(os.environ["PWD"])
EOF
}

. $CARMUSR/etc/scripts/shellfunctions.sh

# If SGE has not been configured yet, try to find it now
[ -z "$SGE_ROOT" ] && \
        _running=`(ps -ef | grep sge_execd | grep -v grep | awk '{print $NF}' | sed 's%/bin/.*$%%') 2>/dev/null`
for _sge in $_running /usr/local/gridengine /usr/local/share/sge /opt/Carmen/sge /opt/sge; do
    [ -z "$SGE_ROOT" -a -f ${_sge}/default/common/settings.sh ] && \
        . ${_sge}/default/common/settings.sh 2>/dev/null
done

if [ -z "$CARMDATA" ]; then
    CARMDATA=$CARMUSR/current_carmdata

  if [ ! -d "$CARMDATA" ]; then
    echo "***************    ERROR    ********************" 
    echo "          No link to CARMDATA found!"
    echo "           Please set and restart!"
    echo "***************    ERROR    ********************" 
    exit -1
  fi
fi

if [ -z "$CARMTMP" -o -z "$CARMSYS" ]; then
    setCarmvars "$SK_APP"
fi

if [ -z "$CARMUSR_JMP" ]; then
    CARMUSR_JMP=$CARMUSR/current_carmusr_jmp

  if [ ! -d "$CARMUSR_JMP" ]; then
    echo "***************    ERROR    ********************" 
    echo "          No link to CARMUSR_JMP found!"
    echo "           Please set and restart!"
    echo "***************    ERROR    ********************" 
    exit -1
  fi
fi

CMSSHELLMODULES=

DAVE_FORK_PROTECTION=1

function help() {
  echo "Help"
  echo "  home       Changes directory to CARMUSR"
  echo "  tmp        Changes directory to CARMTMP"
  echo "  logs       Changes directory to CARMTMP/logfiles"
  echo ""
  echo "  compileRulesets "
  echo "             Starts compilation of a ruleset"
  echo "  studio     Starts Studio"
  echo "  sqlplus    Starts SQL*Plus"
  echo "  sql [stmt] Starts SQL*Plus with the current schema,"
  echo "             optionally executing the specified statement"
  echo "  sysmondctl Manages sysmond"
  for M in $CMSSHELLMODULES; do
    echo "  `printf %-11s $M`(Type '$M help' for help)"
  done
}

function _sqlplus () {
	if type sqlplus >/dev/null 2>&1; then
		sqlplus "$@"
	elif type sqlplus64 >/dev/null 2>&1; then
		sqlplus64 "$@"
	else
		echo "slqplus or sqlplus64 is missing"
	fi
}

function sql() {
  _DB_LOC="`echo $DB_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`"
  echo $_DB_LOC
  if [ "x$1" == "x" ]; then
    _sqlplus $_DB_LOC
  else
    _sqlplus -S $_DB_LOC << EOF
SET LINESIZE 32000
$@ ;
EOF
  fi
}

function sqlhistory() {
  _DB_LOC="`echo $DB_URL_HISTORY |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`"
  echo $_DB_LOC
  if [ "x$1" == "x" ]; then
    _sqlplus $_DB_LOC
  else
    _sqlplus -S $_DB_LOC << EOF
SET LINESIZE 32000
$@ ;
EOF
  fi
}

function sqladm() {
  _DB_LOC="`echo $DB_ADM_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`"
  if [ "x$1" == "x" ]; then
    _sqlplus $_DB_LOC
  else
    _sqlplus -S $_DB_LOC << EOF
SET LINESIZE 32000
$@ ;
EOF
  fi
}

function sqladmhistory() {
  _DB_LOC="`echo $DB_ADM_URL_HISTORY |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`"
  if [ "x$1" == "x" ]; then
    _sqlplus $_DB_LOC
  else
    _sqlplus -S $_DB_LOC << EOF
SET LINESIZE 32000
$@ ;
EOF
  fi
}

function sqlcp() {
  _DB_LOC="`echo $DB_CP_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`"
  if [ "x$1" == "x" ]; then
    _sqlplus $_DB_LOC
  else
    _sqlplus -S $_DB_LOC << EOF
SET LINESIZE 32000
$@ ;
EOF
  fi
}

for F in $CARMUSR/bin/shell/*.py; do
  _MOD=`basename $F .py`
  if [ "x$_MOD" != "x" ]; then
    _CMD="PYTHONPATH=$CARMUSR/bin/shell:$PYTHONPATH python $CARMUSR/bin/shell/shell.inc $_MOD"
    alias $_MOD="$_CMD"
    CMSSHELLMODULES="$CMSSHELLMODULES $_MOD"
    if [ -n $CMSSHELL ]; then
      complete -C "$_MOD --briefhelp" $_MOD
    fi
  fi
done
unset _MOD
unset _CMD


export PATH=$CARMUSR/bin:$CARMSYS/bin:/usr/sbin:$PATH
alias studio=$CARMUSR/bin/studio.sh
alias home="cd $CARMUSR"
alias tmp="cd $CARMTMP"
alias logs="cd $CARMTMP/logfiles"
export CARMUSR CARMSYS CARMTMP CARMDATA CARMUSR_JMP

#Shell completions

if [ -n $CMSSHELL ]; then
  complete -W "init start stop exit shutdown restart" sysmondctl
fi

# SKCMS-2187 / SKS-191: Turn on flag to use fix in CARMSYS (from 25.4).
export DAVE_EXCLUDE_DELETED_REFERENCED=1
