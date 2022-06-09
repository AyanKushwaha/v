#!/bin/env python
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/getRSstart.py,v 1.1 2009/12/29 11:08:54 adg239 Exp $

"""
This script prints start, end time for load of data, for report servers.

Options:
    --help
    -p <process>            Last part of process name excl. process no, e.g. PUBLISH or PUBLISH_FUTURE
    -d <directory>          Directory for logfiles, defaults to current_carmtmp_cct

"""

import sys, getopt, time, re
import datetime


STARTPATTERN =r'INFO '
FINISHPATTERN = r'Register got answer: True'

class LogLine(dict):
    """
    Hold parsed info and help with sorting
    """
    def __init__(self, header):
        self._header = header
                                                                                                                    
    def __cmp__(self, other):
        return cmp(other['sortval'], self['sortval'])
                                                                                                                    
    def __str__(self):
        if self['end'] is None:
            return 'RS%d: Start: %s End: %s Time: %s' % (self['rsno'],  self['sortval'], '', '')
        else:
            return 'RS%d: Start: %s End: %s Time: %s' % (self['rsno'],  self['sortval'], self['end'], self['end']-self['sortval'])
                                                                                                                    
    def str_header(self):
        return ', '.join(self._header)
                                                                                                                    
def getLogfile(carmtmp,process,x,x1):
    for host in ('h1crm23a','h1crm24a','h1crm06a'):
        try:
            if x == 0:
                logFile = carmtmp+'/reportworker.SAS_RS_WORKER_'+process+str(x1)+'.carmadm.'+host
            else:
                logFile = carmtmp+'/reportworker.SAS_RS_WORKER_'+process+str(x1)+'.carmadm.'+host+'.'+str(x)
            f = open(logFile, 'r')
            f.close()
            return logFile
        except Exception, e:
            pass
            #print "getRSstart error: %s" % (str(e))
    return ''

def main(argv):

    try:
        opts, args = getopt.getopt(argv[1:], "h:p:d:", ["help","process"])
    except getopt.GetoptError, e:
        print e
        print __doc__
        sys.exit(2)

    print __doc__
    logFile0 = None
    MM={'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
    try:
        regexStart = re.compile(STARTPATTERN)
        regexEnd = re.compile(FINISHPATTERN)

        process='PUBLISH'
        carmtmp='current_carmtmp_cct/logfiles'
        for opt, val in opts:
            if opt == "--help":
                print __doc__
                sys.exit(0)
            if opt in ('-p', '--process'):
                process = val
            if opt in ('-d',):
                carmtmp = val

        loglines = []
        for x in range(0,11):
            for x1 in range(1,3):
                logline = LogLine(['file','sortval','end','rsno']) 
                logFile0 = getLogfile(carmtmp,process,x,x1)
                if logFile0 == '':
                    if x1 == 1:
                        logFile0 = getLogfile(carmtmp,process,x,'')
                        if logFile0 == '':
                            continue
                    else:
                        continue
                #if x == 0:
                #    logFile0 = carmtmp+'/reportworker.SAS_RS_WORKER_'+process+str(x1)+'.carmadm.h1crm23a'
                #else:
                #    logFile0 = carmtmp+'/reportworker.SAS_RS_WORKER_'+process+str(x1)+'.carmadm.h1crm23a.'+str(x)
                if not logFile0 is None:
                   resStart=None
                   resEnd=None
                   start=None
                   end=None
                   f = open(logFile0, 'r')
                   line='X'
                   while resEnd is None and line != '':
                       line = f.readline()
                       #print 'Read line'+line
                       if resStart is None:
                           resStart = regexStart.search(line)
                           datoStart=line.split()
                           time=datoStart[4].split(':')
                           start = datetime.datetime(int(datoStart[3]),MM[datoStart[2].upper()],int(datoStart[1]),int(time[0]),int(time[1]),int(time[2]))
                       if not resStart is None:
                           resEnd = regexEnd.search(line)
                           if resEnd:
                               datoEnd=line.split()
                               time=datoEnd[4].split(':')
                               end = datetime.datetime(int(datoEnd[3]),MM[datoEnd[2].upper()],int(datoEnd[1]),int(time[0]),int(time[1]),int(time[2]))
                   logline['sortval'] = start
                   logline['end'] = end
                   logline['rsno'] = x1
                   f.close()
                loglines.append(logline)
        loglines.sort()
        #print loglines
        for x in loglines:
             print x

    except Exception, e:
        print "getRSstart error: %s" % (str(e))
        raise
        sys.exit(3)

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
