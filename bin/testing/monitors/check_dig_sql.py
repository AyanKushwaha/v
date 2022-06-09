#!/usr/bin/env python

from optparse import OptionParser
from time import strftime, time, localtime
import xmlrpclib
import httplib
import sys, os

TIMEOUT = 20

UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2


_conn = None
def _SQL(sql):
    from carmensystems.dig.framework.dave import DaveConnector
    global _conn
    if _conn is None:
        _conn = DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])
    l1conn = _conn.getL1Connection()
    l1conn.rquery(sql, None)
    r = []
    try:
        while True:
            l = l1conn.readRow()
            if not l: return r
            r.append(l.valuesAsList())
    finally:
        l1conn.endQuery()
        _conn.close()
        _conn = None

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-u', '--dburl', dest='dburl',
                      help="""DB URL""")
    parser.add_option('-s', '--schema', dest='schema',
                      help="""DB schema""")
    parser.add_option('-t', '--timeout', dest='timeout', type="int",
                      help="""Timeout (default: %i seconds)""" % (TIMEOUT), default=TIMEOUT)

    options, args = parser.parse_args()

    # Check for required options
    for option in ('dburl','schema'):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            sys.exit(CRITICAL)

    try:
        os.environ["DB_URL"] = options.dburl
        os.environ["DB_SCHEMA"] = options.schema
        
        from_time = strftime('%Y-%02m-%02dT%02H:%02M:%02S', localtime(time()-24*3600))
        to_time = strftime('%Y-%02m-%02dT%02H:%02M:%02S', localtime(time()))
        print from_time, to_time
        
        #Number of failed
        statement = "SELECT COUNT(id) FROM job WHERE ended_at != 'not_ended' AND ended_at BETWEEN '%s' AND '%s' AND status not in ('ok', 'skipped (TaskReader started)') AND next_revid = 0 AND deleted = 'N'" % (from_time, to_time)
        nof_failed = int(_SQL(statement)[0][0])
        print statement   
        #Number not executed
        to_time = strftime('%Y-%02m-%02dT%02H:%02M:%02S', localtime(time()-3600))
        statement = "SELECT COUNT(id) FROM job WHERE start_at BETWEEN '%s' AND '%s' AND started_at = 'not_started' AND next_revid = 0 AND deleted = 'N'" % (from_time, to_time)
        print statement
        nof_not_started = int(_SQL(statement)[0][0])
                
        if nof_failed == 0 and nof_not_started == 0:
            print "OK - No failed or not started digjobs"
            sys.exit(OK)
        else:
            print "CRITICAL - %u failed and %u not started jobs" % (nof_failed, nof_not_started)            
            sys.exit(CRITICAL)
        
        
    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking XML-RPC server: %s' % e
        sys.exit(CRITICAL)
