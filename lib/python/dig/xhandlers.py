"""
Various utility dig handlers
"""
__docformat__ = 'restructuredtext en'
__metaclass__ = type

# imports ================================================================{{{1
import os
import datetime
import time
from copy import deepcopy
from AbsTime import AbsTime
from RelTime import RelTime
from Airport import Airport
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult, TextContentType, UnicodeContentType, BinaryContentType
from carmensystems.dig.framework import errors, utils, carmentime
from carmensystems.dig.messagehandlers import reports
from carmensystems.dig.messagehandlers import dave as msgh_dave
from carmensystems.dig.support.queryparser import QueryParser
from carmensystems.dig.support.transports.ftp import Transport
from carmensystems.dig.framework.dave import WriteDaveOperation, DaveSearch, DaveValidator
from carmensystems.dig.jmq import metaRequestMessage
from carmensystems.dave import dmf
from carmensystems.dave import baselib
import cio.acci as acci
import crewlists.status as status
from dig.RSSelector import RSSelector
from dig.constants import error_content_type
from utils.divtools import fd_parser
from crewlists.replybody import Reply, ReplyError, getReportReply
from suds.client import Client
from suds.transport import TransportError
import urllib2
from urllib2 import URLError
import json

# Message Handlers ======================================================={{{1

# FallBackHandler --------------------------------------------------------{{{2
class FallBackHandler(MessageHandlerBase):
    """
    A report that is returned from the Report Server will have two components:
    (1) a DAVE delta with operations that need to be committed to the database,
    (2) a report structure with reports that will be handled by another
        MessageHandler.

    This class will make it possible to modify the report and/or the database
    delta in case an error occurred.

    If one of the reports contain a field 'error', then we assume that the
    report failed.

    The proposed "error report" structure is:
    {
        'content': {
            'name'     : '<string representation of the exception type>',
            'args'     : ( <positional args>, ... )
            'kwargs'   : { <keyword args>, ... }
            'traceback': '<optional string representation of a traceback, from e.g. traceback.format_exc(...)>',
            'string'   : '<string representation of the exception>',
        }
        'content-type' : 'application/vnd.carmen.cms.reportserver.error',
    }

    If a report structure contains the 'error' key, then we assume that the
    report encountered an error.

    This class must be subclassed.
    """
    def __init__(self, name=None):
        super(FallBackHandler, self).__init__(name)

    def handle(self, message):
        """This handler should come right after some kind of 'ReportRequestHandler'."""
        if not reports.metaDelta in message.metadata:
            raise errors.MessageError('missing required metadata key %s' % metaDelta)
        if not reports.metaReports in message.metadata:
            raise errors.MessageError('missing required metadata key %s' % metaReports)

        err_delta = []
        err_reports = []

        # Locate errors
        for report in message.metadata[reports.metaReports]:
            if report['content-type'] == error_content_type:
                d, r = self.handle_error_report(report)
                err_delta.extend(d)
                err_reports.extend(r)

        if err_delta or err_reports:
            reqid, reqsrc, _ = message.metadata[reports.metaDelta]
            # metaDelta contains of a triple: (<requestId>, <requestSrc>, <[list_of_dave_operations]>)
            meta_delta = (reqid, reqsrc, err_delta)
            message.metadata[reports.metaDelta] = meta_delta
            message.metadata[reports.metaReports] = err_reports
            if isinstance(message.contentType, msgh_dave.DaveContentType):
                message.setContent(meta_delta, msgh_dave.DaveContentType())

        return CallNextHandlerResult()

    def handle_error_report(self, report, message):
        # Is this the correct Error type??
        raise errors.ChannelConfigError('FallBackHandler must be subclassed.')


# APISFallBackHandler ----------------------------------------------------{{{2
class APISFallBackHandler(FallBackHandler):
    """
    If the APIS report - Crew Manifest, FCM or Master Crew List, MCL - failed,
    then the report will mark the fault by adding some data.

    In those cases we extract the flight leg information and mark the leg with
    an attribute, to make the leg illegal in the Alert Monitor.

    We have to remove any database delta, and replace this delta with an insertion
    in the table 'flight_leg_attr' instead. The report structure itself will be
    cleared.
    """
    def __init__(self, name=None):
        super(APISFallBackHandler, self).__init__(name)

    def handle_error_report(self, report):
        """Handle 'error' report and return (new_delta, new_report)."""
        try:
            err_content = report['error-content']
        except:
            raise errors.MessageError("no 'error-content' in 'error' report")
        if not 'kwargs' in err_content:
            raise errors.MessageError("'error-content' did not contain 'kwargs'")
        try:
            kwargs = err_content['kwargs']
            fd = fd_parser(kwargs['fd']).flight_descriptor
            udor = kwargs['udor']
            adep = kwargs['adep']
            err_string = err_content['string']
        except Exception, e:
            raise errors.MessageError("unable to extract necessary data from 'error-content', reason=%s" % e)

        self._services.logger.error("failed creating FCM (fd=%s, udor=%s, adep=%s), reason: '%s'" % (fd, udor, adep, err_string))

        new_delta = [WriteDaveOperation('flight_leg_attr', {
                'attr': 'FCMERROR',
                'leg_fd': fd,
                'leg_udor': int(AbsTime(udor)) / 1440,
                'leg_adep': adep,
                'value_str': err_string,
                'value_abs': carmentime.toCarmenTime(self._services.now()),
            })]

        return new_delta, []


# DebugLogger ============================================================{{{2
class DebugLogger(MessageHandlerBase):
    """
    Logs message content (debug level)
    """

    def __init__(self, name=None):
        super(DebugLogger, self).__init__(name)

    def handle(self, message):
        self._services.logger.debug(message.content)
        return CallNextHandlerResult()


# StaticFtpWriter ========================================================{{{2
class StaticFtpWriter(MessageHandlerBase):
    """
    Sends message content by ftp.

    Parameters:

        url
            FTP url as ftp://user:password@host:port/path
    """

    def __init__(self, url, name=None):
        super(StaticFtpWriter, self).__init__(name)
        self.__url = url

    def handle(self, message):
        self._services.logger.debug("Sending message content to %s" % (self.__url))
        ftp = Transport()
        try:
            ftp._send(None, message.content, None, None, self.__url)
        except errors.TransientError, e:
            # Raise a message error. This way it is possible to catch by
            # a Notifier.
            raise errors.MessageError(str(e))

        return CallNextHandlerResult()


