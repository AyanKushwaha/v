#

#
"""
Custom loggers for SAS CMS.
"""

import Errlog
import logging
from logging.handlers import RotatingFileHandler
import os

# Log Constants
LOG_NAME = 'DataErrorLog'
LOG_FILE = '${CARMTMP}/logfiles/sas_logs/data_errors.log'
LOG_LEVEL = logging.WARNING
try:
    user_host = '(%s@%s)' % (os.environ['USER'], os.environ['HOSTNAME'])
except Exception, e:
    print "E",e
    user_host = ''
FORMAT = ':'.join(('%(asctime)s', '%(levelname)s', user_host, '%(message)s'))
MAX_BYTES = 10*1024**2 # 10MB
BACKUP_COUNT = 5


def getLogFile():
    """
    Creates given path of file if not already exists.
    """
    fileName = os.path.abspath(os.path.expandvars(LOG_FILE))
    if not os.path.exists(os.path.dirname(fileName)):
        os.makedirs(os.path.dirname(fileName))
    return fileName


class CustomRotatingFileHandler(RotatingFileHandler):
    """
    Custom RotatingFileHandler which writes problems with logging to
    the cms Errlog.
    """
    def handleError(self, record):
        Errlog.log('%s has failed to log record.'
                   ' Logfile is probably missing or damaged.' % LOG_NAME)


def getLogger():
    """
    Gets the logger instance.
    """
    # Get the logger
    logger = logging.getLogger(LOG_NAME)
    logger.setLevel(LOG_LEVEL)
    # Create handler if not already exist
    if len(logger.handlers) == 0:
        handler = CustomRotatingFileHandler(getLogFile(), maxBytes=MAX_BYTES,
                backupCount=BACKUP_COUNT)
        handler.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(handler)
    return logger


log = getLogger()
