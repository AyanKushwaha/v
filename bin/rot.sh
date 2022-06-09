#!/bin/sh
                                                                                                                 
                                                                                                                 
if [ $# != 3 ]; then
  echo "Script to find ROTs for a certain AcReg in a logfile"
  echo "Usage: $0 <date> <acreg> <logfile>"
  echo "    date: YYMMDD"
  echo "    acreg: LNRFF"
  echo "    logfile: current_carmtmp/logfiles/DIG/CQFMVTD20090101.log"
  exit
fi
                                                                                                                 
                                                                                                                 
awk -v dt="$1$2" ' BEGIN { lno = 0 }
/SKLog/    { lno = 0; }
{ msg[lno] = $0; lno = lno + 1 }
$0 ~ dt    { for (x=0; x<lno;x++) print msg[x]; getline; print $0 }
' $3
                                                                                                                 
