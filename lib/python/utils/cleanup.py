#!/bin/env python

#########################################
# Copyright Jeppesen Systems AB

import os, sys, getopt, glob, datetime
from utils.ServiceConfig import ServiceConfig


__version__ = "$Revision$"
__author__ = "kenneth.altsjo@jeppesen.com"
__all__ = ['main']

# UsageException ---------------------------------------------------------{{{2
class UsageException(RuntimeError):
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


# main ==================================================================={{{1
def main(*argv, **kwds):
    """
    cleanup.py

    This script should be called regularly to clean up temp files and other
    obsolete files from the file system. It uses system time rather than
    simulated time even if a time server is configured and running. Reason
    is that file creation time stamps are always in system time.

    If called without parameters (see 'usage:' below) cleanup should be
    configured in the site configuration file. The following configuration
    structure is expected (example):

    :
    <cleanup>
        <files>
            <path>$(CARMDATA)/REPORTS/EXPORT</path>
            <filter>Manifest*</filter>
            <days>14</days>
        </files>
        <files>
            :
        </files>
    </cleanup>

    Note that <path> and <days> are mandatory within each <files> section.
    Several <cleanup> sections may exist under different parent nodes in
    the configuration.

usage:
    cleanup.py [--test]

    or

    cleanup.py -p path -d days [-h hours] [-f filter] [--test]

    or

    cleanup.py --path=path --days=days [--hours=hours --filter=filter]

    or

    cleanup.py --help


arguments:
    -p path         Remove files in this directory.
    --path=path

    -d days         Remove files older than 'days'.
    --days=days

    [-h hours]      Optional number of hours (added to 'days').
    [--hours=hours]

    [-f fltr]       Optional glob style file filter. Only remove files 
    [--filter=fltr] matching this filter. E.g. 'tmp.*'.

    [--test]        Print filenames instead of removing

    [--help]        This help text.
    """

    if len(argv) == 0:
        argv = sys.argv[1:]
    try:
        try:
            optlist, params = getopt.getopt(argv, 'p:d:h:f:',
                    [
                        "help",
                        "test",
                        "path=",
                        "days=",
                        "hours=",
                        "filter=",
                    ]
            )
        except getopt.GetoptError, msg:
            raise UsageException(msg)
        path = None
        days = None
        hours = 0
        filter = "*"
        testMode = False
        for (opt, value) in optlist:
            if opt == '--help':
                print main.__doc__
                return 0
            elif opt == '--test':
                testMode = True
            elif opt in ('-p', '--path'):
                path = value
            elif opt in ('-d', '--days'):
                days = int(value)
            elif opt in ('-h', '--hours'):
                hours = int(value)
            elif opt in ('-f', '--filter'):
                filter = value
            else:
                pass
    except UsageException, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    except Exception, err:
        print >>sys.stderr, err
        return 22

    if path:
        if days is None:
            raise UsageException("ERROR: Days must be specified!")
        deleteFiles(path, filter, days, hours, testMode)
    else:
        config = ServiceConfig()
        for elem in config.getProperties('cleanup/files/*'):
            tag = elem[0].decode()
            val = elem[1].decode()
            if tag.endswith('/path'):
                deleteFiles(path, filter, days, hours, testMode)
                path = val
                days = None
                filter = "*"
                hours = 0
            elif tag.endswith('/filter'):
                filter = val
            elif tag.endswith('/days'):
                days = int(val)
            elif tag.endswith('/hours'):
                hours = int(val)
        deleteFiles(path, filter, days, hours, testMode)

    print "[%s] Cleanup done" % (datetime.datetime.now())


def deleteFiles(path, filter, days, hours, testMode):
    if path is None or days is None:
        return
    files = glob.glob(os.path.join(path, filter))
    now = datetime.datetime.now()
    olderthan = now - datetime.timedelta(days=days, hours=hours)
    nFiles = 0
    for file in files:
        if os.path.isfile(file):
            mtime = os.path.getmtime(file)
            if olderthan > datetime.datetime.fromtimestamp(mtime):
                if testMode:
                    print file
                else:
                    os.remove(file)
                nFiles += 1
    if testMode:
        print "Cleanup found %d files in %s" % (nFiles, path)
    else:
        print "%s Cleanup removed %d files in %s" % (now, nFiles, path)

if __name__ == "__main__":
    sys.exit(main())