# CustomDaveWriter ========================================================{{{2
class CustomDaveWriter(MessageHandlerBase):
    """
    Writes operation lists to a DAVE database. Allows splitting list of
    operations into two transactions. The second transaction is commited
    only if the first one succeds. If the second transaction fails a warning
    message is printed but the message is otherwise regarded as succeded.

    Unlike the standard DaveWriter this handler does not support caching,
    out-of-order checking or transient error handling.

    Parameters:

        relaxTables
            Comma separated list of tables. Operations belonging to any of 
            these tables will go into the second transaction (see above).
    """

    def __init__(self, relaxTables="", name=None):
        super(CustomDaveWriter, self).__init__(name)
        self.__relaxTables = [x.strip().lower() for x in relaxTables.split(",")]

    def start(self, services):
        super(CustomDaveWriter, self).start(services)
        connector = self._services.getDaveConnector()

        # We must have a database connection.
        if connector.getConnection() is None:
            raise errors.NoDatabaseConnectionError('No database found. Make sure the configuration is correct.')

        self.__storer = connector.getStorer()
        self.__validator = DaveValidator(connector)

    def handle(self, message):
        source, transId, ops = message.content
        if not ops:
            self._services.logger.debug("No DAVE operations in message")
            return CallNextHandlerResult()

        start = datetime.datetime.utcnow()
        self._services.logger.info('starting to validate %s ops' % len(ops))
        self.__validator.validate(ops)
        self._services.logger.info('validating %s ops took %s' % (len(ops), datetime.datetime.utcnow() - start))

        # Move relax operations to a separate list
        idx = 0
        ops_relax = []
        while idx < len(ops):
            if ops[idx].entity.lower() in self.__relaxTables:
                ops_relax.append(ops.pop(idx))
            else:
                idx += 1

        # Commit first transaction (enforced operations)
        self._services.logger.debug('Executing %s enforced DAVE operations: %s' % (len(ops), ops))
        try:
            self.__storer.store(ops)
        except baselib.RuntimeError, e:
            raise errors.MessageError('%s: %s' % (e.__class__.__name__,e))

        # Commit second transaction (relaxed operations)
        try:
            self._services.logger.debug('Executing %s relaxed DAVE operations: %s' % (len(ops_relax), ops_relax))
            self.__storer.store(ops_relax)
        except Exception, e:
            self._services.logger.warning("Failed executing relaxed DAVE operations: %s" % (str(e)))

        return CallNextHandlerResult()


# ReportExtractor ========================================================{{{2
class ReportExtractor(MessageHandlerBase):
    """
    Converts incoming ReportsContentType message to TextContentType.
    Expects a message containing one non-binary report.
    """
    def __init__(self, name=None):
        super(ReportExtractor,self).__init__(name)

    def handle(self, message):
        self._services.logger.info("ReportExtractor started...")
        if not (isinstance(message.contentType, reports.ReportsContentType) and len(list(message.content)) == 1):
            raise errors.MessageError("Expects message to contain one report!")

        # Extract report from message content
        report = message.content[0]
        if report.has_key('content'):
            content = report['content']
        elif report.has_key('content-location'):
            try:
                fp = open(report['content-location'])
                content = fp.read()
                fp.close()
            except IOError, e:
                raise errors.MessageError('Unable to find report content file %s' % report['content-location'], e)
        else:
            raise errors.MessageError('Neither content or content-location found in report!')
        mimeType = 'text/plain'
        encoding = 'ISO-8859-1'
        if report.has_key('content-type'):
            ct = report['content-type'].split(';')
            mimeType = ct[0].strip()
            for entry in ct:
                if entry.strip().startswith('charset='):
                    encoding = entry.split('=')[1].strip()

        message.setContent(content, TextContentType(encoding=encoding))
        return CallNextHandlerResult()


