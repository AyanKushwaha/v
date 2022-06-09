#!/usr/bin/env python
import sys, os
from optparse import OptionParser

TIMEOUT = 15

import check_eval_python as P

# Exit statuses recognized by Nagios
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-u', '--url', dest='url',
                      help="""URL to XML-RPC server""")
    parser.add_option('-c', '--crew', dest='extperkey', metavar="EXTPERKEY",
                      help="Extperkey to use (default is to find a suitable one)")
    parser.add_option('-t', '--timeout', dest='timeout', type="int",
                      help="""Timeout (default: %i seconds)""" % (TIMEOUT), default=TIMEOUT)

    ok1 = "CHECK IN VERIFICATION"
    ok2 = "CHECK OUT VERIFICATION"
    resp = "CHECK IN/CHECK OUT MESSAGE"
    crew = '__import__("cio.run").run.any_crew()'

    options, args = parser.parse_args()
    
    # Check for required options
    for option in ('url',):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            sys.exit(CRITICAL)

    if options.extperkey:
        crew = "'%s'" % options.extperkey
    expr = '__import__("cio.run").run.run(%s)' % crew
    try:
        s = P.TimeoutServerProxy(options.url, timeout=options.timeout)
        response = s.RaveServer.evalPythonString(expr)
        if response:
            if ok1 in response or ok2 in response:
                print "OK - Crew checkin"
                sys.exit(OK)
            if response.startswith("['%s" % resp):
                print "WARNING - %s" % response
                sys.exit(WARNING)
            else:
                print 'CRITICAL - Unexpected response from checkin interface at %s (\'%s\')' % (
                    options.url, response)
                sys.exit(CRITICAL)
        else:
            print 'CRITICAL - XML-RPC server at %s is down' % options.url
        sys.exit(CRITICAL)
    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking XML-RPC server: %s' % e
        sys.exit(CRITICAL)

