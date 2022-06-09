import sys, time
from utils import ServiceConfig
from AbsTime import AbsTime

__C = None


def _C():
    global __C
    if __C == None:
        __C = ServiceConfig.ServiceConfig()
    return __C


def _RPC(uri):
    import httplib, xmlrpclib

    class htconn(httplib.HTTPConnection):
        def connect(self):
            httplib.HTTPConnection.connect(self)
            self.sock.settimeout(20)

    class http(httplib.HTTPConnection):
        _connection_class = htconn

    class tpt(xmlrpclib.Transport):
        def make_connection(self, host):
            return http(host)

    t = tpt()
    s = xmlrpclib.ServerProxy(uri, transport=t)
    return s


def _pytime2abstime(secs):
    return AbsTime((secs - 504921600.0) / 60)


def _uri():
    return _C().getServiceUrl("time")


def uri():
    """Displays the URI for the current time server"""
    print _uri()


def get():
    """Gets the current time according to the time server"""
    u = _uri()
    if not u:
        print >> sys.stderr, "Time server not configured"
        sys.exit(1)
    tv = _RPC(u).carmensystems.xmlrpc.timebaseserver.get()
    now = (time.mktime(time.gmtime()) - tv['utc_start']) * tv["factor"] + tv['logical']
    print str(_pytime2abstime(now))


def set(date, tim=""):
    """Sets current time of the time server"""
    u = _uri()
    if not u:
        print >> sys.stderr, "Time server not configured"
        sys.exit(1)
    if tim:
        date += " " + tim
    t = int(AbsTime(date)) * 60 + 504921600.0
    a = _RPC(u)
    tv = a.carmensystems.xmlrpc.timebaseserver.get()
    tv['logical'] = t + (tv['utc_start'] - time.mktime(time.gmtime())) * tv["factor"]
    a.carmensystems.xmlrpc.timebaseserver.set(tv)
