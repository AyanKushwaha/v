#!/bin/env python


"""
This utility program can be used for replaying messages previously
recorded in SKLog-format. Messages are normally replayed with the
same pace they were originally recorded, thereby simulating a live
feed into the system.

Messages in SKLog-format have been prepended with a special timestamp
header (SKLog-header). 
The following components produces messages in SKLog-format:
    mqcapture.pl      - Stand-alone program that listens to an MQ queue 
                        and records all incoming messages.
    MessageRecorder   - DIG message handler that records all incoming 
                        messages on the DIG channel.
    SKLogFormatter    - DIG error notifyer that records the original
                        incoming MQ message in the channel, in case of 
                        error.
The following components can read messages in SKLog-format:
    SKLogParser       - This program
    SKLogReplayFilter - DIG message handler that delays the message
                        according to the difference between the SKLog
                        timestamp and current time.

User may run the program in two different modes. Which mode the program
runs depends on the options specified (see below).
Normal mode - Put all messages onto queue without delay.
              In this case, if messages are to be consumed by DIG, the
              SKLogReplayFilter may be placed as first messagehandler in
              the DIG channel to handle delays. If no delays are wanted,
              use the -x flag (see below).
Delay mode -  Put messages onto queue one by one with a proper delay 
              inbetween. In this case an absolute time, a time offset 
              or a timeserver must be specified in order to locate
              proper log entries and calculate correct delays. 
              Optionally a time factor may also be specified. Note that
              also in Delay mode the --from/--to options (see below) can
              be used to "catch up" older entries prior to the simulated 
              time.

Usage:
    SkLogParser.py [[-f fileprefix]|[[-h host] -m manager -q queue [-r replyq] [-c channel] [-p port ] [-u altuser] [-e encoding]]] [-n maxmsgs] [-x] [--from time [--to time]] [[--timeservice ts|--starttime time|--timeoffset secs] [--timefactor num][--threshold secs]] [<logfile>]

Options:
    --help              
    -h <host>           MQ server (Default: localhost)
    -m <manager>        MQ queue manager
    -q <queue>          MQ queue
    -r <reply queue>    MQ reply queue (Optional)
    -p <port>           MQ port (Default: 1414)
    -c <channel>        MQ channel (Default: SYSTEM.DEF.SVRCONN)
    -u <altuser>        MQ alternate user (Optional)
    -e <encoding>       MQ encoding. Valid values: [utf-8|latin-1|binary].
                        Default: latin-1
    -f <fileprefix>     Write messages to file instead of MQ. No need to
                        specify any of the above MQ parameters.
    -n <maxmsgs>        Max number of messages (Optional)
    -x                  Exclude SKLog-header. Automatically excluded if
                        running in Delay mode (see above).
    -d                  Debug mode
    --from <str>        Time string YYYY-mm-ddTHH:MM:SS. (Optional) See --to  
    --to <str>          Time string YYYY-mm-ddTHH:MM:SS. (Optional) Entries 
                        in the from-to interval are processed without delay,
                        regardless if in Delay mode or not. In Delay mode
                        however, these options only have effect if the start-
                        end interval is before the simulated start time.
The following options only apply to Delay mode:
    --timeservice <ts>  Timeserver service name (Optional)
    --starttime <str>   Logical start time YYYY-mm-ddTHH:MM:SS (Optional)
    --timeoffset <secs> Offset time in seconds. Relative to current time
                        (Optional).
    --timefactor <num>  Logical time factor. Time may progress below
                        or above realtime speed. Only applicable if
                        --starttime or --timeoffset is specified (Default: 1)
    --threshold <secs>  Delay threshold. Do not delay if delay time turns
                        out to be smaller than this. (Default 0.1)
    -s                  Silent output (like Normal mode)
Please note that timeservice, starttime and timeoffset are mutually exclusive.

Parameters:
    logfile             Path to file with recorded livefeeds. 'logfile' may
                        also be a directory in which case it is assumed that
                        it contains files named <queue>_LIVE<date>.log, where
                        <date> is in format YYYYmmdd. (Optional.) Default is
                        directory /carm/proj/skcms/migration/livefeeds
                        

===============================================================================                        
Examples Normal mode:
   --------------------------
   SkLogParser.py -h taramajima -m MQTRACK.SK -p 1415 -q CQFREQ 
      -r APA $CARMTMP/test1.txt
   
   Put all entries from test1.txt as RequestMessages on queue CQFREQ without
   delays and including the SKLog-headers. Reply queue APA is added to the
   MQMD-headers, telling the receiving application where to put the response
   messages.
   
   --------------------------
   SkLogParser.py -h taramajima -m MQTRACK.SK -p 1415 -q CQFMVTD 
      -x $CARMTMP/test2.txt
   
   Put all entries from test2.txt on queue CQFMVTD without delays and without
   SKLog-headers.
   
   --------------------------
   SkLogParser.py -h taramajima -m MQTRACK.SK -p 1415 -q CQFMVTD -x 
      --from 2008-02-20T00:00:00 --to 2008-02-26T00:00:00 $CARMTMP/test2.txt
      
   Put entries from test2.txt with timestamps from 20Feb until and including 
   25Feb on queue CQFMVTD without delays and without SKLog-headers.
   
   --------------------------
   SkLogParser.py -h taramajima -m MQTRACK.SK -p 1415 -q CQFMVTD -x 
      --from 2008-02-01T00:00:00
      --to 2008-03-01T00:00:00 ~/mydir

   Put entries with timestamps from 1Feb until and including 25Feb from all 
   files ~/mydir/CQFMVTD_LIVE*.log on queue CQFMVTD without delays and
   without SKLog-headers.
   
===============================================================================
Examples Delay mode:
   --------------------------
   SkLogParser.py -h taramajima -m MQTRACK.SK -p 1415 -q CQFREQ -r APA 
      --starttime 2008-02-01T15:05:30
      
   Put entries with timestamps larger than or equal to 1Feb 15:05:30 from 
   all files /carm/proj/skcms/migration/livefeeds/CQFREQ_LIVE*.log on
   queue CQFREQ without SKLog-headers.
   The program simulates the time progressing from 2008-02-01 15:05:30 and
   puts each message at the point in time given by the SKLog-header timestamp. 
   It starts to read entries in file CQFREQ_LIVE20080201.log (if available)
   and continues with subsequent files in order of the datestamp in the
   filename. Reply queue APA is added to the MQMD-headers, telling the
   receiving application where to put the response messages.
   
   --------------------------
   SkLogParser.py -h taramajima -m MQTRACK.SK -p 1415 -q CQFREQ -r APA 
      --from 2008-01-15T00:00:00 --starttime 2008-02-01T15:05:30
      
   As above, but the program will also put all entries from 
   /carm/proj/skcms/migration/livefeeds/CQFREQ_LIVE*.log with timestamps 
   between 15Jan and 1Feb 15:05:30 onto the queue without delays.
   
   --------------------------
   SkLogParser.py -h taramajima -m MQTRACK.SK -p 1415 -q CQFREQ -r APA 
      --from 2008-01-15T00:00:00 --starttime 2008-02-01T15:05:30 
      --timefactor 2
      
   As above, but the simulated time will progress at double normal speed.
   
   --------------------------
   SkLogParser.py -h taramajima -m MQTRACK.SK -p 1415 -q CQFMVTD 
      --timeservice time
   
   Put entries from the simulated time and onwards from all files 
   /carm/proj/skcms/migration/livefeeds/CQFMVTD_LIVE*.log on queue CQFMVTD.
   The simulated time is given by a time server configured with service 
   name 'time'.
"""

