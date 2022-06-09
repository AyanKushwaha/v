#!/usr/bin/env python
from util.common import SQL
from optparse import OptionParser
import datetime
import sys, os

WARNING_LIMIT = 60
ERROR_LIMIT = 120

UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-u', '--dburl', dest='dburl',
                      help="""DB URL""")
    parser.add_option('-s', '--schema', dest='schema',
                      help="""DB schema""")
    parser.add_option('-w', '--warning_limit', dest='warning_limit', type="int",
                      help="""Warning Limit in seconds(default: %i seconds)""" % (WARNING_LIMIT), default=WARNING_LIMIT)
    parser.add_option('-e', '--error_limit', dest='error_limit', type="int",
                      help="""Error Limit in seconds(default: %i seconds)""" % (ERROR_LIMIT), default=ERROR_LIMIT)

    options, args = parser.parse_args()

    # Check for required options
    for option in ('dburl','schema'):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            sys.exit(CRITICAL)

    try:
        statement = "SELECT MAX(committs) FROM dave_revision"
        last_committs = SQL(statement,options.dburl,options.schema)[0][0]
        time_since_commit = datetime.datetime.now() - datetime.timedelta(0,last_committs) - datetime.datetime(1986, 1, 1, 0, 0, 0)

        printstring  = "Last commit %s seconds ago." %(time_since_commit.seconds)
        if time_since_commit.seconds < options.warning_limit:
            print "OK - %s"%(printstring)
            sys.exit(OK)
        elif time_since_commit.seconds < options.error_limit:
            print "Warning - %s"%(printstring)
            sys.exit(WARNING)            
        else:
            print "CRITICAL - %s"%(printstring)
            sys.exit(CRITICAL)
        
    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking last commit: %s' % e
        sys.exit(CRITICAL)
