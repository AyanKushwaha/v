#!/bin/sh
# Start script to start Studio in the different modes that are
# available for in the SAS user.

usageText() {
  echo "Script to start a studio instance"
  echo "Usage: "`basename $0`" [-X h|c|C] flag [studio flags]" 
  echo "  -a           : flag from the alertmonitor when starting studio "
  echo "  -b           : flag from the alertmonitor when starting studio dayofops "
  echo "  -t           : flag to start studio tracking from  sessionserver launcher "
  echo "  -o           : flag to start studio day of operations tracking from  sessionserver launcher "
  echo "  -p           : flag to start studio planning from  sessionserver launcher "
  echo "  -l           : flag to start studio planning in lookback mode "
  echo "  -m           : flag to start studio prerostering from sessionserver launcher "
  echo "  -S t|p|m|o   : flag to start with log file written to standard out; the options"
  echo "                 are the same as when used as flags above"
  echo "  -P t|p|m|o   : Use performance logging"
  echo "  -D           : flag to start studio in debug mode; normal studio flags apply "
  echo "                 note that environment variable SK_APP needs to be set correctly"
  echo "  -X h|m|c|C   : Start in Profile mode:"
  echo "                   h: Heap profiler (Google perftools)"
  echo "                   m: Memcheck (valgrind)"
  echo "                   c: CPU profiler (Google perftools)"
  echo "                   C: CPU profiler (callgrind)"
  echo "  -h           : help"
}

function start_studio() {
    # Sets default arguments (used for all studio applications). 
    SK_ARG="-w -p PythonRunFile(\"carmensystems/studio/webserver/InitWebServer.py\")"
    # If nothing else is set, the log will contain the application name
    LOG_ID=$SK_APP

    # Sets default window size. 
    WIN_SIZE=1180x950

    # Modifies the arguments depending on the application.
    _LOAD_PLAN=
    case $1 in
        -a) LOG_ID=AlertMonitor
            SK_ARG="$SK_ARG" 
            ;;

        -b) LOG_ID=AlertMonitorDayOfOps
            SK_ARG="$SK_ARG" 
            ;;

        -t) _LOAD_PLAN=1 
            SK_ARG="$SK_ARG"
            ;;

        -o) _LOAD_PLAN=1 
            SK_ARG="$SK_ARG"
            ;;

        -p) #unset CARM_PRE_PYTHONPATH
            SK_ARG="$SK_ARG"
            ;;

        -l) #unset CARM_PRE_PYTHONPATH
            SK_ARG="$SK_ARG"
            ;;

        -m) WIN_SIZE=960x700
            SK_ARG="$SK_ARG  -p PythonEvalExpr(\"carmusr.StartStudio.prerostering()\")";;
    esac

    if [ "$PERIOD_START" -o "$PERIOD_END" -o "$SINGLE_CREW_PLAN" ]; then
      _LOAD_PLAN=1
    fi
    
    if [ "$SK_APP" == "Tracking" -a "$_LOAD_PLAN" ]; then
      echo "Loading plan"  
      SK_ARG="$SK_ARG -p PythonEvalExpr(\"carmusr.tracking.OpenPlan.loadPlan($START_SCRIPT)\")"
    fi

    if [ "$SK_APP" == "DayOfOps" -a "$_LOAD_PLAN" ]; then
      echo "Loading plan"  
      SK_ARG="$SK_ARG -p PythonEvalExpr(\"carmusr.tracking.OpenPlan.loadPlan($START_SCRIPT)\")"
    fi
    
    timestamp=`date '+%Y%m%d.%H%M.%S'`
    LOGDIR=$CARMTMP/logfiles
    [ -d $LOGDIR ] || mkdir -m a+rwxt $LOGDIR
    LOG_FILE=$LOGDIR/studio.$LOG_ID.$USER.$timestamp.$HOSTNAME
    export LOG_FILE
    # Start studio depending on the application.
    case $1 in
        -a) shift
            $CARMSYS/bin/studio $SK_ARG -p "-xrm Carmen*geometry:$WIN_SIZE" -l $LOG_FILE "$@"
            ;;
        -b) shift
            $CARMSYS/bin/studio $SK_ARG -p "-xrm Carmen*geometry:$WIN_SIZE" -l $LOG_FILE "$@"
            ;;
        -t|-o|-p|-l|-m|-r)
            shift
            $CARMSYS/bin/studio $SK_ARG -p "-xrm Carmen*geometry:$WIN_SIZE" -l $LOG_FILE "$@"
            ;;
        -S|-P)
            shift 2
            export CARMDEV=1
            $CARMSYS/bin/studio $SK_ARG -p "-xrm Carmen*geometry:$WIN_SIZE" "$@" | /usr/bin/tee $LOG_FILE
            ;;
        -D) shift
            $CARMSYS/bin/studio "$@"
            ;;
    esac
}