import sys, getopt, re, os, glob
import time, datetime
import xmlrpclib
from carmensystems.dig.jmq import jmq
from utils.ServiceConfig import ServiceConfig

SIM_NODELAY = 1     # Normal mode
SIM_TIMESERVER = 2  # Delay mode - timeserver
SIM_STARTTIME = 3   # Delay mode - absolute starttime specified
SIM_OFFSET = 4      # Delay mode - time offset relative to current time

class SKLogParser:
    TS_PAT = r'SKLogEntry;(\d\d\d\d\-\d\d\-\d\d\T\d\d\:\d\d\:\d\d)$'

    def checkMQError(self,err,who, doThrow = True):
        if not err:
            return ''
        else:
            if err == -1:
                errMsg = "Memory ERROR"
            else:
                errMsg = DigMQ.qerr_string(err,who)
            if not len(errMsg):
                return errMsg
            if errMsg.find('ERROR') < 0:
                # is a warning
                if self.loglevel >= 0:
                    print >>sys.stderr,errMsg
                return errMsg
            if doThrow:
                raise RuntimeError,errMsg
            else:
                print >>sys.stderr,errMsg
                return errMsg

    def __init__(self, mqserver='', mqmanager='', mqqueue='', mqreplyq=None, mqchannel='', mqport='', mqaltuser='', mqenc='', logfilename='', fileprefix='', noOfMsgs=-1, exclHeader=False, intervalFrom=None, intervalTo=None, timeservice=None, starttime=None, timeoffset=None, timefactor=None, threshold=None, verbose=False, debug=False):
        self.mqserver = mqserver
        self.mqmanager = mqmanager
        self.mqqueue = mqqueue
        self.mqreplyq = mqreplyq
        self.mqchannel = mqchannel
        self.mqport = int(mqport)
        self.mqaltuser = mqaltuser
        self.mqencoding = mqenc
        self.logfilename = logfilename
        self.filePrefix = fileprefix
        self.useMQ = len(fileprefix) == 0
        self.noOfMsgs = noOfMsgs
        self.exclHeader = exclHeader
        self.intervalFromStr = intervalFrom
        self.intervalToStr = intervalTo
        self.tsMin = '9'
        self.tsMax = '0'
        self.mqm = None
        self.mqq = None
        self._filecounter = 1
        self._msgCount = 0
        self.timeservice = timeservice
        self.timeserver = None
        self.simMode = SIM_NODELAY
        self.verbose = False
        self.threshold = float(threshold)
        self.runstart = time.time()
        self.timefactor = float(timefactor)
        self._last_ts_secs = 0
        self.debug = debug
        self.skipahead = True
        
        self.intervalFrom = None
        self.intervalTo = None
        if self.intervalFromStr is not None:
            self.intervalFrom = time.mktime(time.strptime(self.intervalFromStr, "%Y-%m-%dT%H:%M:%S"))
        if self.intervalToStr is not None:
            self.intervalTo = time.mktime(time.strptime(self.intervalToStr, "%Y-%m-%dT%H:%M:%S"))

        if timeservice:
            self.simMode = SIM_TIMESERVER
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
            self.simMode = SIM_STARTTIME
            self.utcstart = time.time()
            self.runstart = time.mktime(time.strptime(starttime, "%Y-%m-%dT%H:%M:%S"))
            self.timefactor = float(timefactor)
        elif timeoffset:
            self.simMode = SIM_OFFSET
            self.utcstart = time.time()
            self.runstart = self.utcstart + int(timeoffset)
            self.timefactor = float(timefactor)
                        
        if self.simMode != SIM_NODELAY:
            self.exclHeader = True
            self.verbose = verbose
            self.skipahead = True


    def start(self):
        print "SKLogParser: Started."
        # Ignore intervalFrom if it comes after simulated time
        if self.simMode != SIM_NODELAY and self.intervalFrom is not None:
            if self.intervalFrom >= self.now():
                self.intervalFrom = None
        try:
            if self.useMQ:
                self.mqm = jmq.Connection(host=self.mqserver, port=self.mqport, manager=self.mqmanager, channel=self.mqchannel)
                self.mqq = self.mqm.openQueue(queueName=self.mqqueue, mode='w', altUser=self.mqaltuser)
            if os.path.isfile(self.logfilename):
                self.readLogEntries(self.logfilename)
            elif os.path.isdir(self.logfilename):
                if self.intervalFrom is None:
                    if self.simMode == SIM_NODELAY:
                        datestamp = None
                    else:
                        datestamp = time.strftime("%Y%m%d",time.gmtime(self.now()))
                else:
                    datestamp = self.intervalFromStr[:10].replace('-','')

                filename = self.getNextFilename(datestamp=datestamp)
                while True:
                    self.readLogEntries(filename)
                    filename = self.getNextFilename(filename=filename)
            else:
                raise Exception("Cannot open %s" % self.logfilename)
        except Exception,e:
            sys.stderr.write("%s\n" % str(e))
            if self.useMQ and self.mqm is not None:
                self.mqm.rollback()

        print "SKLogParser: Finished."
        if self.useMQ:
            self.mqq.close()
            self.mqm.disconnect()
            print 'Put %d message(s) to queue %s:%s' % (self._msgCount, self.mqmanager, self.mqqueue)
            print ' (%s -- %s)' % (self.tsMin, self.tsMax)
        else:
            print 'Wrote %d message(s) files with prefix %s' % (self._msgCount, self.filePrefix)
            print ' (%s -- %s)' % (self.tsMin, self.tsMax)


    def getNextFilename(self, filename=None, datestamp=None):
        try:
            files = glob.glob(os.path.join(self.logfilename, "%s_LIVE*log" % self.mqqueue))
            files.sort()
            if filename:
                index = files.index(filename)
                return files[index+1]
            else:
                for file in files:
                    index = file.find('_LIVE')
                    datestr = file[index+5:index+13]
                    if datestamp is None or datestr >= datestamp:
                        return file
                raise Exception("No logfiles available for %s" % datestamp)
        except:
            raise Exception("No more logfiles available...")


    def now(self):
        if self.simMode == SIM_NODELAY:
            now = time.time()
        else:
            now = self.runstart + (time.time() - self.utcstart) * self.timefactor
        return now
        

    def readLogEntries(self, livefeedfile):
        if self.verbose:
            print "Processing logfile %s" % livefeedfile
        logfile = open(livefeedfile, 'r')

        loglines = []
        allDone = False
        endOfFile = False
        entryFound = False
        if not self.verbose:
            sys.stderr.write(" (100 messages per dot. %s)\n\tWorking: " % os.path.basename(livefeedfile))
        else:
            sys.stderr.write("\n")
        while not allDone:
            logline = logfile.readline()
            if logline == '' or (self.noOfMsgs >= 0 and self._msgCount >= self.noOfMsgs):
                allDone = True
                if entryFound:
                    sendit = self.preprocess(self._curHeader)
                    if sendit:
                        self.process(''.join(loglines))
                    continue
                else:
                    continue
                                    
            m = re.match(self.TS_PAT, logline)
            if m:
                if not entryFound:
                    if self.exclHeader:
                        loglines = []
                    else:
                        loglines = [logline]
                    entryFound = True
                else:
                    sendit = self.preprocess(self._curHeader)
                    if sendit:
                        self.process(''.join(loglines))
                    if self.exclHeader:
                        loglines = []
                    else:
                        loglines = [logline]
                self._curHeader = logline
            else:
                if not entryFound and self._msgCount == 0:
                    continue
                loglines.append(logline)
    
        logfile.close()
        if (self._filecounter - 1) % 5000 != 0:
            sys.stderr.write(" (%08d)\n" % (self._filecounter - 1))
            sys.stderr.flush()
        if self.useMQ:
            self.mqm.commit()
        

    def preprocess(self, header):
        arr = header.rstrip('\n').split(';')
        self._cur_ts_str = arr[1]
        if self.simMode == SIM_NODELAY and self.intervalFrom is None:
            return True

        # Calculate delay period
        ts_secs  = time.mktime(time.strptime(self._cur_ts_str[0:19], "%Y-%m-%dT%H:%M:%S"))
        if len(self._cur_ts_str) > 19:
            # add microsecs
            ts_secs += float(self._cur_ts_str[20:24]) * 0.0001
        if ts_secs <= self._last_ts_secs:
            ts_secs = self._last_ts_secs + 0.001
        self._last_ts_secs = ts_secs

        now = self.now()
        sleep_time = (ts_secs - now) / self.timefactor
        if self.verbose and self.debug:
            sys.stdout.write("\nts_str='%s' delay: (ts_secs %f - now %f ) / factor %f = sleep %f\n" % (self._cur_ts_str, ts_secs, now, self.timefactor, sleep_time))

        if sleep_time > 0:
            self.skipahead = False
        if self.skipahead and self.intervalFrom is not None and ts_secs >= self.intervalFrom:
            if self.intervalTo is None or ts_secs < self.intervalTo:
                if self.verbose:
                    sys.stdout.write("forwarding msg %s within specified interval\n" % self._cur_ts_str)
                    sys.stdout.flush()
                return True
            
        if self.simMode != SIM_NODELAY and sleep_time > self.threshold:
            if self.verbose:
                print "delay: %f - sleeping... (next ts %s)" % (sleep_time,self._cur_ts_str)
            time.sleep(sleep_time)
        else:
            if self.verbose:
                if self.skipahead:
                    if self.debug:
                        sys.stdout.write("skipping msg %s (too early)\n" % self._cur_ts_str)
                else:
                    sys.stdout.write("delay: %f - forwarding msg without delay\n" % sleep_time)
        if self.verbose:
            sys.stdout.flush()
        if self.skipahead:
            return False
        return True

        
    def process(self, logEntry):
        logEntry = logEntry.rstrip('\n')
        if self.useMQ:
            if self.mqreplyq:
                m = jmq.Message(content=logEntry, encoding=self.mqencoding, msgType=jmq.Message.requestMessageType, replyToQ=self.mqreplyq, replyToQMgr=self.mqmanager)
            else:
                m = jmq.Message(content=logEntry, encoding=self.mqencoding)
            self.mqq.writeMessage(m)
        else:
            f = open('%s.%07d' % (self.filePrefix, self._filecounter), 'w')
            f.write(logEntry)
            f.close()

        if self.useMQ and self.simMode != SIM_NODELAY:
            self.mqm.commit()
        if self._filecounter % 100 == 0:
            if not self.verbose:
                sys.stderr.write(".")
                sys.stderr.flush()
            if self.useMQ and self.simMode == SIM_NODELAY:
                self.mqm.commit()
        if self._filecounter % 5000 == 0:
            if not self.verbose:
                sys.stderr.write(" (%08d)\n" % (self._filecounter))
                sys.stderr.write("\tWorking: ")
                sys.stderr.flush()
        self.statistics()
        
    def __setattr__(self, attr, value):
        self.__dict__[attr] = value        
        
    def statistics(self):
        if self._cur_ts_str < self.tsMin:
            self.tsMin = self._cur_ts_str
        if self._cur_ts_str > self.tsMax:
            self.tsMax = self._cur_ts_str
        self._filecounter += 1
        self._msgCount += 1
            
