"""
DIG dispatcher handlers.
A dispatcher handler can be used to create an alternate message flow 
through a DIG channel. E.g. a message can be routed to different parsers
depending on content.
"""
__docformat__ = 'restructuredtext en'
__metaclass__ = type
import os
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult, ExitResult
from carmensystems.dig.framework import errors, utils
from carmensystems.dig.messagehandlers.ssim import SSIMHandler
from dig.opusxmlparser import OPUSParser
from carmensystems.dig.jmq import metaRequestMessage
from carmensystems.dig.messagehandlers.reports import CachingReportRequestHandler, ReportRequestHandler, ReportsContentType, BaseReportHandler
from carmensystems.dig.messagehandlers import digxml, dave as msgh_dave
from AbsDate import AbsDate

metaDispatchedHandler = "dig.dispatchers.DispatchedHandler"

class MessageDispatcher(MessageHandlerBase):
    """ Base class for dispatchers. Must be subclassed.
        Sets metadata key metaDispatchedHandler for subsequent handlers
        to know which handler was actually selected for the message.

        Parameters:
        
            bypassUnknown   -   Controls the behaviour with messages for
                                which no handler is found. If True, the
                                message is silently passed on to the next
                                handler in the channel. If False (default),
                                processing of the message is stopped and
                                an error message is issued.
                                
        Subclasses must implement the following methods:

        __init__(...)             -  The various alternative message
                                     handlers should be instantiated here.
                                     Parameters from the various handlers
                                     may be multiply inherited by passing
                                     them on to their constructors. 
        getHandlers()             -  Returns a list of alternative message 
                                     handlers.
        getHandlerForMsg(message) -  Returns the message handler to use for
                                     a certain message. Return None if no
                                     suitable handler is found.
    """
    def __init__(self, name=None, bypassUnknown="False"):
        super(MessageDispatcher, self).__init__(name)
        self.bypassUnknown = utils.convertToBoolean(bypassUnknown)

    def start(self, services):
        super(MessageDispatcher, self).start(services)
        for h in self.getHandlers():
            services.logger.info("Starting %s" % h.__class__)
            h.start(services)

    def handle(self, message):
        h = self.getHandlerForMsg(message)
        if not h is None:
            message.metadata.update({ metaDispatchedHandler : h.__class__.__name__ })
            return h.handle(message)
        if self.bypassUnknown:
            return CallNextHandlerResult()
        self._services.logger.error("Message could not be dispatched. No handler found.")
        return ExitResult()


class OpusSsimDispatcher(MessageDispatcher):
    """ This dispatcher routes messages of types MVT/ROT/ASM/SSM/SSIM to
        the correct parser. MVT and ROT messages are routed to the OPUS
        parser. Any other message is assumed to be parsed by the SSIM
        handler.
        When configuring this handler in the DIG channel, parameters
        normally used for configuring the SSIMHandler are also valid for
        this handler.
    """
    def __init__(self, name=None, divertSuffixStart='G', flightFilter=""):
        super(OpusSsimDispatcher, self).__init__(name)
        # Instantiate OPUSParser and SSIMHandler
        self.p_MVT_ROT = OPUSParser()
        self.p_ASM_SSM = SSIMHandler(divertSuffixStart=divertSuffixStart, flightFilter=flightFilter)

    def getHandlers(self):
        return [self.p_MVT_ROT, self.p_ASM_SSM]

    def getHandlerForMsg(self, message):
        # Simply route xml messages to the OPUSParser, we assume other
        # messages are ASM/SSM/SSIM.
        if message.content[:5] in ('<mvt ', '<rot ', '<?xml'):
            return self.p_MVT_ROT
        return self.p_ASM_SSM

class ArchiveMessageHandler(MessageHandlerBase):
    def __init__(self, name=None, archive_dir=None):
        super(ArchiveMessageHandler, self).__init__(name)
        self.archive_dir = archive_dir
        
    def handle(self, message):
        metaReports = BaseReportHandler.metakey('Reports')
        metaDelta = BaseReportHandler.metakey('Delta')
        assert hasattr(message, 'rptfile'), "Missing rptfile attribute"
        self._services.logger.debug("Returning archived report")
        message.metadata[metaReports] = [{'content':file(message.rptfile,'r').read(),
                                            'destination':[['default',{}]], 'content-type':'text/plain'}]
        message.metadata[metaDelta] = (0, 0, [])
        message.setContent(message.metadata[metaDelta], msgh_dave.DaveContentType())
        return CallNextHandlerResult()
        
