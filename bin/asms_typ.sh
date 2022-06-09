#!/bin/sh
                                                                                                                 
if [ $# != 2 ]; then
        echo "Script to find ASMs of a certain type in a logfile"
        echo "Usage: $0 <type> <logfile>"
        echo "    type: EQT"
        echo "    logfile: current_carmtmp/logfiles/DIG/CQFMVTD20090101.log"
  exit
fi
                                                                                                                 
                                                                                                                 
awk -v dt="$1" ' BEGIN { found="false"; lno = 0 }
/SKLog/    { if (found=="true") { for (x=0; x<lno;x++) print msg[x] }; found="false"; lno = 0; }
{ msg[lno] = $0; lno = lno + 1 }
$0 ~ dt    { found="true"; }
' $3
                                                                                                                 

