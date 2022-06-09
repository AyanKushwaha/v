"""
Python log handler for Studio Errlog

Provides nicely-formatted-by-default log messages for Python code running inside Studio, and
falls back gracefully to stdout printing if Errlog is not available.
"""

import logging
import inspect

DEFAULT_LOG_FORMAT = '%(asctime)-15s %(levelname)-8s %(name)-5s %(message)s'
DEFAULT_LOG_LEVEL = logging.INFO

try:
    import Errlog
    errlog_log = Errlog.log
except ImportError:
    def errlog_log(msg):
        print msg


class StudioErrlogHandler(logging.Handler):
    def __init__(self, format_spec=None):
        logging.Handler.__init__(self)
        self.formatter = logging.Formatter(format_spec or DEFAULT_LOG_FORMAT)
        self.propagate = False
        
    def emit(self, record):
        errlog_log(self.format(record))
       

def get_logger(name=None, format_spec=None, level=None):
    """
    All parameters are optional. Don't specify them unless you have a good reason.
    
    :param str name: Name of the logger, by default the name of the calling module
    :param str format_spec: Format string for the message, per python logging module standard.
    :param str level: The level from which messages should be printed.
    :rtype logging.Logger
    """
    if name is None:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        name = mod.__name__
        
    lgr = logging.Logger(name=name)
    lgr.handlers = [StudioErrlogHandler(format_spec=format_spec), ]
    lgr.setLevel(level or DEFAULT_LOG_LEVEL)
    
    return lgr

if __name__ == "__main__":
    get_logger().fatal("This is fatal")
    get_logger().error("This is an error")
    get_logger(format_spec="%(levelname)-8s %(message)s").warn("This is a warning with overriden format spec.")
    get_logger(name="carmstd.mobok").info("This is info. Also, the logger name is overriden.")
    get_logger().debug("This is debug")

