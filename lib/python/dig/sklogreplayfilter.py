"""This is a filter for delaying messages on SKLog-format to be replayed at a simulated time.
   Messages to be replayed are created on a file by the MessageRecorder. This file can later be
   parsed and posted to MQ via SKLogParser. Note that instead of using this filter,
   the SKLogParser itself can replay messages with proper delays inbetween.
"""

import base64
import time, traceback, sys, xmlrpclib
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult, SleepResult
from carmensystems.dig.framework import errors

class SKLogReplayFilter(MessageHandlerBase):
    """ Delay posting of messages """
    def __init__(self, 
                delay_threshold=0.1,
                logical_time_factor=1,
                time_offset=None, 
                logical_time_start=None, 
                min_delay=0,
                timeserver_url=None,
                name=None):
        super(SKLogReplayFilter, self).__init__(name)
        self.active = True
        self._last_ts_secs = 0

        # dont sleep smaller portions than this
        self.threshold = float(delay_threshold)
        # realtime from now with factor
        self.runfactor = int(logical_time_factor)
        self.runstart = time.time() 
        if time_offset:
            self.utc_offset = int(time_offset)
        elif logical_time_start:
            start = logical_time_start
            start_secs = time.mktime(time.strptime(start, "%Y-%m-%dT%H:%M:%S"))
            self.utc_offset = int( self.runstart - start_secs)
        else:
            self.utc_offset = 0
        # get time from timeserver
        self.timeserver = timeserver_url

        # TOTO: minimum delay seems strange? Henrik O or Fredrik G, can you explain?
        self.minDelay = int(min_delay)
        self.server = None
        self.tb = None
        self.te = None

    def start(self, services):
        super(SKLogReplayFilter, self).start(services)
        self._services.logger.debug("delay: entered setup()")
        if self.timeserver:
            try:
                self.server = xmlrpclib.ServerProxy(self.timeserver)
                self.tb = self.server.carmensystems.xmlrpc.timebaseserver
                self.te = self.tb.get()
            except:
                traceback.print_exc()
                raise errors.MessageError("delay: failed to connect to TimeServer [%s]" %
                    self.timeserver)
            #self.timeserver = None

    def handle(self, message):
        """ Delay the call of forwardMsg a number of seconds. Data is not modified """
        # This shall not happen, if it does happen how will it be parsed?
        if not self.active:
            self._services.logger.debug("delay: msg received, but not active")
            return CallNextHandlerResult()

        # Parse data, figure out timestamp
        data_split = message.content.split('\n')
        log_header = data_split[0].split(';')

        identifier = log_header[0]

        # magic identifier not found?
        if not identifier == 'SKLogEntry':
            # Don't delay messages we don't understand
            if self.minDelay:
                self._services.logger.info("delay: msg delayed %d seconds" % (self.minDelay))
                return SleepResult(self.onWakeup, None, self.minDelay, None, False)
            return CallNextHandlerResult()

        # Data is identified as a SKLogEntry

        # Calculate delay period and send off message
        ts_str = log_header[1]
        self._services.logger.debug("delay: ts_str='%s'" % ts_str)

        ts_secs  = time.mktime(time.strptime(ts_str[0:19], "%Y-%m-%dT%H:%M:%S"))
        if len(ts_str) > 19:
            # add microsecs
            ts_secs += float(ts_str[20:24]) * 0.0001

        if ts_secs <= self._last_ts_secs:
            ts_secs = self._last_ts_secs + 0.001

        self._last_ts_secs = ts_secs

        # Strip header row from data
        if len(data_split) > 0:
            content = '\n'.join(data_split[1:])
        else:
            content = ''
        message.setContent(content, message.contentType)

        if self.timeserver:
            now = self.te['logical'] + (time.time() - self.te['utc_start']) * self.te['factor']
            sleep_time = (ts_secs + self.utc_offset - now) / self.te['factor']
            self._services.logger.debug("delay: (ts_secs %f + offset %f - now %f ) / factor %f = sleep %f" % 
            (ts_secs, self.utc_offset, now, self.te['factor'], sleep_time))
        else:
            now = self.runstart + (time.time() - self.runstart) *  self.runfactor
            sleep_time = (ts_secs + self.utc_offset - now) / self.runfactor
            self._services.logger.debug("ts_str= '%s' delay: (ts_secs %f + offset %f - now %f) / factor %f = sleep %f" % 
            (ts_str, ts_secs, self.utc_offset, now, self.runfactor, sleep_time))

        msgId = self.getMsgId(message.metadata)
        if sleep_time > self.threshold:
            if self.timeserver:
                self.te = self.tb.get()
            self._services.logger.info("delay: msg %s delayed %f seconds" % (msgId, sleep_time))
            return SleepResult(self.onWakeup, None, sleep_time, None, False)
        else:
            self._services.logger.info("delay: msg %s forwarded without delay (sleep_time=%f sec)" % (msgId, sleep_time))
            return CallNextHandlerResult()

    def onWakeup(self, message):
        msgId = self.getMsgId(message.metadata)
        self._services.logger.info("delay: onWakeup message %s" % msgId)
        # Continue processing the message
        return CallNextHandlerResult()

    def getMsgId(self, metadata):
        msgId = ''
        key = 'carmensystems.dig.jmq.RequestMessage'
        if metadata.has_key(key):
            msgId = base64.b64encode(metadata[key].msgId)
        return msgId