# ReportRequestBuilder ==================================================={{{2
class ReportRequestBuilder(MessageHandlerBase):
    """
    Creates a report request xml intended for the ReportRequestHandler or
    CachingReportRequestHandler component.
    This component may be used in two ways:
        1. Configure 'script' and specify report parameters in 'args'
        2. Configure 'configFile' and let the component build report
           parameters from incoming message and the configFile in the
           same manner as the old ClassicReportHandler.
    It is also feasible (although unusual) to combine both methods.

    Parameters:

        script
            The name of the report script to run. If ommitted, script name
            from 'configFile' is used.

        server
            Symbolic name of report server. If ommitted, the handler looks
            for the presence of parameter 'serviceLookupClass'.

        serviceLookupClass
            Path to a class that returns a symbolic name of a report server
            based on the message content. If ommitted, the default server
            configured on the ReportHandler will be used.

            The class must implement the following method:
                string symbolicname lookup(list msgparts)
            where msgparts is an array of message content split up using
            the 'paramSeparator'.

        delta
            [True|False] Default "False". If True, the report server will
            generate a database delta after the report script has run.
            See also "overrideServerArgs" below.

        reload 
            [True|False] Default "False". If True, the report server will
            run a freshly reloaded database.
            See also "overrideServerArgs" below.

        configFile
            Path to configuration file used to interpret parameters in 
            incoming message. Note that the configuration file is the same
            as that used by the ClassicReportHandler. 
            If ommitted, incoming message is not used for
            producing request arguments (see parameter 'args').

        overrideServerArgs
            [True|False] Default "False". If True, any server arguments e.g.
            delta and reload in configFile override the values of "delta" 
            and "reload" (see above), instead of being used as report
            arguments. This option is only valid if configFile is specified.
            By using this option, it is possible to control server arguments
            per request type.

        paramSeparator
            Separator between parameters in incomming message. Used if
            parameter 'serviceLookupClass' and/or 'configFile' is used.
            Default ' '.

        reqidSeparator
            Separator character for the source request identifier, if any.
            Default None. If request id is used, reqidSeparator must be 
            explicitly defined.
            
        args
            Arguments for the report server script in python format. Supported
            data is either a list, a dictionary or a simple string value
            [[...]|{...}|string]. Default is None. 
    """

    def __init__(self, script=None, server=None, serviceLookupClass=None, configFile=None, overrideServerArgs="0", paramSeparator=' ', reqidSeparator=None, args=None, delta="0", reload="0", name=None):
        super(ReportRequestBuilder, self).__init__(name)
        if not script and not configFile:
            raise errors.ChannelConfigError("Either script or configFile must be specified.")
        self.__script = script
        self.__delta = utils.convertToBoolean(delta)
        self.__reload = utils.convertToBoolean(reload)
        self.__overrideServerArgs = utils.convertToBoolean(overrideServerArgs)
        self.__server = server
        self.__paramSeparator = paramSeparator
        self.__reqidSeparator = reqidSeparator
        self.__configFile = configFile

        self.__queryConfig = None
        if configFile:
            if not os.path.exists(configFile):
                raise errors.ChannelConfigError("Invalid configFile: %s" % configFile)
            qpParam = {}
            qpParam['config'] = configFile
            qpParam['param_separator'] = paramSeparator
            qp = QueryParser(qpParam)
            try:
                qp.readConfig()
                self.__queryConfig = qp.queries
            except Exception,e:
                raise errors.ChannelConfigError("Failed parsing configFile '%s': %s" % (configFile,e))
            
        if serviceLookupClass:
            try:
                self.__serverFinder = utils.getClass(serviceLookupClass)()
            except:
                raise errors.ChannelConfigError("Cannot instantiate class %s" % serviceLookupClass)
        else:
            self.__serverFinder = None

        if args:
            # Make sanity check on argument data
            if (args.startswith('{') and args.endswith('}')) or \
               (args.startswith('[') and args.endswith(']')):
                try:
                    self.__args = eval(args)
                except:
                    self.__args = args
            else:
                self.__args = args
        else:
            self.__args = None


    def handle(self, message):
        self._services.logger.debug("Handling %s message" % message.contentType)
        if isinstance(message.contentType, TextContentType) or \
           isinstance(message.contentType, BinaryContentType) or \
           isinstance(message.contentType, UnicodeContentType):
            msg = message.content.rstrip('\r\n')
            # Handle request Id, if available
            reqid = None
            trid = None
            if self.__reqidSeparator:
                parts = msg.split(self.__reqidSeparator)
                if len(parts) == 1:
                    # No request Id found
                    msg = parts[0]
                elif len(parts) == 2:
                    # Request id found
                    msg = parts[0]
                    reqid = parts[1]
                    trid = datetime.datetime.now()
                else:
                    raise errors.MessageError("Several occurances of reqidSeparator '%s' not allowed in request: %s" % (self.__reqidSeparator,msg))
            msgArr = msg.split(self.__paramSeparator)
        elif self.__serverFinder or self.__queryConfig:
            raise errors.MessageError("'configFile' and 'serviceLookupClass' can only be used with text messages.")

        rsLookupError = None
        # Lookup which ReportServer to use
        if self.__serverFinder:
            try:
                lookupServer = self.__serverFinder.lookup(msgArr, self._services.now())
            except ReplyError, e:
                lookupServer = 'rs_latest'
                rsLookupError = True
            except Exception, e:
                raise errors.MessageError("Server lookup failed for msg: %s: %s" % (utils.toStringIfUnicode(msg), str(e)))
            if lookupServer:
                self._services.logger.debug("Dynamically selected logical Report Server '%s'" % lookupServer)
                self.__server = lookupServer

        # Prepare report parameters
        scriptname = self.__script
        delta = self.__delta
        reload = self.__reload
        server = self.__server
        if self.__queryConfig:
            # Get parameters from incoming message
            if not self.__queryConfig.has_key(msgArr[0]):
                raise errors.MessageError("Request type '%s' is not defined in parameter config '%s'" % (msgArr[0], self.__configFile))
            rq = self.__queryConfig[msgArr[0]]
            # Use report script source from parameter config if missing
            if not scriptname:
                scriptname = rq.report
            self._services.logger.debug("Using Report script source: %s" % scriptname)
            try:
                raveDict,pList,pDict = rq._generateParameters(msgArr)
            except Exception, e:
                raise errors.MessageError("Invalid request: %s" % str(e))
            if raveDict:
                raise errors.MessageError("Usage of rave parameters in parameter config is not supported")
            # See if 'delta', 'reload' and 'server' should be fetched from config file
            if self.__overrideServerArgs:
                if pDict.has_key('delta'):
                    delta = utils.convertToBoolean(pDict['delta'])
                    self._services.logger.debug("Using delta=%s from configFile" % (pDict['delta']))
                    del pDict['delta']
                if pDict.has_key('reload'):
                    reload = utils.convertToBoolean(pDict['reload'])
                    self._services.logger.debug("Using reload=%s from configFile" % (pDict['reload']))
                    del pDict['reload']
                if pDict.has_key('server'):
                    server = pDict['server']
                    self._services.logger.debug("Using server=%s from configFile" % (pDict['server']))
                    del pDict['server']
            if rsLookupError:
                pDict['rsLookupError'] = rsLookupError
            # Merge args from message with args configured in channel
            if isinstance(self.__args, list):
                pList += self.__args
            elif isinstance(self.__args, dict):
                pDict.update(self.__args)
            reportArgs = [pList,pDict]
            if not pList and not pDict:
                self._services.logger.warning("No report parameters found while treating message '%s'" % msg)
        else:
            reportArgs = self.__args

        request = reports.ReportRequest(scriptname, reportArgs, server, reqid, trid, delta, reload)
        message.setContent(request, reports.ReportRequestContentType())
        return CallNextHandlerResult()



# ReportCachePostProc ===================================================={{{2
class ReportCachePostProc(MessageHandlerBase):
    """
    This handler manipulates output from CachingReportRequestHandler. It only
    applies to messages orignating from an MQReader.

    Options:
        paramSeparator
            Separator between parameters in original request message.
            Default ','.
    """

    def __init__(self, paramSeparator=',', name=None):
        super(ReportCachePostProc, self).__init__(name)
        self.__paramSeparator = paramSeparator

    def handle(self, message):
        if not isinstance(message.contentType, reports.ReportsContentType):
            self._services.logger.warning("Ignored message type '%s'" % (message.contentType))
            return CallNextHandlerResult()
        if not message.metadata.has_key(metaRequestMessage):
            self._services.logger.warning("Ignored non-MQ message")
            return CallNextHandlerResult()
        # Ignore if not cached report
        if not message.metadata.get(reports.metaIsCached, False):
            return CallNextHandlerResult()

        orgRequestMsg = message.metadata[metaRequestMessage]
        orgRequest = utils.toStringIfUnicode(orgRequestMsg.content)
        orgRequestArr = orgRequest.split(self.__paramSeparator)

        # Replace successful check-in reply messages
        if orgRequestArr[0] == 'CheckInOut':
            self._services.logger.debug("Found cached CheckInOut report")
            cacheReport = message.content[0]['content']
            extperkey = orgRequestArr[1].strip()
            logname =  self.getLogname(extperkey, self._services.now())
            report = CioReport(cacheReport, extperkey, logname, self._services.now())
            if report.isSuccessfulCheckin():
                self._services.logger.info("Replacing cached CheckInOut report")
                message.content[0]['content'] = report.getAlreadyCI()

        return CallNextHandlerResult()

    def getLogname(self, extperkey, now_time):
        now_date = carmentime.toCarmenTime(now_time) / 1440
        crewid = 0
        logname = ''
        emp_search = DaveSearch('crew_employment', [('extperkey','=',extperkey)])
        for rec in self._services.getDaveConnector().runSearch(emp_search):
            crewid = rec['crew']
        # Try first with logname from crew_extra_info
        for rec in self._services.getDaveConnector().runSearch(
                DaveSearch('crew_extra_info', [
                    ('id','=',crewid),
                    ('validfrom', '<=', now_date),
                    ('validto', '>', now_date),
                ])):
            return rec['logname']
        # If not found in crew_extra_info, use logname from crew.
        crew_search = DaveSearch('crew', [('id','=',crewid)])
        for rec in self._services.getDaveConnector().runSearch(crew_search):
            logname = rec['logname']
        return logname


