#!/bin/sh
                                                                                                                 
if [ $# != 3 ]; then
        echo "Script to find all ASMs regarding a certain flt in a logfile"
        echo "Usage: $0 <fltno> <date> <logfile>"
        echo "    fltno: 0480"
        echo "    date: DDMMMYY (20DEC08)"
        echo "    logfile: current_carmtmp/logfiles/DIG/CQFMVTD20090101.log"
  exit
fi
                                                                                                                 
                                                                                                                 
awk -v dt="SK$1/$2" ' BEGIN { found="false"; lno = 0 }
/SKLog/    { if (found=="true") { for (x=0; x<lno;x++) print msg[x] }; found="false"; lno = 0; }
{ msg[lno] = $0; lno = lno + 1 }
$0 ~ dt    { found="true"; }
' $3
                                                                                                                 
