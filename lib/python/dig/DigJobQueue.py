"""
Interface to run reports in report server via dig.
"""
import datetime
from AbsDate import AbsDate
from AbsTime import AbsTime
import carmensystems.dig.scheduler.job as jobmodule
import carmensystems.dig.framework.dave as dave
from carmensystems.dig.framework.carmentime import fromCarmenTime

from utils import TimeServerUtils

class DigJobQueue(object):
    """This class is a utility to work directly against DIG's job queue.
    """
    def __init__(self, channel, submitter, reportName, delta='1', connstr=None, schemastr=None, useTimeServer=True):
        """Sets up db conn. Initializes values for jobs. Connects to timeserver.

        inparams:
         channel:    Dig channel to put job to.
         submitter:  Name of the one who submitted the job.
         reportName: Name of the report to be called by the report server.
         delta:      Default value used for the job parameter.
         connstr:    Default is taken from tablemanager, so no need to supply then.
         schemastr:  dito
         useTimeServer: If True - gets simulated time if a time server is
                        configured and available, else system time.
                        If False - Does not look for time server. Instead you
                        can specify time when calling submitJob. Use this
                        option when calling from Studio environment because
                        it's a lot less time consuming. Simulated time can
                        easily be retrieved from rave ('fundamental.%now%').

        """
        self.delta = delta
        self.reportName = reportName
        self.channel = channel
        self.submitter = submitter
        self.useTimeServer = useTimeServer

        if not connstr or not schemastr:
            from tm import TM
            connstr = TM.getConnStr()
            schemastr = TM.getSchemaStr()
        self.dbconnector = dave.DaveConnector(connstr, schemastr)

        #init time server connection
        if self.useTimeServer:
            self.timeserver = TimeServerUtils.TimeServerUtils(useSystemTimeIfNoConnection=True)
            self.__nowMethod = self.timeserver.getTime
        else:
            self.__nowMethod = datetime.datetime.now

        self.__jobMapper = jobmodule.JobMapper(connector=self.dbconnector,
                                               nowMethod=self.__nowMethod)

    def makeValuesToStrings(self, dict):
        """Converts values of dict to string representation.

        Both AbsTime & AbsDate are made str yyyymmdd
        Keys with value None or "" are removed
        All other are typecasted with str()
        """
        for key in dict.keys():
            val = dict[key]
            if isinstance(val, (AbsTime, AbsDate)):
                dict[key] = str(val)
            elif val is None or val == '':
                del dict[key]
            elif type(val) != str:
                dict[key] = str(val)
        return dict

    def submitJob(self, params, reloadModel="0", curtime=None):
        """Submits a job, with params, to be run by Report Server via DIG.

        Params should be a dictionary {'param_name':'value', ...}
        Tries to typecast values to string, if necessary.

        Return job id.
        """
        # Set default parameters for DIG's ReportTranslator
        if not params.has_key('delta'):
            params['delta'] = self.delta
        if not params.has_key('reload'):
            params['reload'] = reloadModel
        if not params.has_key('report'):
            params['report'] = self.reportName
        self.makeValuesToStrings(params)
        print 'Job parameters:'
        for pk,pv in params.items():
            print "  %s = %s" % (pk, pv)

        if curtime is None:
            start_at = self.__nowMethod()
        else:
            start_at = fromCarmenTime(int(curtime))

        job = jobmodule.Job(self.channel, self.submitter, start_at, params=params)
        self.__jobMapper.insert(job)
        return job.id