# AddressInjector ========================================================{{{2
class AddressInjector(MessageHandlerBase):
    """
    This handler replaces destinations data in the reportDicts structure
    returned by report scripts. It is supposed to be placed between the
    ReportHandler and the TransportDispatcher in cases where the report
    script itself does not know the destination(s) of the reports it produces,
    nor which protocol(s) to be used to transport them.

    For each report returned by the report script it is possible to specify
    one or more destinations. Each destination consists of a protocol (mq, mqreply
    mail, ftp or file) and one or more protocol-specific addressing parameters.

    In order to associate a certain report with certain destination(s), a
    logical report name is used. Several reports returned by the report script
    may have the same logical report name. In the current version of dig, the 
    reportDicts data structure does not contain a report name. Instead the 
    protocol field of the destination specifier is used for carrying the report
    name. Only values other than the supported protocols (mq,mqreply,mail,ftp,file)
    are interpreted as logical report names and thus subject to address
    injection. Any valid addressing parameters specified by the report script
    supercede those specified in the AddressInjector, i.e. it is possible for
    the report script to specify e.g. mail subject for a logical report,
    and that will be used instead of the mail subject specified for the
    corresponding destination(s) in the AddressInjector.

    Any incoming destination specifiers having one of the supported protocols
    (mq,mqreply,mail,ftp,file) are left unchanged.

    Parameters:

        <reportname>_dests
            A comma separated list of logical destinations. <reportname> is
            replaced by the actual logical report name.

        <logicaldestination>_protocol
            Protocol for the <logicaldestination> which must be one of the
            logical destinations listed in one of the <reportname>_dests
            parameters. Supported protocols are [mq|mqreply|mail|ftp|file].

        <logicaldestination>_<protocol>_<param>
            Protocol-specific addressing parameters specified per destination.
            The following values of <param> can be specified:

            mq:     manager,queue
            mqreply:<none>
            mail:   data,body,to,subject,cc,mfrom,bcc,replyTo,attachmentName
            ftp:    url(*)
            file:   filename(*)

            (*) If several reports share the same logical report name
                they will overwrite eachother. To prevent this, you may
                include the special placeholder '###' in the url or
                filename. It will be replaced by a sequence number, 
                unique per logical report name, destination and message.
                Special placeholders '__ORGFILE__' and '__ORGPATH__'
                will be replaced by the file name/full path of the 
                original report file (i.e. content of the 'report-location'
                report keyword). If report-location is not used, an error
                will be generated if any of those two placeholders are used.
                Special placeholder __TIMESTAMP__ will be replaced by 
                current date/time on a format specified by parameter
                'timestampFormat' (default "%Y%m%d_%H%M%S").
                Special placeholder __MSGCOUNT__ will be replaced by
                a message serial number starting at 1 when channel starts.

    By specifying the special reportname 'ALL' the AddressInjector will
    replace all report destinations with those specified by 'ALL_dests'.
    This may be useful when testing.

    Parameters with unknown <reportname>, i.e. <reportname> is not found in
    the incoming reportDicts, are ignored.

    Example:
        In the example below, the report script returns two reports with
        the logical report names 'DKreport' and 'SEreport'.

        <messagehandler class="carmensystems.dig.messagehandlers.reports.ReportHandler"
            defaultServer="server1"
            server1="%(API/getserviceUrl/report)"
            contentIsReports="True"/>
        <messagehandler class="dig.xhandlers.AddressInjector"
            DKreport_dests="dkdest1,dkdest2"
            dkdest1_protocol="mail"
            dkdest1_mail_to="someone@somewhere.dk"
            dkdest1_mail_subject="Report in danish"
            dkdest1_mail_cc="someoneelse@somewhereelse.dk"
            dkdest2_protocol="ftp"
            dkdest2_ftp_url="ftp://user:passw@host:port/path"
            SEreport_dests="Archive"
            Archive_protocol="file"
            Archive_file_filename="/data/report.txt"/>
        <messagehandler class="carmensystems.dig.messagehandlers.transport.TransportDispatcher"
            mail_host="smtp.sas.dk"
            mail_port="25"/>
    """
    def __init__(self, name=None, timestampFormat="%Y%m%d_%H%M%S", **kw):
        super(AddressInjector, self).__init__(name)
        self.__timestampFormat = timestampFormat
        self.__params = kw
        self.__SUPPORTED_PROTOCOLS = ('mq','mqreply','mail','ftp','file')
        self.__SUPPORTED_PARAMS = {}
        self.__SUPPORTED_PARAMS['mq'] = ('manager','queue')
        self.__SUPPORTED_PARAMS['mqreply'] = ()
        self.__SUPPORTED_PARAMS['mail'] = ('data','to','subject','body','mfrom','cc','bcc','replyTo','attachmentName')
        self.__SUPPORTED_PARAMS['ftp'] = ('url',)
        self.__SUPPORTED_PARAMS['file'] = ('filename',)
        self.__msgCount = 0


    def handle(self, message):
        self.__msgCount += 1
        if not isinstance(message.content, list):
            raise errors.MessageError("Expects message to be a list of reportDicts!")

        # Treat special case: replace all destinations
        if self.__params.has_key("ALL_dests"):
            newDests = self.__getDestinations("ALL")
            for rd in message.content:
                if rd.has_key('destination'):
                    for dest in rd['destination']:
                        self._services.logger.debug("Replacing destination: %s" % serializeDest(dest))
                rd['destination'] = newDests
        else:
            reportNames = self.__getReportNames(message.content)
            self.__serial = {}
            newDests = {}
            for rn in reportNames:
                newDests[rn] = self.__getDestinations(rn)
            message.setContent(self.__injectDestinations(message.content, newDests), reports.ReportsContentType())

        self._services.logger.debug(serializeResult(message.content))
        return CallNextHandlerResult()


    def __getReportNames(self, reportDicts):
        """Extracts and creates a list of all report names from the indata
        structure. In the current version of dig, the reportDict data
        structure does not contain a report name. Instead the protocol field
        of the destination specifier is used for carrying the report name.
        """
        reportNames = []
        for rd in reportDicts:
            if not isinstance(rd, dict):
                raise errors.MessageError("Expects message to be a list of reportDicts!")
            if rd.has_key('destination'):
                for (protocol, params) in rd['destination']:
                    # reportname is stored in the 'protocol' field...
                    if protocol and protocol not in self.__SUPPORTED_PROTOCOLS:
                        if reportNames.count(protocol) == 0:
                            reportNames.append(protocol)
        return reportNames


    def __getDestinations(self, reportName):
        dests = []
        if self.__params.has_key(reportName + "_dests"):
            cLogicalDests = self.__params[reportName + "_dests"].split(',')
            for cd in cLogicalDests:
                cd = cd.strip()
                dest = self.__createDestFromParams(cd)
                self._services.logger.debug("Found destination %s: %s" % (cd,serializeDest(dest)))
                dests.append(dest)
        return dests


    def __injectDestinations(self, reportDicts, destmap):
        for i, rd in enumerate(reportDicts):
            orgpath = None
            if rd.has_key('content-location'):
                orgpath = rd['content-location']
            elif rd.has_key('filename'):
                orgpath = rd['filename']
            if rd.has_key('destination'):
                for (protocol, params) in rd['destination']:
                    if protocol not in self.__SUPPORTED_PROTOCOLS:
                        # Use any valid protocol parameter from reportDict
                        dests = deepcopy(destmap[protocol])
                        for (dProt,dParams) in dests:
                            pValid = self.__filterParams(params, dProt)
                            dParams.update(pValid)
                        # Note that xmlrpc "converts" tuple to list...
                        reportDicts[i]['destination'].remove([protocol, params])
                        reportDicts[i]['destination'] += self.__postProcess(dests, protocol, orgpath)
            else: 
                self._services.logger.warning("In-message reportDict has no 'destination' specifier!")
        return reportDicts


    def __filterParams(self, params, protocol):
        """ Keep parameters valid for the specified protocol """
        pValid = {}
        for (pKey,pVal) in params.items():
            if pKey in self.__SUPPORTED_PARAMS[protocol]:
                pValid[pKey] = pVal
        return pValid


    def __postProcess(self, dests, reportName, reportPath):
        """This function handles the following special features:
           
           Looks for '###' in the ftp url or file filename. If present,
           it is replaced by a serial number to avoid reports
           overwriting eachother in case of several reports sharing the
           same logical name.

           Looks for '__ORGFILE__' or '__ORGPATH__' in the ftp url or
           file filename. If present, it is replaced by the original
           file name (or whole path if __ORGPATH__) of the report. This
           presupposes that the content-location field in the report dict
           is used. If not, an error is generated.
        """
        doEnumerate = False
        for  protocol, params in dests:
            if protocol in ('file','ftp'):
                doEnumerate = True
        if not doEnumerate:
            return dests

        self.__serial.setdefault(reportName, {})
        timestamp = self._services.now().strftime(self.__timestampFormat)

        d = []
        for (protocol, params) in dests:
            p = params.copy()
            destKey = str((protocol, params))
            if protocol == 'file':
                self.__serial[reportName][destKey] = self.__serial[reportName].setdefault(destKey, 0) + 1
                if 'filename' in params:
                    if '__ORGFILE__' in p['filename'] or '__ORGPATH__' in p['filename']:
                        if not reportPath is None:
                            p['filename'] = p['filename'].replace('__ORGPATH__', reportPath)
                            p['filename'] = p['filename'].replace('__ORGFILE__', os.path.basename(reportPath))
                        else:
                            raise errors.MessageError("Placeholders __ORGFILE__ and __ORGPATH__ may only be used in combination with 'content-location' keyword")
                    p['filename'] = p['filename'].replace('###', "%03d" % self.__serial[reportName][destKey])
                    p['filename'] = p['filename'].replace('__TIMESTAMP__', timestamp)
                    p['filename'] = p['filename'].replace('__MSGCOUNT__', "%d" % self.__msgCount)
            if protocol == 'ftp':
                self.__serial[reportName][destKey] = self.__serial[reportName].setdefault(destKey, 0) + 1
                if 'url' in params:
                    if '__ORGFILE__' in p['url'] or '__ORGPATH__' in p['url']:
                        if not reportPath is None:
                            p['url'] = p['url'].replace('__ORGPATH__', reportPath)
                            p['url'] = p['url'].replace('__ORGFILE__', os.path.basename(reportPath))
                        else:
                            raise errors.MessageError("Placeholders __ORGFILE__ and __ORGPATH__ may only be used in combination with 'content-location' keyword")
                    p['url'] = p['url'].replace('###', "%03d" % self.__serial[reportName][destKey])
                    p['url'] = p['url'].replace('__TIMESTAMP__', timestamp)
                    p['url'] = p['url'].replace('__MSGCOUNT__', "%d" % self.__msgCount)
            d.append((protocol, p))
        return d


    def __createDestFromParams(self, ld):
        """Returns a tuple (protocol, params), where params is a dictionary
           of protocol specific parameters.
        """
        if self.__params.has_key(ld + "_protocol"):
            cProtocol = self.__params[ld + "_protocol"]
            if cProtocol not in self.__SUPPORTED_PROTOCOLS:
                raise errors.ChannelConfigError("Unknown protocol '%s' specified for destination '%s'" % (cProtocol,ld))
            # Make a hash of configured addressing parameters
            cParam = {}
            for key,value in self.__params.items():
                prefix = "%s_%s" % (ld,cProtocol)
                if key.startswith(prefix):
                    cParamName = key[len(prefix)+1:]
                    cParam[cParamName] = value
                    if cParamName not in self.__SUPPORTED_PARAMS[cProtocol]:
                        self._services.logger.warning("Ignored unknown parameter '%s' specified for protocol '%s'" % (cParamName,cProtocol))
            if not cParam.keys() and cProtocol != 'mqreply':
                raise errors.ChannelConfigError("No addressing parameters specified for destination '%s_%s'" % (ld,cProtocol))

            # Check protocol-specific addressing data
            if cProtocol == 'mq':
                if not (cParam.has_key('manager') and cParam.has_key('queue')):
                    raise errors.ChannelConfigError("Parameters 'manager' and 'queue' needs to be specified for protocol mq")
            elif cProtocol == 'ftp':
                if not cParam.has_key('url'):
                    raise errors.ChannelConfigError("Parameter 'url' needs to be specified for protocol ftp")
            elif cProtocol == 'file':
                if not cParam.has_key('filename'):
                    raise errors.ChannelConfigError("Parameter 'filename' needs to be specified for protocol file")
        else:
            raise errors.ChannelConfigError("Protocol is not specified for destination '%s'" % ld)

        return (cProtocol, cParam)