function setup_profiler() {
    if [ -f /users/rickard/bin/perftools/lib/libprofiler.so ]; then
       _GOOGLELIB=/users/rickard/bin/perftools/lib
    fi
    if [ -f /users/carmadm/bin/perftools/lib/libprofiler.so ]; then
       _GOOGLELIB=/users/carmadm/bin/perftools/lib
    fi
    _MARKER=`date +%Y%m%d-%H%M%S`
    case $1 in
        callgrind)
          _CALLGRIND_BINARY=`which valgrind`
          if [ -f /users/rickard/bin/valgrind/bin/valgrind ]; then
              # Use newer version, if available
              _CALLGRIND_BINARY=/users/rickard/bin/valgrind/bin/valgrind
          fi
          if [ -f /users/carmadm/bin/valgrind/bin/valgrind ]; then
              # Use newer version, if available
              _CALLGRIND_BINARY=/users/carmadm/bin/valgrind/bin/valgrind
          fi
          if [ -z "$_CALLGRIND_BINARY" ]; then
              echo "Did not find Valgrind on the system. Check your PATH"
              exit 1
          fi
          export DEBUGGER="$_CALLGRIND_BINARY --tool=callgrind --separate-threads=yes --callgrind-out-file=/tmp/studio.$USER.cg.%p.out --instr-atstart=no"
          echo "Profiler:               `$_CALLGRIND_BINARY --version`"
          echo "Profiler output:        /tmp/studio.$USER.cg.%p.out"
          _EXTRA_ARGS="-x"
          ;;
        memcheck)
          _CALLGRIND_BINARY=`which valgrind`
          if [ -f /users/rickard/bin/valgrind/bin/valgrind ]; then
              # Use newer version, if available
              _CALLGRIND_BINARY=/users/rickard/bin/valgrind/bin/valgrind
          fi
          if [ -f /users/carmadm/bin/valgrind/bin/valgrind ]; then
              # Use newer version, if available
              _CALLGRIND_BINARY=/users/carmadm/bin/valgrind/bin/valgrind
          fi
          if [ -z "$_CALLGRIND_BINARY" ]; then
              echo "Did not find Valgrind on the system. Check your PATH"
              exit 1
          fi
          export DEBUGGER="$_CALLGRIND_BINARY --leak-check=yes --track-origins=yes"
          echo "Profiler:               `$_CALLGRIND_BINARY --version`"
          _EXTRA_ARGS="-x"
          ;;
        google_cpu)
          if [ -z "$_GOOGLELIB" ]; then
              echo "Did not find Google Perftools on the system."
              exit 1
          fi
          echo "Profiler:               `$_GOOGLELIB/../bin/pprof --version | grep google-perftools`"
          export LD_PRELOAD=$_GOOGLELIB/libprofiler.so
          export CPUPROFILE=/tmp/studio.$USER.cp.$_MARKER.out
          echo "Profiler output:        $CPUPROFILE"
          echo "*** NOTE**** There will be error messages below about LD_PRELOAD. Please ignore them."
          ;;
        google_heap)
          if [ -z "$_GOOGLELIB" ]; then
              echo "Did not find Google Perftools on the system."
              exit 1
          fi
          echo "Profiler:               `$_GOOGLELIB/../bin/pprof --version | grep google-perftools`"
          export LD_PRELOAD=$_GOOGLELIB/libtcmalloc.so
          export HEAPPROFILE=/tmp/studio.$USER.hp.$_MARKER.out
          export HEAPCHECK=normal
          echo "Profiler output:        $HEAPPROFILE"
          echo "*** NOTE**** There will be error messages below about LD_PRELOAD. Please ignore them."
          ;;
        libtcmalloc)
          if [ -z "$_GOOGLELIB" ]; then
              echo "Did not find Google Perftools on the system."
          else
              echo "Using libtcmalloc: `$_GOOGLELIB/../bin/pprof --version | grep google-perftools`"
              export LD_PRELOAD=$_GOOGLELIB/libtcmalloc.so
              echo "*** NOTE**** There will be error messages below about LD_PRELOAD. Please ignore them."
          fi
          ;;
        *)
          echo "Bad choice of profiler"
          exit 0;
          ;;
    esac
}

