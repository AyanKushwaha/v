#!/usr/bin/env python

from optparse import OptionParser
import xmlrpclib
import httplib
import sys

TIMEOUT = 5

EVAL_EXPRESSION = "2+2"
EXPECTED_EVAL_RESPONSE = "4"
# from xmlrpclib import ServerProxy
# s = ServerProxy("http://stoelmans:11002/RPC2")
# s.RaveServer.evalPythonString("2+2")

# Exit statuses recognized by Nagios
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2

class TimeoutHTTPConnection(httplib.HTTPConnection):
    def connect(self):
        httplib.HTTPConnection.connect(self)
        self.sock.settimeout(self.timeout)

class TimeoutHTTP(httplib.HTTP):
    _connection_class = TimeoutHTTPConnection
    def set_timeout(self, timeout):
        self._conn.timeout = timeout

class TimeoutTransport(xmlrpclib.Transport):
    def __init__(self, timeout=10, *l, **kw):
        xmlrpclib.Transport.__init__(self,*l,**kw)
        self.timeout=timeout
    def make_connection(self, host):
        conn = TimeoutHTTP(host)
        conn.set_timeout(self.timeout)
        return conn

class TimeoutServerProxy(xmlrpclib.ServerProxy):
    def __init__(self,uri,timeout=10,*l,**kw):
        kw['transport']=TimeoutTransport(timeout=timeout, use_datetime=kw.get('use_datetime',0))
        xmlrpclib.ServerProxy.__init__(self,uri,*l,**kw)

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-u', '--url', dest='url',
                      help="""URL to XML-RPC server""")
    parser.add_option('-e', '--expression', dest='expression', default=EVAL_EXPRESSION,
                      help="""Expression to evaluate (default: %s)""" % EVAL_EXPRESSION)
    parser.add_option('-r', '--response', dest='response', default=EXPECTED_EVAL_RESPONSE,
                      help="""Expected response (default: %s)""" % EXPECTED_EVAL_RESPONSE)
    parser.add_option('-S', '--substr', dest='substringMatch', action="store_true",
                      help="Match substring of response instead of whole")
    parser.add_option('-t', '--timeout', dest='timeout', type="int",
                      help="""Timeout (default: %i seconds)""" % (TIMEOUT), default=TIMEOUT)

    options, args = parser.parse_args()

    # Check for required options
    for option in ('url',):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            sys.exit(CRITICAL)

    try:
        s = TimeoutServerProxy(options.url, timeout=options.timeout)
        response = s.RaveServer.evalPythonString(options.expression)
        if response:
            response = str(response)
            if response == options.response or options.substringMatch and options.response in response:
                print 'OK - XML-RPC server at %s is up (\'%s\' => \'%s\')' % (
                    options.url,
                    options.expression,
                    options.response)
                sys.exit(OK)
            else:
                print 'CRITICAL - Unexpected response from host at %s (\'%s\' => \'%s\')' % (
                    options.url, options.expression,response)
                sys.exit(CRITICAL)
        else:
            print 'CRITICAL - XML-RPC server at %s is down' % options.url
        sys.exit(CRITICAL)
    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking XML-RPC server: %s' % e
        sys.exit(CRITICAL)
