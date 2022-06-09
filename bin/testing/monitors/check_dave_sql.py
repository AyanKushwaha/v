#!/usr/bin/env python

from optparse import OptionParser
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
        print "OK -",_SQL("SELECT 'SQL OK' FROM dual")[0][0]
        
        sys.exit(OK)
    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking XML-RPC server: %s' % e
        sys.exit(CRITICAL)