# UserConfigurableDispatcher ========================================================{{{2
class UserConfigurableDispatcher(MessageHandlerBase):
    """
    This handler chooses destination based on the contents of 
    a table called dig_recipients.

    """
    def __init__(self, name=None, **kw):
        super(UserConfigurableDispatcher, self).__init__(name)
        import dig.userconfig as D        
        self.lookup = D.lookup
        self.searchpatterns = D.searchpatterns
        self.__params = kw


    def handle(self, message):
        if not isinstance(message.content, list):
            raise errors.MessageError("Expects message to be a list of reportDicts!")

        # Treat special case: replace all destinations
        if self.__params.has_key("enabled") and self.__params["enabled"] == "false":
            self._services.logger.logDebug("UserConfigurableDispatcher is not enabled")
            return CallNextHandlerResult()
        log = lambda x: self._services.logger.debug(x)
        if self.__params.has_key("debugLog") and self.__params["debugLog"] == "true":
            log = lambda x: self._services.logger.info(x)
                
        for rd in message.content:
            if rd.has_key('destination'):
                dest = rd['destination']
                for i in range(len(dest)-1, -1, -1):
                    maintype, params = dest[i]
                    if maintype in ("mail","ftp","file","mq"):
                        self._services.logger.info("Fallback to hard-coded message type: %s" % maintype)
                        continue

                    #if protocol == "database-defined":
                    #if not "maintype" in params:
                    #    raise errors.MessageError("maintype must be set for database-defined destinations")
                    if not "subtype" in params:
                        self._services.logger.info("Problem with params: %s" % message.content)
                        raise errors.MessageError("subtype must be set for database-defined destinations")
                    del dest[i]
                    rcpttypes = []
                    if not "rcpttype" in params:
                        content = rd.get('content', '')
                        rcpttypes = self.searchpatterns(content, maintype, params["subtype"])
                        if len(rcpttypes) == 0: rcpttypes = ['']
                    else:
                        rcpttypes = [params['rcpttype']]
                    for rcpttype in rcpttypes:
                        lkup = self.lookup(maintype, params["subtype"], rcpttype)
                        if not lkup:
                            self._services.logger.warning("No matching recipents for %s, %s, %s" % (maintype, params["subtype"], params.get("rcpttype","")))
                        for d in lkup:
                            newParams = {}
                            newProto = d["protocol"].lower()
                            if newProto =="file":
                                fn = d["target"]
                                if "$" in fn:
                                    fn = os.path.expandvars(fn)
                                newParams["filename"] = fn
                            elif newProto =="ftp":
                                newParams["url"] = d["target"]
                            elif newProto == "mail":
                                newParams["to"] = d["target"]
                                if "subject" in params:
                                    newParams["subject"] = params["subject"]
                                if "from" in params:
                                    newParams["from"] = params["from"]
                                if d["subject"]:
                                    newParams["subject"] = d["subject"]
                            elif newProto == "mq":
                                try:
                                    q,m = d["target"].split("@")
                                    newParams["queue"] = q
                                    newParams["manager"] = m
                                except:
                                    raise errors.MessageError("'mq' target must be specfied as queue@manager")
                            else:
                                raise errors.MessageError("Invalid message target protocol '%s'")
                            dest.append((newProto, newParams))
                            self._services.logger.info("Final destination: %r" % dest)

        #log(serializeResult(message.content))
        return CallNextHandlerResult()