class ReportCacheDispatcher(MessageDispatcher):
    """ This dispatcher routes certain types of requests to the 
        CachingReportRequestHandler and others to the normal non-caching
        ReportRequestHandler.
        The request types to cache are configured as a comma separated
        list in parameter cachingRequests. The rest of the parameters
        are a superset of the standard parameters of ReportRequesthandler
        and CachingReportRequestHandler.
    """
    def __init__(self, name=None, **kw):
        super(ReportCacheDispatcher, self).__init__(name)
        self.cachingRequests = kw.pop('cachingRequests', '').split(',')
        self.paramSeparator = kw.pop('paramSeparator', ',')
        self.archive_dir = kw.pop("archive_dir",None)
        self.defaultServer = kw.pop('defaultServer','')
        if not self.defaultServer:
            raise ValueError("defaultServer must be set")
        self.contentIsReports=kw.pop('contentIsReports','False')
 
        # Instantiate CachingReportRequestHandler and ReportRequestHandler
        self.cachingReportRequestHandler = CachingReportRequestHandler(defaultServer=self.defaultServer, contentIsReports=self.contentIsReports, name=name, **kw)
        self.timeout = kw.pop('timeout', None)
        self.reportRequestHandler = ReportRequestHandler(defaultServer=self.defaultServer, contentIsReports=self.contentIsReports, name=name, **kw)
        self.archiveMessageHandler = ArchiveMessageHandler(name=name, archive_dir=self.archive_dir)

    def getHandlers(self):
        return [self.cachingReportRequestHandler, self.reportRequestHandler, self.archiveMessageHandler]

    @staticmethod
    def format_activity(activity_id):
        """ The user can entry different things in the CrewPortal like
        In the crew portal"""

        activity_id = str(activity_id).replace(" ", "") # Remove all blanks

        if activity_id.isdigit():
            activity_id = "SK%04d" % (int(activity_id))    
        elif activity_id.startswith("SK") and activity_id[2:].isdigit():
            activity_id = "SK%04d" % (int(activity_id[2:]))
        else:
            # Keep the original string, this is either a activity or a malformed string
            pass
    
        return activity_id

    def get_date_from_string(self, date_string):
        """ Extracts year, month and date from a string """ 
        try:
            year, month, date = AbsDate(str(date_string)).split()
        except:
            self._services.logger.debug("Invalid date format %s" % (date_string))
            year = 0
            month = 1
            date = 1
            
        return year, month, date

    def getHandlerForMsg(self, message):
        
        rptfile = None
        rpt = None
        year = None
        month = None
        day = None
        crew = None
        flight = None
        activity_id = None
        

        if hasattr(message.content, "reportArg") and hasattr(message.content, "name"):
            args, kwargs = message.content.reportArg

            if message.content.name == "report_sources.report_server.rs_crewroster":
                crew = str(kwargs['empno'])
                year, month, _ = self.get_date_from_string(str(kwargs['startDate']))
                rpt = "crewroster" 
            elif message.content.name == "report_sources.report_server.rs_crewlist":
                if 'activityId' in kwargs.keys():
                    activity_id = self.format_activity(str(kwargs['activityId']))
                if 'date' in kwargs.keys():
                    year, month, day = self.get_date_from_string(str(kwargs['date']))
                rpt = "crewlist"
            elif message.content.name == "report_sources.report_server.rs_crewbasic":
                crew = str(kwargs['empno']).replace(" ", "") # Remove all blanks
                year, month, day = self.get_date_from_string(str(kwargs['searchDate']))
                rpt = "crewbasic" 
            elif message.content.name == "report_sources.report_server.rs_getreport" and len(args) > 3 and args[0] == "GetReport":
                rpt = args[1]
                if rpt in ("DUTYOVERTIME", "PILOTLOGCREW", "PILOTLOGSIM"):
                    crew, month, year = args[3:6]
                    crew = str(crew)
                    month = str(month)
                    year = str(year)
                # # ref SKCMS-760:
                # # We don't want reports from file used,
                # # as this alteres the date span and therefy the data requested by the user.
                # elif rpt in ("DUTYCALC",):
                #     crew, firstdate, _ = args[3:6]
                #     crew = str(crew)
                #     firstdate = str(firstdate)
                #     year, month, _ = self.get_date_from_string(firstdate)
                elif rpt in ("PILOTLOGFLIGHT",):
                    crew, flight, date = args[3:6]
                    crew = str(crew)
                    flight = self.format_activity(str(flight))
                    date = str(date)
                    year, month, day = self.get_date_from_string(date)
                    
            if isinstance(month, str):
                month_array = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
                if month.isdigit():
                    month = int(month)
                elif month.upper() in month_array:
                    month = 1 + month_array.index(month.upper())
                else:
                    # Invalid month format
                    month = 0 # This is handled by the code and will e.g. return FlightNotFound
                                                    
            if isinstance(day, str):
                if day.isdigit():
                    day = int(day)
                else:
                    # Invalid day format
                    day = 0 # This is handled by the code and will e.g. return FlightNotFound
            
            if rpt and flight and year and month and day:
                rptfile = os.path.join(self.archive_dir, str(year), "%02d" % month, "crewlists.%s.current" % rpt, "%02d" % day, "%s.xml" % flight)
            elif rpt and crew and year and month and day:
                rptfile = os.path.join(self.archive_dir, str(year), "%02d" % month, "crewlists.%s.current" % rpt, "%02d" % day, "%s.xml" % crew)
            elif rpt and crew and year and month:
                rptfile = os.path.join(self.archive_dir, str(year), "%02d" % month, "crewlists.%s.current" % rpt, "%s.xml" % crew)
            elif rpt and activity_id and year and month and day:
                rptfile = os.path.join(self.archive_dir, str(year), "%02d" % month, "crewlists.%s.current" % rpt, "%02d" % day, "%s.xml" % activity_id)

        if rptfile:
            self._services.logger.debug("Checking if archived response exists type %s, file '%s'" % (rpt, rptfile))
            if os.path.exists(rptfile):
                message.content.serverName = "rs_publish"
                message.rptfile = rptfile
                return self.archiveMessageHandler
            else:
                self._services.logger.debug("No archive found, forwarding to normal cached lookup")
        else:
            self._services.logger.debug("Normal cached lookup")
                        
        
        if not message.metadata.has_key(metaRequestMessage):
            # If original request missing in metadata, default to non-caching.
            return self.reportRequestHandler
        
        orgRequestMsg = message.metadata[metaRequestMessage]
        orgRequest = utils.toStringIfUnicode(orgRequestMsg.content)
        orgRequestArr = orgRequest.split(self.paramSeparator)
        if orgRequestArr[0] in self.cachingRequests:
            self._services.logger.debug("Using CachingReportRequestHandler for request: %s" % orgRequest)
            return self.cachingReportRequestHandler
        self._services.logger.debug("Using (non-caching) ReportRequestHandler for request: %s" % orgRequest)
        return self.reportRequestHandler