if [ -f "$HOME/.carmdev" ]; then
    export CARMDEV=1
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

. $CARMUSR/etc/scripts/shellfunctions.sh

#
# Get the command line options and take actions
# 

case $1 in
    -X)
    case $2 in
        c) _PROFILE_TOOL=google_cpu ;;
        h) _PROFILE_TOOL=google_heap ;;
        m) _PROFILE_TOOL=memcheck ;;
        C) _PROFILE_TOOL=callgrind ;;
        q) _PROFILE_TOOL=libtcmalloc ;;
        *) usageText; exit 0 ;;
    esac
    shift 2
    ;;
esac

case $1 in
    -a) CARMUSINGAM=YES
        export CARMUSINGAM
        SK_APP=Tracking
        CARM_PROCESS_NAME=AlertMonitorStudio
        ;;
    -b) CARMUSINGAM=YES
        export CARMUSINGAM
        SK_APP=DayOfOps
        CARM_PROCESS_NAME=AlertMonitorStudioDayOfOps
        ;;
    -t|-r) SK_APP=Tracking
        CARM_PROCESS_NAME=TrackingStudio
        ;;
    -o) SK_APP=DayOfOps
        CARM_PROCESS_NAME=DayOfOpsStudio
        ;;
    -p) SK_APP=Planning
        CARM_PROCESS_NAME=PlanningStudio
        #unset CARM_PRE_PYTHONPATH
        ;;
    -l) SK_APP=Planning
        CARM_PROCESS_NAME=PlanningStudio
        LOOKBACK_SUFFIX=_calibration_lookback
        export LOOKBACK_SUFFIX
        ;;
  -m) SK_APP=PrePlanning
        CARM_PROCESS_NAME=PreStudio
        ;;
    -s) SK_APP=Server ;; # The s-option is just for testing what happens if no SK_APP is set.
    -S|-P) 
        if [[ "$1" = "-P" ]]; then 
            # 1: Log load and save times
            CARM_LOG_PERF_LEVEL=1
            export CARM_LOG_PERF_LEVEL
        fi
        case $2 in
            t) SK_APP=Tracking
               CARM_PROCESS_NAME=TrackingStudio
               ;;
            o) SK_APP=DayOfOps
               CARM_PROCESS_NAME=DayOfOpsStudio
               ;;
            p) SK_APP=Planning
               CARM_PROCESS_NAME=PlanningStudio
               ;;
            m) SK_APP=PrePlanning
               CARM_PROCESS_NAME=PreStudio
               ;;
            *) usageText ; exit 0 ;;
        esac ;;
    -D) if [ -z "$SK_APP" ]; then 
           echo "For this option, the environment variable SK_APP must be defined!"
           exit 0;
        fi ;;
    *) usageText ; exit 0 ;; 
esac
export SK_APP
export CARM_PROCESS_NAME
# Set the default editor
CARM_EDITOR=emacs
export CARM_EDITOR

_EXTRA_ARGS=
if [ -n "$_PROFILE_TOOL" ]; then
  echo "Setting up profiler:    $_PROFILE_TOOL"
  setup_profiler $_PROFILE_TOOL
fi

#exit 1

# Sets CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
if [ -z "$CARMSYS" ]; then
  . $CARMUSR/bin/carmenv.sh
else
  setCarmvars "$SK_APP"
fi

# Adding performance printouts for certain users during SP7
#test_users="46395 ade407 46365 26116 27569 34236 sandberg 39486"
# ade407 = Christoffer Sandberg, Jeppesen
# 46395  = Martin Arwidsson
# 46365  = Mikael Soderberg
# 26116  = Ditte Soderberg
# 27569  = Morden De Lasson
# 34236  = Boi Aarrestad
# 39486  = Cecilie Winderen

if [[ $test_users = *$USER* ]]; then
    PERFORMANCE_TRACE=10
    export PERFORMANCE_TRACE
fi

#export LD_PRELOAD="$HOME/lib/libprofiler.so"
#export CPUPROFILE="/tmp/prof_`date '+%Y%m%d%H%M%S'`.log"
#echo "PROFILING TO $CPUPROFILE !"
start_studio "$@" $_EXTRA_ARGS
