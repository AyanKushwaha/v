#!/usr/bin/env python

from optparse import OptionParser
import socket,sys

TIMEOUT = 5

# Exit statuses recognized by Nagios
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2

def ping_sysmond(host, port, timeout):
    ping_msg = '\x02<ping />\x03'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    response = ""
    try:
        s.connect((host, port))
        s.sendall(ping_msg)
        s.shutdown(socket.SHUT_WR)
        while 1:
            data = s.recv(1024)
            if data == "":
                break
            else:
                response = data
    except Exception, e:
        print 'CRITICAL - Sysmond connection failed: %s' % e
        sys.exit(CRITICAL)
    s.close()
    return response

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-H', '--hostname', dest='hostname',
                      help="""Sysmond host""")
    parser.add_option('-p', '--sysmond-port', dest='port', type="int",
                      help="""Sysmond port""")
    parser.add_option('-t', '--timeout', dest='timeout', type="int",
                      help="""Timeout (default: %i seconds)""" % (TIMEOUT), default=TIMEOUT)

    options, args = parser.parse_args()

    # Check for required options
    for option in ('hostname', 'port'):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            sys.exit(CRITICAL)
    try:
        response = ping_sysmond(options.hostname, options.port, options.timeout)
        if response:
            if not "SYSMOND" in response:
                print 'CRITICAL - Unknown response from sysmond at %s (\'%s\')' % (
                    options.hostname, repr(response))
                sys.exit(CRITICAL)
            else:
                print 'OK - Sysmond at %s is up (\'%s\')' % (
                    options.hostname, str(response)[1:-2])
                sys.exit(OK)
        else:
            print 'CRITICAL - Sysmond at %s is down' % options.hostname
        sys.exit(CRITICAL)
    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking sysmond: %s' % e
        sys.exit(CRITICAL)
