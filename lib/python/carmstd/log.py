"""
log.py

Functions for unified look and feel of logging messages generated from
Python code in the CARMUSR.

Example of usage:

from carmstd import log
log.error('Something went wrong')

"""
import inspect
import time

try:
    import Errlog
    _studio_log = True
except ImportError:
    _studio_log = False

_current_log_level = 'trace'

log_levels = {'fatal': 0,
              'error': 1,
              'info': 2,
              'debug': 3,
              'trace': 4}


def fatal(msg, stack_level=0):
    """
    Log msg with severity FATAL.

    @param msg: The message
    @type msg: string
    @param stack_level: The number of levels in the stack top move before checking context.
    @type stack_level: int
    @rtype: None
    """
    _log('fatal', msg, stack_level)


def error(msg, stack_level=0):
    """
    Log msg with severity ERROR.

    @param msg: The message
    @type msg: string
    @param stack_level: The number of levels in the stack top move before checking context.
    @type stack_level: int
    @rtype: None
    """
    _log('error', msg, stack_level)


def warning(msg, stack_level=0):
    """
    Log msg with severity WARNING.

    @param msg: The message
    @type msg: string
    @param stack_level: The number of levels in the stack top move before checking context.
    @type stack_level: int
    @rtype: None
    """
    _log('warning', msg, stack_level)


def info(msg, stack_level=0):
    """
    Log msg with severity INFO.

    @param msg: The message
    @type msg: string
    @param stack_level: The number of levels in the stack top move before checking context.
    @type stack_level: int
    @rtype: None
    """
    _log('info', msg, stack_level)


def debug(msg, stack_level=0):
    """
    Log msg with severity DEBUG.

    @param msg: The message
    @type msg: string
    @rtype: None
    """
    _log('debug', msg, stack_level)


def trace(msg, stack_level=0):
    """
    Log msg with severity TRACE.

    @param msg: The message
    @type msg: string
    @rtype: None
    """
    _log('trace', msg, stack_level)


def set_log_level(log_level):
    """
    @param log_level: One of the strings: 'fatal', 'error', 'info', 'debug' or 'trace'.
    """
    global _current_log_level
    _current_log_level = log_level


def _log(log_level, msg, stack_level=0):

    if log_levels.get(log_level, 4) > log_levels.get(_current_log_level, 4):
        return

    msg = str(msg)

    frame = inspect.currentframe()
    for _ix in range(2 + stack_level):
        frame = frame.f_back
    method = frame.f_code.co_name
    module = frame.f_globals["__name__"]
    line = frame.f_lineno
    t = time.strftime("%Y%m%d %H:%M:%S", time.gmtime())
    text = "%s %s::%s [line:%s] %5s:\n%s" % (t, module, method, line, log_level, msg)

    if _studio_log:
        Errlog.log(text)
    else:
        print text
