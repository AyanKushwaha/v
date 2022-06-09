#!/bin/env python

"""
This utility program can be used for replaying previously recorded 
file feeds. File feeds are subscribe interfaces fed by files normally
transfered from an external system by means of ftp. 
For queue based feeds please see utility program SKLogParser.py.

The program copies files from a source library to a target location
from where they are imported and processed by DIG channels in the CMS.
As time progresses the program locates files due for copy by looking
Each file in the source library must have a timestamp as part of its
filename according to the following scheme: <type><timestamp><ext>,
e.g. FIA080312.TXT.
Time progress can be simulated in one of three ways: 
absolute time, time offset or a timeserver (see options below).

Usage:
    SKFileFeed.py --timeservice ts|--starttime time|--timeoffset secs [--timefactor num] [-s <sourcedir>] [-t <targetdir>]

Options:
    --help              
    -d                  Debug mode
    -s                  Source directory with recorded file feeds.
                        Default:
                        /carm/proj/skcms/migration/livefeeds/ftp/imported
    -t                  Target directory
                        Default:
                        /opt/Carmen/CARMUSR/CMS/nf_sk_stab/current_carmtmp/ftp/in
    --timeservice <ts>  Timeserver service name (Optional)
    --starttime <str>   Logical start time YYYY-mm-ddTHH:MM:SS (Optional)
    --timeoffset <secs> Offset time in seconds. Relative to current time
                        (Optional). Default 0.
    --timefactor <num>  Logical time factor. Time may progress below
                        or above realtime speed. Only applicable if
                        --starttime or --timeoffset is specified (Default: 1)
Please note that timeservice, starttime and timeoffset are mutually exclusive.

                        

===============================================================================                        
Examples:
   --------------------------
   SKFileFeed.py --timeservice time -t $CARMTMP/ftp/in
      
   The program copies files from 
   /carm/proj/skcms/migration/livefeeds/ftp/imported to $CARMTMP/ftp/in
   at points in time corresponding to the file timestamps.
   Time progress is simulated by a time server.
   
   --------------------------
   SKFileFeed.py -t $CARMTMP/ftp/in
      
   As above, but time is not simulated. Time progresses in 'reltime'.
   
"""

import sys, getopt, os, glob, shutil
import time, datetime
import xmlrpclib
from utils.ServiceConfig import ServiceConfig

class SKFileFeed:

    def __init__(self, sourceDir, targetDir, timeservice=None, starttime=None, timeoffset=None, timefactor=None, debug=False):
        self.sourceDir = sourceDir
        self.targetDir = targetDir
        self.timeservice = timeservice
        self.timeserver = None
        self.runstart = time.time()
        self.timefactor = float(timefactor)
        self.debug = debug
        self.sleep_secs = 10
        self.sent = []
        self._count = 0

        self.jobs = [
            Job(name='FIA', sendTime='03:00'),
            Job(name='CUR', sendTime='08:00'),
            Job(name='ucTI1',sendTime='02:00', stripTS=True),
            Job(name='OAA')
        ]

        if timeservice:
            config = ServiceConfig()
            tsUrl = config.getServiceUrl(timeservice)
            if not tsUrl:
                sys.stderr.write("Cannot find url for timeserver '%s'\n" % timeservice)
                sys.exit(2)
            try:
                tsProxy = xmlrpclib.ServerProxy(tsUrl)
                te = tsProxy.carmensystems.xmlrpc.timebaseserver.get()
                self.runstart = te['logical']
                self.utcstart = te['utc_start']
                self.timefactor = te['factor']
            except:
                sys.stderr.write("Failed to connect to TimeServer %s" % tsUrl)
                sys.exit(2)
        elif starttime:
            self.utcstart = time.time()
            self.runstart = time.mktime(time.strptime(starttime, "%Y-%m-%dT%H:%M:%S"))
            self.timefactor = float(timefactor)
        else:
            self.utcstart = time.time()
            self.runstart = self.utcstart + int(timeoffset)
            self.timefactor = float(timefactor)

    def start(self):
        self.log("SKFileFeed: Started.")
        try:
            while True:
                for job in self.jobs:
                    files = self.getNextFile(job)
                    for file in files:
                        destFilename = job.getDestFilename(file)
                        shutil.copy2(file, os.path.join(self.targetDir,destFilename))
                        self.log("Copied file '%s'" % file)
                        self.sent.append(file)
                        self._count += 1
                time.sleep(self.sleep_secs)
        except Exception,e:
            sys.stderr.write("%s\n" % str(e))

        self.log("SKFileFeed: Finished.")
        self.log('Copied %d files' % (self._count))


    def getNextFile(self, job):
        toSend = []
        files = glob.glob(os.path.join(self.sourceDir, "%s*%s" % (job.name,job.ext)))
        for file in files:
            try:
                sendTime = job.getSendTime(file)
            except Exception,e:
                self.log("ERROR: Cannot parse timestamp of '%s' error: %s" % (file, str(e)))
                continue
            if abs(sendTime - self.now()) <= self.sleep_secs * self.timefactor:
                if self.sent.count(file) == 0:
                    toSend.append(file)
        return toSend


    def now(self):
        now = self.runstart + (time.time() - self.utcstart) * self.timefactor
        return now

    def log(self, txt):
        print txt

    def logdebug(self, txt):
        if self.debug:
            self.log(txt)


