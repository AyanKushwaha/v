

"""
Makes it easy to get time from a time server.
"""

import os
import sys
import time
import datetime
import xmlrpclib

from utils.ServiceConfig import ServiceConfig


class TimeServerUtils(object):
    """This class is a utility to easily get the time from a timeserver.
    
    It gets the needed time service from the configurations files.
    It is of course dependant on that there is a running time server.
    """
    
    # Singleton, by letting instances share the same state.
    __shared_state = {}

    def __init__(self, useSystemTimeIfNoConnection=True, debug=True):
        """init time server connection
        
        inargs:
         useSystemTimeIfNoConnection: Sets default behaviour when no connection.
        """
        # Makes it a singleton.
        self.__dict__ = self.__shared_state
        self.debug = debug
        if hasattr(self, 'useSystemTimeIfNoConnection'):
            if not self.useSystemTimeIfNoConnection == useSystemTimeIfNoConnection:
                raise TimeServerUtilsError, \
                      'Already initialized with useSystemTimeIfNoConnection=%s, change to %s not allowed.' %\
                      (self.useSystemTimeIfNoConnection, useSystemTimeIfNoConnection)
        else:
            self.useSystemTimeIfNoConnection = useSystemTimeIfNoConnection
        if hasattr(self, 'timeserver'):
            # Already initialized
            return

        self._TimeServerUrl = '<UNCONFIGURED>'
        try:
            config = ServiceConfig()
            self._TimeServerUrl = config.getServiceUrl('time')
            if not self._TimeServerUrl:
                raise TimeServerUtilsError, "Cannot find url for timeserver in configuration."
            tsProxy = xmlrpclib.ServerProxy(self._TimeServerUrl)
            self.timeserver = tsProxy.carmensystems.xmlrpc.timebaseserver
            # Test calling...
            timedummy = self.timeserver.get()
        except Exception, e:
            errMsg = "Failed to connect to xmlrpc timebaseserver %s. Error: %s" % (self._TimeServerUrl, e)
            if not self.useSystemTimeIfNoConnection:
                raise TimeServerUtilsError, errMsg
            print errMsg
            self.timeserver = None
            print "Using system time from now on ..."

    def getTime(self):
        """Returns the current time in python datetime format.
        
        Note that the default behaviour when unable use timeserver,
        depends on how the class is initiated.

        Conversion to AbsTime:
          utc_tup = TSU_INSTANCE.getTime().timetuple()
          utc_abs = AbsTime(*utc_tup[0:5])

        """
        try:
            timeDict = self.timeserver.get()
            now = timeDict['logical'] + (time.time() - timeDict['utc_start']) * timeDict['factor']
            now_datetime = datetime.datetime(*time.localtime(now)[:6])
            if self.debug:
                print "Using time server time: %s" % now_datetime

        except Exception, e:
            if self.useSystemTimeIfNoConnection and self.timeserver is None:
                now_datetime = datetime.datetime.now()
                if self.debug:
                    print "Using system time: %s" % now_datetime
            else:
                errMsg = "Failed to get current time from timebaseserver %s. Error: %s" % (self._TimeServerUrl, e)
                print errMsg
                raise TimeServerUtilsError, errMsg
        return now_datetime

    def getTimeLocal(self):
        """SASCMS-4189: getTime() returns the local time but since the servers
        are configured to use UTC then local time is also UTC. This
        function temporarily changes the time zone to be Copenhagen,
        fetches the local time in Copenhagen and then resets it to UTC.
        Affecting only current process. For more information see comment in getTime() above.
        """
        try:
            timeDict = self.timeserver.get()
            now = timeDict['logical'] + (time.time() - timeDict['utc_start']) * timeDict['factor']
            now_datetime = datetime.datetime(*time.localtime(now)[:6])
            if self.debug:
                print "Using time server time: %s" % now_datetime

        except Exception, e:
            if self.useSystemTimeIfNoConnection and self.timeserver is None:
                default_zone = os.environ['TZ']
                os.environ['TZ'] = 'Europe/Copenhagen'
                time.tzset()
                now_datetime = datetime.datetime.now() # Getting the local time in Copenhagen.
                os.environ['TZ'] = default_zone # Re-setting to default value. Just-in-case.
                time.tzset()
                if self.debug:
                    print "Using system time: %s" % now_datetime
            else:
                errMsg = "Failed to get current time from timebaseserver %s. Error: %s" % (self._TimeServerUrl, e)
                print errMsg
                raise TimeServerUtilsError, errMsg
        return now_datetime


#################  Exception classes #################

class TimeServerUtilsError(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.wrapped_exc = sys.exc_info()

    def __str__(self):
        return repr(self.args)


# Remove debug messages
debug = False


# functions
# UTC time.
def now_AbsTime():
    """Convenience function. Return current time as AbsTime."""
    from AbsTime import AbsTime
    return AbsTime(*now_datetime().timetuple()[:5])

def now_datetime():
    """Convenience function. Return current time as datatime."""
    return TimeServerUtils(debug=debug).getTime()

# Local time, Copenhagen.
def nowLocal_AbsTime():
    """Convenience function. Return current time as AbsTime."""
    from AbsTime import AbsTime
    return AbsTime(*nowLocal_datetime().timetuple()[:5])

def nowLocal_datetime():
    """Convenience function. Return current time as datatime."""
    return TimeServerUtils(debug=debug).getTimeLocal()


# The default now and nowLocal functions will return times as AbsTime
# since that is the more common time format in the CARMUSR code.
now = now_AbsTime
nowLocal = nowLocal_AbsTime

# eof
