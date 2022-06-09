
# [acosta:06/347@11:48] Some tools for Websphere MQ

"""
This module contains some a class, MQ, that can be used to read and write
messages to/from a MQ queue.
"""

# imports ================================================================{{{1
import DigMQ
import warnings


# export statement ======================================================={{{1
__all__ = ['MQError', 'MQUserError', 'MQManager', 'MQueue']


# constants =============================================================={{{1
O_RDONLY = DigMQ.O_RDONLY
O_WRONLY = DigMQ.O_WRONLY
O_RDWR = DigMQ.O_RDWR


# exception classes ======================================================{{{1

# MQError ----------------------------------------------------------------{{{2
class MQError(RuntimeError):
    """
    Custom exception class for MQ related errors.
    """
    msg = ''
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


# MQUserError ------------------------------------------------------------{{{2
def MQUserError(MQError):
    """
    Custom exception class for MQ errors due to faulty usage.
    """
    operation = ''
    instance = None
    def __init__(self, operation, instance):
        self.operation = operation
        self.instance = instance
    def __str__(self):
        return "Trying operation '%s' on a %s that is not ready (connected or opened)." % (operation, instance.__class__.__name__)


# classes ================================================================{{{1

# MQManager --------------------------------------------------------------{{{2
class MQManager:
    """
    Handles connections, backout and commit operations.
    """
    def __init__(self, host='localhost', port=1414, manager=None, channel=None):
        if manager is None:
            raise MQError("No queue manager name given.")
        self.host = host
        self.port = port
        self.manager = manager
        self.channel = channel
        self.__connexion = None
        if channel is None:
            err, self.__connexion = DigMQ.qconnect(host, port, manager)
        else:
            err, self.__connexion = DigMQ.qconnect(host, port, manager, channel)
        checkMQError(err, "connect", self)

    def __str__(self):
        return '<%s host="%s" port="%d" manager="%s" channel="%s">' % (
            self.__class__.__name__,
            self.host,
            self.port,
            self.manager,
            self.channel
        )

    __repr__ = __str__

    def __int__(self):
        return self.__connexion

    def disconnect(self):
        if self.__connexion is None:
            raise MQUserError("disconnect")
        err = DigMQ.qdisconnect(self.__connexion)
        checkMQError(err, "disconnect", self)
        self.__connexion = None

    def backout(self):
        if self.__connexion is None:
            raise MQUserError("backout")
        err = DigMQ.qback(self.__connexion)
        checkMQError(err, "backout", self)

    def commit(self):
        if self.__connexion is None:
            raise MQUserError("commit")
        err = DigMQ.qcommit(self.__connexion)
        checkMQError(err, "commit", self)


# MQueue -----------------------------------------------------------------{{{2
class MQueue:
    def __init__(self, connexion, queue=None, mode=O_RDWR, altuser=None):
        if queue is None:
            raise MQError("No queue name given.")
        self.queue = queue
        self.mode = mode
        self.altuser = altuser
        self.__connexion = connexion
        if self.altuser is None:
            err, self.__queue = DigMQ.qopen(self.__connexion, queue, mode)
        else:
            err, self.__queue = DigMQ.qopen(self.__connexion, queue, mode, altuser)
        checkMQError(err, "qopen", self)

    def __str__(self):
        return '<%s connection=%s host="%s" queue="%s" mode="%d" altuser="%s">' % (
            self.__class__.__name__,
            str(self.__connexion),
            self.queue,
            self.mode,
            self.altuser
        )

    __repr__ = __str__

    def __int__(self):
        return self.__queue

    def put(self, data):
        if self.__connexion is None or self.__queue is None:
            raise MQUserError("commit")
        err = DigMQ.qput(self.__connexion, self.__queue, data, len(data))
        checkMQError(err, "put", self)

    def get(self, timeout=5000, codeset=-1):
        if self.__connexion is None or self.__queue is None:
            raise MQUserError("get")
        # Note the order for this particular function is different 'data, err'!
        data, err = DigMQ.qget_string(self.__connexion, self.__queue, timeout, codeset)
        checkMQError(err, "get(timeout=%d, codeset=%d)" % (timeout, codeset), self)
        return data

    def iterator(self):
        while 1:
            data = self.get()
            if data == '':
                return
            yield data

    def close(self):
        if self.__connexion is None or self.__queue is None:
            raise MQUserError("get")
        err = DigMQ.close(self.__connexion, self.__queue)
        checkMQError(err, "close", self)


# functions =============================================================={{{1

# checkMQError -----------------------------------------------------------{{{2
def checkMQError(err, operation, instance):
    """
    Warn if a MQ warning, if a MQ Error else raise MQError.
    """
    if err == 0:
        return ''
    else:
        if err == -1:
            raise MQError("Memory ERROR from %s" % (str(instance)))
        else:
            errMsg = "%s from %s" % (DigMQ.qerr_string(err, operation), str(instance))
            if err < 0:
                raise MQError(errMsg)
        warnings.warn(errMsg)

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
