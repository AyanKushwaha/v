#!/usr/bin/env python

from optparse import OptionParser
import sys, os, time

UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-f', '--file', dest='file',
                      help="""The path to the file that will be created""")
    parser.add_option('-e', '--error_limit', dest='error_limit',
                      help="""Max time to write file until it is considered to be an error""")
    parser.add_option('-w', '--warning_limit', dest='warning_limit',
                      help="""Max time to write file until it is considered to be a warning""")

    options, args = parser.parse_args()

    # Check for required options
    for option in ('file', 'error_limit', 'warning_limit'):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            sys.exit(CRITICAL)

    try:
        start_time = time.time()
        
        fd = open(options.file, 'w')
        fd.write("This is a test")
        fd.close()
        
        write_time = round(time.time() - start_time, 4)

        if write_time > float(options.error_limit):
            print "CRITICAL: Time above error limit %s s (limit: %s s)" % (write_time, options.error_limit)
            sys.exit(CRITICAL)
        elif write_time > float(options.warning_limit):
            print "WARNING: Time above warning limit %s s (limit: %s s)" % (write_time, options.warning_limit)
            sys.exit(WARNING)
        else:
            print "OK: Write time %s s" % (write_time)
            sys.exit(OK)
            
    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking XML-RPC server: %s' % e
        sys.exit(CRITICAL)
