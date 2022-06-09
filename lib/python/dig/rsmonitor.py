#!/bin/env python

"""
This script monitors startup of report workers. It sends a mail if
RS didn't finish loading within a certain time. It also sends a mail
if there is a report worker that is close to exceeding the 4GB memory
limit for 32-bit processes.

Options:
    --help
    -h <hours>              Scan window, the script only reports errors
                            occurred during the last <hours> + <minutes>
                            Default <hours>=1
    -m <memory>             Hi RS worker memory usage
    -l <logfile>            Logfile of the actual worker process

Exit codes:
    0 - Normal exit
    2 - Argument error
    3 - Other runtime errors
"""

import sys, getopt, datetime, time, re
from dig.intgutils import IntgServiceConfig
from carmensystems.dig.support.transports.mail import Transport


LOGLINEPATTERN =r'dig.rs_init: INFO prepare\(\) ... finished'

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "h:m:l:", ["help","memory"])
    except getopt.GetoptError, e:
        print e
        print __doc__
        sys.exit(2)

    memory = 0
    memmax = 3900000
    logFile0 = None
    maxtime = 3000 # 50 minutes
    sleeptime = 60
    try:
        regexLOG = re.compile(LOGLINEPATTERN)
        for opt, val in opts:
            if opt == "--help":
                print __doc__
                sys.exit(0)
            if opt in ('-m', '--memory'):
                memory = int(val)
            if opt in ('-l',):
                logFile0 = val

        process = logFile0.split('.')[1]
        if memory > memmax:
            subject = "RS Memory high"
            msg = "%s Memory max exceeded: %d" % (process, memory)
            sendMail(subject, msg)
        if not logFile0 is None:
            time.sleep(60)
            tottime = 0
            while (tottime < maxtime):
                time.sleep(sleeptime)
                now = datetime.datetime.now()
                tottime += sleeptime
                #print "%s RSMON Checking for start condition" % (now)
                #sys.stdout.flush()
                f = open(logFile0, 'r')
                log = f.read().strip()
                res = regexLOG.search(log)
                f.close()
                if res:
                    print "%s RSMON found start condition" % (now)
                    return
                if log.endswith("Got signal 15, quit") or \
                   log.endswith("Forward signal 15 to pgrp") or \
                   log.endswith("superceded, about to exit(16)"):
                    print "%s Process %s ended, RSMON exiting..." % (now, process)
                    return
            msg = "%s Report Worker has not started within %d minutes" % (process, int(maxtime/60))
            print "%s %s" % (now, msg)
            sendMail("Report Server failed to start", msg)

    except Exception, e:
        print "RSMON error: %s" % (str(e))
        sys.exit(3)

def sendMail(subject, msg):
    config = IntgServiceConfig()
    (key, mailhost) = config.getProperty("dig_settings/mail/host")
    (key, mailport) = config.getProperty("dig_settings/mail/port")
    (key, mailfrom) = config.getProperty("dig_settings/mail/from")
    (key, mailto) = config.getProperty("dig_settings/mail/to")
    mailer = Transport(host=mailhost, port=int(mailport), defaultFrom=mailfrom,
                    defaultSubject=subject)
    mailer._send(None, msg, 'text/plain', 'latin1', mailto)

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