# MailBlocker ============================================================{{{2
class MailBlocker(MessageHandlerBase):
    """
    This handler will, if enabled, 
    (1) change all 'to' email addresses in the reports structure to the email
        address given as parameter 'recipients';
    (2) remove all 'cc' and 'bcc' addresses'.
    If the parameter 'recipients' is empty, all mail destinations will be
    removed.

    This MessageHandler allows test systems to block all outgoing email traffic
    from a channel, and instead send messages to a local email account.

    This MessageHandler should be placed in front of the TransportDispatcher.

    Example:
        <!-- ... in digchannels.xml ... -->
        [...]
        <messagehandler class="dig.xhandlers.MailBlocker" enabled="%(dig_settings/mail@blocked)"
            recipients="%(dig_settings/mail/to)" />
        <messagehandler class="carmensystems.dig.messagehandlers.transport.TransportDispatcher"
            mail_host="smtp.sas.dk"
            mail_port="25"/>
        [...]

        <!-- ... in site_XXX.xml ... -->
        <mail blocked="True">
            <to>nobody@carmen.se</to>
            [...]
        </mail>
    """
    def __init__(self, name=None, enabled=False, recipients=None):
        super(MailBlocker, self).__init__(name)
        try:
            self.enabled = utils.convertToBoolean(enabled)
        except:
            # No attribute set
            self.enabled = False
        self.recipients = recipients

    def start(self, services):
        """Show settings in DIG log."""
        super(MailBlocker, self).start(services)
        if self.recipients:
            enabled_msg = "enabled, all email will be sent to <%s>" % self.recipients
        else:
            enabled_msg = "enabled, no email will be sent"
        self._services.logger.info("Email blocking is %s." % ("disabled", enabled_msg)[bool(self.enabled)])

    def handle(self, message):
        if not isinstance(message.content, list):
            raise errors.MessageError("Expects message to be a list of reportDicts!")
        if self.enabled:
            for rd in message.content:
                if 'destination' in rd:
                    new_dests = []
                    for protocol, data in rd['destination']:
                        if protocol == 'mail':
                            if self.recipients:
                                try:
                                    data['to'] = self.recipients
                                except:
                                    pass
                                try:
                                    del data['cc']
                                except:
                                    pass
                                try:
                                    del data['bcc']
                                except:
                                    pass
                                new_dests.append((protocol, data))
                                self._services.logger.debug("Changing email recipient to '%s', removing all 'cc' and 'bcc'." % self.recipients)
                            else:
                                self._services.logger.debug("Removing all 'mail' destinations since parameter 'recipients' is empty.")
                        else:
                            new_dests.append((protocol, data))
                    rd['destination'] = new_dests
                    self._services.logger.debug(serializeResult([dict(destination=new_dests)]))
        else:
            self._services.logger.debug("Mail blocking disabled - not changing any email addresses.")
        return CallNextHandlerResult()

class FileWriter(MessageHandlerBase):

    def __init__(self, filename, name=None, # pylint: disable=R0913
             delimiter='', encoding='latin-1', mkdirs=True):
        super(FileWriter, self).__init__(name)

        self.__filename = os.path.abspath(filename)
        self.__delimiter = utils.toStringIfUnicode(
        utils.convertNewlines(delimiter), encoding)
        self.__encoding = encoding
        self.__mkdirs = utils.convertToBoolean(mkdirs)
        self.__baseDir = os.path.dirname(self.__filename)

        # Sanity checks.
        if not os.path.exists(self.__baseDir):
            if self.__mkdirs:
                os.makedirs(self.__baseDir)
            else:
                raise errors.ChannelConfigError(
                    "Invalid filename (%r): Directory %r doesn't exist!"
                    % (self.__filename, self.__baseDir))
        utils.validateEncoding(encoding, error=errors.ChannelConfigError)

    def handle(self, message):
        """Handle a message by writing the message content to file."""
        #Make sure the base directory exists.
        if self.__mkdirs and not os.path.exists(self.__baseDir):
            os.makedirs(self.__baseDir)

        outfile = open(self.__filename, "a")
        try:
            for r in message.content:
                outfile.write(r['content'])
        finally:
            outfile.close()
        return CallNextHandlerResult()



