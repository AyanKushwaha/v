#!/bin/env python
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/getHistStart.py,v 1.4 2009/12/29 11:03:05 adg239 Exp $

"""
This script prints start, end time for historic servers.
It also prints the overlap between servers (should be min. 14days), and
the number of days each server has loaded, should be around 3 months.

"""

import sys, getopt, time, re
import datetime


LOGLINEPATTERN =r'reportserver::startServer::'

def getLogfile(x):
    for host in ('h1crm23a','h1crm24a','h1crm06a'):
        try:
            logFile = 'current_carmtmp/logfiles/reportworker.SAS_RS_WORKER_HISTORIC_'+str(x)+'.carmadm.'+host
            f = open(logFile, 'r')
            f.close()
            return logFile
        except Exception, e:
            pass
            #print "getRSstart error: %s" % (str(e))
    return None

def main(argv):

    print __doc__
    logFile0 = None
    pst = 0
    overlap = 0
    MM={'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
    try:
        regexLOG = re.compile(LOGLINEPATTERN)

        for x in [3,6,9,12,15,18,21,24,27]:
            logFile0 = getLogfile(x)
            if not logFile0 is None:
               res=None
               f = open(logFile0, 'r')
               while res is None:
                   line = f.readline()
                   res = regexLOG.search(line)
               if res:
                   PT='period(Start|End) = '
                   reg=re.compile(PT)
                   d=reg.split(line)
                   start = d[2]
                   end = d[4][:-1]
                   dst=datetime.date(int(start[5:]),MM[start[2:5]],int(start[:2]))
                   det=datetime.date(int(end[5:]),MM[end[2:5]],int(end[:2]))
                   dur=(det-dst).days
                   if pst != 0:
                       overlap=(det-pst).days
                   pst=dst
                   print 'Start: %s End: %s Overlap: %3d Days loaded: %3d' % (start, end, overlap, dur)
               f.close()

    except Exception, e:
        print "getHistStart error: %s" % (str(e))
        sys.exit(3)

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
