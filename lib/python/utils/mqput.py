#!/bin/env python

# [acosta:06/345@11:08] Extended to accept input from stdin as well.

import sys, getopt
from carmensystems.dig.jmq import jmq

#from utils.mq import MQManager, MQueue

__all__ = ['main', 'put']

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
    mqput ($Revision$)

usage:
    mqput.py -h host -q queue [-p port] [-u altuser] [-v] file(s)

    or

    mqput.py --host=host --queue=queue [--replytoq=replytoq --replytoqmgr=replytoqmgr] [--port=port] [--altuser=altuser] \\
            [--verbose] file(s)

    or

    mqput.py --help


arguments:
    -h host         Connect to queue manager on this host.
    --host=host

    -m manager      Use this queue manager.
    --manager=manager

    -q queue        Use this queue.
    --queue=queue

    [--replytoq=replytoq]
                    Use this as reply to queue, message becomes a request.

    [--replytoqmgr=replytoqmgr]
                    Use this as reply to qmgr.

    [-c channel]    Use the named channel.
    [--channel=channel]

    [-p port]       Use port 'port' instead of default (%d).
    [--port=port]

    [-u altuser]    Use alternate user id 'altuser' for this connection.
    [--altuser=altuser]

    [--help]        This help text.

    [--verbose]     Show more messages

    file(s)         One or more filenames, if file is '-' then input is taken
                    from stdin.

    """

    if len(argv) == 0:
        argv = sys.argv[1:]
    try:
        try:
            optlist, params = getopt.getopt(argv, 'h:m:q:c:p:u:v',
                    [
                        "help",
                        "host=",
                        "manager=",
                        "queue=",
                        "channel="
                        "port=",
                        "altuser=",
                        "user=",
                        "verbose",
                        "replytoq=",
                        "replytoqmgr=",
                    ]
            )
        except getopt.GetoptError, msg:
            raise UsageException(msg)
        k = {}
        for (opt, value) in optlist:
            if opt == '--help':
                print main.__doc__
                return 0
            elif opt in ('-h', '--host'):
                k['host'] = value
            elif opt in ('-m', '--manager'):
                k['manager'] = value
            elif opt in ('-q', '--queue'):
                k['queue'] = value
            elif opt in ('--replytoq'):
                k['replytoq'] = value
            elif opt in ('--replytoqmgr'):
                k['replytoqmgr'] = value
            elif opt in ('-c', '--channel'):
                k['channel'] = value
            elif opt in ('-p', '--port'):
                k['port'] = int(value)
            elif opt in ('-u', '--altuser', '--user'):
                k['altuser'] = value
            elif opt in ('-v', '--verbose'):
                k['verbose'] = True
            else:
                pass
        kwds.update(k)
        _put(params, **kwds)
    except UsageException, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    except Exception, err:
        print >>sys.stderr, err
        return 22


def _put(filenames, host=None, port=None, queue=None, manager='', altuser='', channel='', replytoqmgr='', replytoq='', verbose=None):
    from carmensystems.common.Config import Config
    C = Config()
    if not host:
        _, host = C.getProperty('dig_settings/mq/server')
        if not host:
            host = 'localhost'
    if not port:
        _, port = C.getProperty('dig_settings/mq/port')
        if not port:
            port = 1415 
    if not manager:
        _, manager = C.getProperty('dig_settings/mq/manager')
        if not manager: manager = ''
    if not channel:
        _, channel = C.getProperty('dig_settings/mq/channel')
        if not channel: channel = ''
    if not altuser:
        _, altuser = C.getProperty('dig_settings/mq/altuser')
        if not altuser: altuser = ''
    mqm = jmq.Connection(host=host, port=int(port), manager=manager, channel=channel)
    print mqm
    mqq = mqm.openQueue(queueName=queue, altUser=altuser, mode='w') 
    print mqq
    if len(filenames) < 1:
        raise UsageException('ERROR: No file(s) specified')

    for fn in filenames:
        try:
            if fn == '-':
                data = ''.join(sys.stdin.readlines())
            else:
                f = open(fn)
                data = f.read()
                f.close()

            m = None
            if len(replytoq) > 0:
                m = jmq.Message(content=data,msgType = jmq.Message.requestMessageType, replyToQ=replytoq, replyToQMgr=replytoqmgr)
            else:
                m = jmq.Message(content=data)
            mqq.writeMessage(m)
            if verbose is not None:
                print "Message from file %s posted." % (fn)
            mqm.commit()
        except Exception, e:
            print >>sys.stderr, str(e)
            mqm.rollback()
            mqq.close()
            mqm.disconnect()
            sys.exit(2)

    mqq.close()
    mqm.disconnect()

if __name__ == "__main__":
    sys.exit(main())