# Utility Classes ========================================================{{{1
class RSLookup:
    """ Dynamic selection of Report Server based on message content.
        Several Report Servers may be set up to run on different servers,
        e.g for performance reasons where each one may be loaded with a 
        unique timeframe of model data. By matching different types of
        report requests with the most suitable Report Server, better
        overall performance may be achieved.

        Using this class it is possible to control to which Report Server
        instance a particular request will be directed.
        Please see $CARMUSR/data/config/dig/queries/reports.services for
        information on the different report request types handled by the
        'services' channel.
    """

    def lookup(self, msgArr, now=None):
        start = None
        # Select non-published data if CrewRoster field 'getPublishedRoster'
        # (position 3) is 'N'
        if msgArr[0] == 'CrewRoster' and msgArr[2] == 'N':
            return 'rs_latest_short'
        # Select non-published data for CrewLanding requests
        if msgArr[0] == 'CrewLanding':
            return 'rs_latest_short'
        # Select scheduled data for CrewSlip requests
        if msgArr[0] == 'GetReport' and msgArr[1] == 'CREWSLIP':
            return 'rs_scheduled'
        # The same goes for DUTYCALC, only show activities until today's date.
        if msgArr[0] == 'GetReport' and msgArr[1] in ('DUTYCALC', 'VACATION', 'COMPDAYS', 'BOUGHTDAYS'):
            return 'rs_publish_short'
        # The same goes for DUTYOVERTIME, only show activities until today's date.
        if msgArr[0] == 'GetReport' and msgArr[1] == 'DUTYOVERTIME':
            return 'rs_latest_short'
        # Select published data and reportsever with future data, for FutureActivities requests
        if msgArr[0] == 'FutureActivities':
            return 'rs_publish'
        # Select non-published data for CrewFlight requests, and PILOTLOG request for prev or current month
        if msgArr[0] == 'CrewFlight' or msgArr[1].startswith('PILOTLOG'):
            return 'rs_latest_short'
        # Default assignment to published short report worker        
        if msgArr[0] in ('CrewBasic', 'CrewList', 'CrewRoster', 'CheckInOut'):
            return 'rs_publish_short'
        # Fallback on default report server (published data)
        return 'rs_publish'


class CioReport:
    """ Helper class encapsulating functionality to manipulate CheckInOut
        reports.
    """
    h01 = ("H01", 0, 0)  # Arial 14pt bold

    def __init__(self, report, extperkey, logname, now):
        self.report = report
        self.extperkey = extperkey
        self.logname = logname
        self.now = AbsTime(carmentime.toCarmenTime(now))

    def isSuccessfulCheckin(self):
        if self.report.find('<statusCode>000</statusCode>') != -1:
            if self.report.find('CHECK IN VERIFICATION') != -1 and \
               self.report.find('CHECK OUT VERIFICATION') == -1:
                return True
        return False

    def getAlreadyCI(self):
        msg = acci.ACCI()
        # Report Header
        msg.appendf("%-60s%s" % ('CHECK IN/CHECK OUT MESSAGE', self.now), self.h01)
        msg.append('')

        msg.append("%s   %-30s" % (self.extperkey, self.logname))
        msg.appendf("Already checked in.", self.h01)
        msg(mesno=status.OK, cico=0, perkey=self.extperkey)
                
        return msg.asXML()


# functions =============================================================={{{1
# isValidFlight =========================================================={{{2
_flightFilterCache = {}
def isValidFlight(services, msgTyp, flight):
    """ 
    This function is used for filtering out flights that should not be
    handled in SAS CMS. It was implemented for SAS Change Request CR176.
    It's primary use is for incoming ASM/SSM/SSIM messages - prior to
    handling a flight message, the dig ssim parser calls this function
    to determine if the flight should be handled or ignored. The incoming 
    feed of ASM/SSM/SSIM contains truck transports and flights of foreign 
    carriers, some of which are not relevant to the SAS CMS.

    As one of several things the function checks if the carrier code and 
    flight number is within the range specified in table flight_filter 
    (see below). If not, it returns False which means flight is not valid.

    Table flight_filter (example):
    CARRIER_CODE         FROM_FLTNO        TO_FLTNO
    ------------------------------------------------------
    QI                   2000                  2900
    LH                    100                   999
    SK                      0                  9999

    Note that dig channel needs to be restarted if flight_filter is
    reconfigured.

    The complete function with the rest of the checks is documented in
    the CR176 specification.
    """

    global _flightFilterCache
    try:
        if (flight.fd,flight.udor) in _flightFilterCache:
            services.logger.debug("Returning cached %s/%s valid=%s" % (flight.fd,flight.udor,_flightFilterCache[(flight.fd,flight.udor)]))
            return _flightFilterCache[(flight.fd,flight.udor)]

        # Decompose the flight descriptor
        f = fd_parser(flight.fd)

        # Exclude flights with a leg having service type code 'V' or 'U'
        for leg in flight.legs:
            if 'stc' in leg.data:
                if leg.data['stc'] in ('V','U'):
                    services.logger.info("Caching %s/%s valid=False (stc='%s')" % (flight.fd,flight.udor,leg.data['stc']))
                    _flightFilterCache[(flight.fd,flight.udor)] = False
                    return False

        # Issue log error if adep/ades doesn't exist in the airport table
        for stn in flight.stations:
            stn = stn.encode()
            ap = Airport(stn)
            if not ap.isAirport():
                services.logger.error("Flight %s/%s non-existing airport %s" % (flight.fd,flight.udor,stn))

        # Include flight if any leg already exists in database (Could be
        # created manually). However this check is not applicable on SDS
        # messages since they re-create a complete range of flights.
        if msgTyp[:3] != 'SDS':
            search = DaveSearch('flight_leg', [
                    ('fd', '=', flight.fd),
                    ('udor', '=', flight.udor)])
            for rec in services.getDaveConnector().runSearch(search):
                services.logger.debug("Caching %s/%s valid=True (leg exists in db)" % (flight.fd,flight.udor))
                _flightFilterCache[(flight.fd,flight.udor)] = True
                return True

        # Include flights matching carriers and flight number ranges 
        # defined in flight_filter table
        search = DaveSearch('flight_filter', [
                ('carrier_code', '=', f.carrier),
                ('from_fltno', '<=', f.number),
                ('to_fltno', '>=', f.number)])
        for rec in services.getDaveConnector().runSearch(search):
            services.logger.debug("Caching %s/%s valid=True (flight_filter match)" % (flight.fd,flight.udor))
            _flightFilterCache[(flight.fd,flight.udor)] = True
            return True

        # Include flights with any leg CAE (cabin crew employer) or 
        # CPE (cockpit employer) matching those defined in table 
        # employer_filter. If neither CAE or CPE is available, include
        # flight if carrier='SK'.
        cae_cpe_avail = False
        for leg in flight.legs:
            if 'adep' in leg.data and not Airport(leg.data['adep']).isAirport():
                services.logger.error("Flight %s/%s non-existing airport %s" % (flight.fd,flight.udor,leg.data['adep']))
            if 'ades' in leg.data and not Airport(leg.data['ades']).isAirport():
                services.logger.error("Flight %s/%s non-existing airport %s" % (flight.fd,flight.udor,leg.data['ades']))
            if 'cae' in leg.data or 'cpe' in leg.data:
                cae_cpe_avail = True
                search = DaveSearch('employer_filter', [])
                for rec in services.getDaveConnector().runSearch(search):
                    if 'cae' in leg.data and not leg.data['cae'] is None and leg.data['cae'].strip() == rec['employer'].strip() or \
                       'cpe' in leg.data and not leg.data['cpe'] is None and leg.data['cpe'].strip() == rec['employer'].strip():
                        services.logger.debug("Caching %s/%s valid=True (employer_filter match)" % (flight.fd,flight.udor))
                        _flightFilterCache[(flight.fd,flight.udor)] = True
                        return True
        if not cae_cpe_avail:
            if f.carrier.strip() == 'SK':
                services.logger.debug("Caching %s/%s valid=True (carrier='SK')" % (flight.fd,flight.udor))
                _flightFilterCache[(flight.fd,flight.udor)] = True
                return True

    except Exception, e:
        raise errors.MessageError("isValidFlight: Invalid flight: %s" % str(e))

    services.logger.info("Caching %s/%s valid=False" % (flight.fd,flight.udor))
    _flightFilterCache[(flight.fd,flight.udor)] = False
    return False


