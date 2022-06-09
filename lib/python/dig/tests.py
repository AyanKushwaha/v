"""
Code for testing DIG 
"""

from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult, TextContentType, UnicodeContentType, BinaryContentType
from carmensystems.dig.framework import errors, utils, carmentime
from carmensystems.dig.messagehandlers import reports
from carmensystems.dig.messagehandlers import dave as msgh_dave
from carmensystems.dig.support.queryparser import QueryParser
from carmensystems.dig.support.transports.ftp import Transport
from carmensystems.dig.framework.dave import WriteDaveOperation, DaveSearch, DaveValidator
from carmensystems.dig.jmq import metaRequestMessage

class MockReport(MessageHandlerBase):
    """
    This is a handler to create mock reports for testing DIG setup and handlers
    without all the headache of starting a report worker...
    """
    def __init__(self, name=None, contentType="text/plain", content=None, contentLocation=None, destination="", subtype="", rcpttype=""):
        super(MockReport, self).__init__(name)
        if contentLocation is None and content is None:
            content = "-- NO DATA CONFIGURED FOR MOCK REPORT --"
        self.contentType = (contentType or "text/plain")
        self.contentLocation = contentLocation        
        self.content = content
        self.destinations = (destination or "").split(",")
        self.subtypes = (subtype or "").split(",")
        self.rcpttypes = (rcpttype or "").split(",")

    def handle(self, message):
        self._services.logger.logDebug("Creating mock report %s" % self.destination)

        outData = {}
        dests = outData['destination'] = []
        for dest in self.destinations:
            for st in self.subtypes:
                for rt in self.rcpttypes:
                    d = {}
                    if st:
                        d['subtype'] = st
                    if rt:
                        d['rcpttype'] = rt
                    dests.append([dest, d])
        outData['content-type'] = self.contentType
        if self.content is None:
            outData['content-location'] = self.contentLocation
        else:
            outData['content'] = self.content
        
        self.setContent([outData])

        self._services.logger.logDebug(message.content)
        return CallNextHandlerResult()