class Job:
    def __init__(self, name, sendTime=None, tsFormat="%y%m%d", stripTS=False, ext='.TXT'):
        self.name = name
        self.sendTime = sendTime
        self.tsFormat = tsFormat
        self.stripTS = stripTS
        self.ext = ext

    def getDestFilename(self, path):
        base = os.path.basename(path)
        if not self.stripTS:
            return base
        return self.name + self.ext

    def getSendTime(self, path):
        base = os.path.basename(path)
        tsStr = base[len(self.name):-len(self.ext)]
        ts_tm = time.strptime(tsStr, self.tsFormat)
        if not self.sendTime is None:
            # Configured sendTime overrides time of day
            ts_tm = (
                    ts_tm[0],
                    ts_tm[1],
                    ts_tm[2],
                    int(self.sendTime.split(':')[0]),
                    int(self.sendTime.split(':')[1]),
                    0,
                    ts_tm[6],
                    ts_tm[7],
                    ts_tm[8]
                    )
        return time.mktime(ts_tm)


def usage (progname, msg):
    print "%s" % msg
    print "%s --timeservice name | --starttime time | --timeoffset secs [--timefactor num] [-s sourceDir] [-t targetDir]" % progname
    sys.exit(0)

def main(args):
    timeservice = None
    starttime = None
    timeoffset = 0
    timefactor = 1
    debug = False
    sourceDir = None
    targetDir = None
    simspc = False
    
    try:
        optlist, params = getopt.getopt(args[1:], 's:t:d', 
                ["timeservice=","starttime=","timeoffset=","timefactor=","help"])
        for opt in optlist:
            if opt[0] == '--help':
                print __doc__
                return
            if opt[0] == '--timeservice':
                if simspc:
                    usage(args[0], 'error: only one of timeservice, starttime and timeoffset may be specified')
                simspc = True
                timeservice = opt[1]
            if opt[0] == '--starttime':
                if simspc:
                    usage(args[0], 'error: only one of timeservice, starttime and timeoffset may be specified')
                simspc = True
                starttime = opt[1]
            if opt[0] == '--timeoffset':
                if simspc:
                    usage(args[0], 'error: only one of timeservice, starttime and timeoffset may be specified')
                simspc = True
                timeoffset = opt[1]
            if opt[0] == '--timefactor':
                timefactor = opt[1]
            if opt[0] == '-s':
                sourceDir = opt[1]
            if opt[0] == '-t':
                targetDir = opt[1]
            if opt[0] == '-d':
                debug = True

    except getopt.GetoptError, e:
        print >> sys.stderr, e
        sys.exit(1)

    if sourceDir is None:
        sourceDir = '/carm/proj/skcms/migration/livefeeds/ftp/imported'
    if targetDir is None:
        targetDir = '/opt/Carmen/CARMUSR/CMS/nf_sk_stab/current_carmtmp/ftp/in'
    
    feeder = SKFileFeed(sourceDir,targetDir,timeservice,starttime,timeoffset,timefactor,debug)
    feeder.start()
        
if __name__ == "__main__":
    main(sys.argv)