# serializeResult ========================================================{{{2
def serializeResult(reportDicts):
    out = ""
    for rd in reportDicts:
        out += "\n=========================================================\n"
        if rd.has_key('content-type'):
            out += "content-type: %s\n" % rd['content-type']
        if rd.has_key('content-location'):
            out += "content-location: %s\n" % rd['content-location']
        if rd.has_key('content'):
            out += "content: %s\n" % rd['content']
        out += "DESTINATIONS:"
        if rd.has_key('destination'):
            for dest in rd['destination']:
                out += "\n%s" % serializeDest(dest)
    return out

# serializeDest =========================================================={{{2
def serializeDest(dest):
    out = ""
    (protocol, params) = dest
    out += "protocol:%s " % protocol
    if isinstance(params,dict):
        for key,value in params.items():
            out += "%s:%s " % (key,value)
    else:
        out += params
    return out


def is_webservice(data): return any(map(has_webservice, data["destination"]))

def has_webservice(lst): return lst[0] in ["webservice"]

class StockholmTaxiWebServiceSender(MessageHandlerBase) :

    ''' Filters out those messages that shall be sent to webservice and send them to the webservice, the rest of the message
    is forwarded to the next handler'''



    def __init__(self, name=None, url=None, key=None, enabled=False, mail_defaultFrom=None, recipients=None):
        super(StockholmTaxiWebServiceSender, self).__init__(name)
        self.url = url
        self.key = key
        try:
            self.enabled = utils.convertToBoolean(enabled)
        except:
            # No attribute set
            self.enabled = False
        self.mail_defaultFrom = mail_defaultFrom
        self.recipients = recipients

    def send_to_webservice(self, report, client, key):
        result = client.service.ProcessSuti(key, report)
        #result = True
        if result :
            print "## Booking success"
            print report
        else:
            print "## Booking failure, content:"
            print report

    def handle(self, message) :

        #Filter out those messages that shall be sent to webservice
        webservice_messages = filter(is_webservice, message.content)

        #Filter out those message that shall be forwarded further in the dig channel i.e. all messages that does not have the destination webservice
        messages_to_be_forwarded = filter(lambda x: not is_webservice(x), message.content)

        if webservice_messages:
            try:
                client = Client(self.url)
                for webmessage in webservice_messages:
                    for destination in webmessage['destination']:
                        if 'webservice' in destination:
                            self.send_to_webservice(webmessage['content'],client,self.key)
            except TransportError as e: #In case messages can't be sent to remote server, send a warning email.
                messages_to_be_forwarded.extend([{'destination':
                                                      [('mail', {'to': self.recipients,
                                                                 'mfrom': self.mail_defaultFrom,
                                                                 'subject': 'DIG channel \'hotel\' error: Unable to connect to server'})],
                                                  'content-type': 'text/plain; charset=ISO-8859-1',
                                                  'content': 'Unable to connect to %s. Error code: %s. '
                                                             'Contact TaxiBokning Support: support@taxibokning.se or '
                                                             '+46 18 444 31 40 ' % (self.url, e)}])
            except URLError as e: #Mainly for test environment where a dummy URL is used.
                messages_to_be_forwarded.extend([{'destination':
                                                      [('mail', {'to': self.recipients,
                                                                 'mfrom': self.mail_defaultFrom,
                                                                 'subject': 'DIG channel \'hotel\' error: Unable to connect to server'})],
                                                  'content-type': 'text/plain; charset=ISO-8859-1',
                                                  'content': 'Unable to connect to %s. Error code: %s. '
                                                             'Check URL adress for the connection.' % (self.url, e)}])
            except Exception as e: #SKSD-8883, catching generic errors when trying to connect to webservice, allows
                                   # normal reports to be sent although webservice connection problems
                messages_to_be_forwarded.extend([{'destination':
                                                      [('mail', {'to': self.recipients,
                                                                 'mfrom': self.mail_defaultFrom,
                                                                 'subject': 'DIG channel \'hotel\' error: Unknown error'})],
                                                  'content-type': 'text/plain; charset=ISO-8859-1',
                                                  'content': 'Problem to connect to %s. Error message: %s. \n'
                                                             'Unknown error, check \'hotel\' dig channel log. \n \n' % (self.url,
                                                                                                       e.getMessage())}])

        message.setContent(messages_to_be_forwarded,reports.ReportsContentType())
        return CallNextHandlerResult()



# testdata ==============================================================={{{1
class MockReportResult(MessageHandlerBase):
    def __init__(self, name=None):
        super(MockReportResult, self).__init__(name)
    def handle(self, message):
        message.setContent([{'content-type':"text/html; charset=ISO-8859-1",
                            'content':"AAAAAAAA",
                            'destination':
                                [["mq",{'manager':"MQTRACK.SK.TEST",'queue':"A"}],
                                ["ftp",{'url':"ftp://user:passw@host:port/path"}]
                                ]
                           },
                           {'content-type':"text/html; charset=ISO-8859-1",
                            'content':"BBBBBBBB",
                            'destination':
                                [["DKreport",{'subject':"Override mail subject"}],
                                 ["mail",{'to':"kenneth.altsjo@jeppesen.com",'mfrom':"ka@crepido.com"}]
                                ]
                           },
                           {'content-type':"text/html; charset=ISO-8859-1",
                            'content':"CCCCCCCC",
                            'destination':
                                [["DKreport",{}]
                                ]
                           }
                          ], reports.ReportsContentType())
        return CallNextHandlerResult()


class CrewNotAckReportRequestBuilder(MessageHandlerBase) :

    def handle(self, message) :
        scriptname = 'report_sources.report_server.rs_crewnotification_ack'

        #Since we have an MQ header and we also can have garbage on the line, the message is
        #modified so it hopefully only consists of XML message

        i = message.content.find('''<?xml version="1.0"''')
        if i==-1 :
            modified_message='<Dummy>Dummy</Dummy>'
        else:
            modified_message=message.content[i:]
        reportArgs = modified_message
        request = reports.ReportRequest(scriptname, reportArgs, delta = True)
        message.setContent(request, reports.ReportRequestContentType())
        return CallNextHandlerResult()


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=0:
# eof
