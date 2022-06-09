#!/bin/sh



function setCarmvars() {
  case $1 in
    *)
      CARMSYS=$CARMUSR/current_carmsys_cct
      CARMTMP=$CARMUSR/current_carmtmp_cct
      ;;
  esac

  if [ ! -d "$CARMSYS" ]; then
    echo "***************    ERROR    ********************" 
    echo "          No link to CARMSYS found!"
    echo "           Please set and restart!"
    echo "***************    ERROR    ********************" 
    exit -1
  fi

  if [ ! -d "$CARMTMP" ]; then
    echo "***************    ERROR    ********************" 
    echo "          No link to CARMTMP found!"
    echo "           Please set and restart!"
    echo "***************    ERROR    ********************" 
    exit -1
  fi

  #
  # Source the CONFIG in the SYS to get site environment

  . $CARMSYS/CONFIG #> /dev/null
}