def usage (progname, msg):
    print "%s" % msg
    print "%s [[-f fileprefix]|[[-h host] -m manager -q queue [-c channel] [-p port ] [-u altuser] [-e encoding]]] [-n maxmsgs] [-x] [--from time [--to time]] [[--timeservice name | --starttime time | --timeoffset secs] [--timefactor num][--threshold secs]] [<logfile>]" % progname
    sys.exit(0)

def main(args):
    p = {}
    mqs='localhost'
    mqm=''
    mqq=''
    mqr=None
    mqc='SYSTEM.DEF.SVRCONN'
    mqp=1414
    mqa=''
    mqenc='latin-1'
    fileprefix=''
    noOfMsgs = -1
    exclHeader = False
    intervalFrom = None
    intervalTo = None
    timeservice = None
    starttime = None
    timeoffset = None
    timefactor = 1
    threshold = 0.1
    delayMode = False
    assumeDelayMode = False
    verbose = True
    debug = False
    
    try:
        optlist, params = getopt.getopt(args[1:], 'h:m:q:r:c:p:u:e:f:n:xsd', 
                ["from=","to=","timeservice=","starttime=","timeoffset=","timefactor=","threshold=","help"])
        for opt in optlist:
            if opt[0] == '--help':
                print __doc__
                return
            if opt[0] == '-f':
                fileprefix=opt[1]
            if opt[0] == '-h':
                mqs=opt[1]
            if opt[0] == '-m':
                mqm=opt[1]
            if opt[0] == '-q':
                mqq=opt[1]
            if opt[0] == '-r':
                mqr=opt[1]
            if opt[0] == '-c':
                mqc=opt[1]
            if opt[0] == '-p':
                mqp=int(opt[1])
            if opt[0] == '-u':
                mqa=opt[1]
            if opt[0] == '-e':
                mqenc=opt[1]
            if opt[0] == '-n':
                noOfMsgs = int(opt[1])
            if opt[0] == '-x':
                exclHeader = True
            if opt[0] == '--from':
                intervalFrom = opt[1]
            if opt[0] == '--to':
                intervalTo = opt[1]
            if opt[0] == '--timeservice':
                timeservice = opt[1]
                if delayMode:
                    usage(args[0], 'error: only one of timeservice, starttime and timeoffset may be specified')
                delayMode = True
            if opt[0] == '--starttime':
                starttime = opt[1]
                if delayMode:
                    usage(args[0], 'error: only one of timeservice, starttime and timeoffset may be specified')
                delayMode = True
            if opt[0] == '--timeoffset':
                timeoffset = opt[1]
                if delayMode:
                    usage(args[0], 'error: only one of timeservice, starttime and timeoffset may be specified')
                delayMode = True
            if opt[0] == '--timefactor':
                timefactor = opt[1]
                assumeDelayMode = True
            if opt[0] == '--threshold':
                threshold = opt[1]
                assumeDelayMode = True
            if opt[0] == '-s':
                verbose = False
            if opt[0] == '-d':
                debug = True

    except getopt.GetoptError, e:
        print >> sys.stderr, e
        sys.exit(1)

    if len(fileprefix) == 0:
        if len(mqq) == 0 or len(mqm) == 0:
            usage(args[0], 'error: missing -m or -q')

    if assumeDelayMode and not delayMode:
        usage(args[0], 'error: in delay mode you must specify timeservice, starttime or timeoffset')
        
    logfilename = '/carm/proj/skcms/migration/livefeeds'
    if len(params) > 0:
        logfilename = params[0]
    
    parser = SKLogParser(mqserver=mqs, mqmanager=mqm, mqchannel=mqc, 
            mqqueue=mqq, mqreplyq=mqr, mqaltuser=mqa, mqport=mqp, mqenc=mqenc,
            logfilename=logfilename, fileprefix=fileprefix,
            noOfMsgs=noOfMsgs, exclHeader=exclHeader,
            intervalFrom=intervalFrom, intervalTo=intervalTo,
            timeservice=timeservice, starttime=starttime, timeoffset=timeoffset,
            timefactor=timefactor, threshold=threshold,
            verbose=verbose, debug=debug)
    parser.start()
        
if __name__ == "__main__":
    main(sys.argv)

