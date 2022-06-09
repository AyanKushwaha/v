"""
This module contains message handlers related to salary interfaces
"""

import os, sys, platform
import signal
import subprocess
import carmensystems.dig.framework.carmentime as carmentime

from AbsTime import AbsTime
from carmensystems.dig.scheduler.job import JobReader
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult, SleepResult, WakeupResult, TextContentType
from carmensystems.dig.framework import errors, dave
from carmensystems.dig.messagehandlers import reports
from salary import conf
from dig.intgutils import IntgServiceConfig
from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from carmensystems.basics.atfork.atfork import basics_fork, BASICS_ATFORK_NONE
import time

metaCustomSleeper = 'dig.salary.customSleeper'
metaCustomWorkerProcess = 'dig.salary.customWorkerProcess'

FH = file(os.path.expandvars("/var/carmtmp/logfiles/DIG/x.log"),"a")

class DebugJobReader(JobReader):
    def __init__(self, *a, **kw):
        print >>FH, "Initializing"
        FH.flush()
        ret = super(DebugJobReader, self).__init__(*a, **kw)
        print >>FH, "Initialized",ret
        FH.flush()
        return ret
    def activate(self):
        print >>FH, "Activating"
        FH.flush()
        return super(DebugJobReader, self).activate()
    def done(self, message):
        print >>FH, "Done"
        print >>FH, message
        FH.flush()
        return super(DebugJobReader, self).done(message)
    def read(self, blocking):
        print >>FH, "Reading"
        print >>FH, blocking
        FH.flush()
        msg = super(DebugJobReader, self).read(blocking)
        print >>FH, "Read",msg
        FH.flush()
        return msg
class CrewStatementEmailer(MessageHandlerBase):
    """ Message handler for 43.1 Illness Report.
        The illnesshandler is a wrapper, the core functionality is
        in: ../salary/illness.py
    """
    def __init__(self, name=None, numthreads="8", mail_host="localhost", mail_port="25", mail_blocked=False, mail_blocked_to=None, mail_displayFrom="CMS", mail_defaultFrom="carmadm@carmen.se", **kwargs):
        super(CrewStatementEmailer, self).__init__(name)
        self.smtp = mail_host
        self.smtpPort = int(mail_port)
        self.defaultFrom = mail_defaultFrom or ("%s@carmen.se" % os.environ.get("USER","nobody"))
        self.displayFrom = mail_displayFrom or "CMS"
        self.numthreads = int(str(numthreads) or "8")
        self.reportdir = os.path.expandvars(conf.crewStatementsDirectory or "$CARMTMP/crewstatements")
        self.subjects = {}
        self.bodies = {}
        for k in kwargs:
            if k[:8] == 'subject_':
                self.subjects[k[8:].upper()] = kwargs[k]
            if k[:5] == 'body_':
                self.bodies[k[5:].upper()] = kwargs[k]
        if mail_blocked and str(mail_blocked).lower() in ("true", "1"):
            self.blocked = True
            self.blockedTo = mail_blocked_to or os.environ["USER"]
        else:
            self.blocked = False
        print self.__dict__
        
        
    def handle(self, message):
        runid = message.content.params['runid']
        runtype = message.content.params['runtype']
        extsys = message.content.params['extsys']
        firstdate = message.content.params.get('firstdate','')
        
        if firstdate:
            firstdate = str(AbsTime(str(firstdate)))[2:9]
        path = os.path.realpath(os.path.join(self.reportdir, runid))
        if self.blocked:
            self._services.logger.warning("Mail blocked, all email sent to %s" % self.blockedTo)
        else:
            self._services.logger.info("Production, all mail sent to crew")
        self._services.logger.info("Will email run %s, type %s, extsys %s" % (runid, runtype, extsys))
        if not os.path.isdir(path):
            self._services.logger.error("Path not found: %s" % path)
            raise errors.MessageError("No reports found for run %s" % runid)
        
        pids = []
        subject = self.subjects.get("%s_%s" % (runtype, extsys), self.subjects.get(runtype, "%s statement" % runtype))
        body = self.bodies.get("%s_%s" % (runtype, extsys), self.bodies.get(runtype, ""))
        if not runtype in self.subjects and not ("%s_%s" % (runtype, extsys)) in self.subjects:
            self._services.logger.warning("Subject not set for '%s'. Subject configuration: %r" % (runtype, self.subjects))
        if "{date}" in body: body = body.replace("{date}", firstdate)
        if "{date}" in subject: subject = subject.replace("{date}", firstdate)
        if "{extsys}" in body: body = body.replace("{extsys}", extsys)
        if "{extsys}" in subject: subject = subject.replace("{extsys}", extsys)
        if "{runid}" in body: body = body.replace("{runid}", runid)
        if "{runid}" in subject: subject = subject.replace("{runid}", runid)
        if "{runtype}" in body: body = body.replace("{runtype}", runtype)
        if "{runtype}" in subject: subject = subject.replace("{runtype}", runtype)
        def doEmail(cid):
            msg = MIMEMultipart()
            if self.blocked:
                to = self.blockedTo
            else:
                to = "%s@sas.dk" % cid
            msg['From'] = "%s <%s>" % (self.displayFrom, self.defaultFrom)
            msg['To'] = to
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject
            msg.attach(MIMEText(body+"\r\n\r\n"))
            part = MIMEBase('application', "pdf")
            part.set_payload(open(os.path.join(path, "%s.pdf" % cid),"rb").read())
            Encoders.encode_base64(part)
            mailer = SMTP(self.smtp, self.smtpPort)
            part.add_header('Content-Disposition', 'attachment; filename="%s_%s.pdf"' % (runtype, cid))
            msg.attach(part)
            self._services.logger.info("   email  %s" % cid)
            mailer.sendmail(self.defaultFrom, to, msg.as_string())
            self._services.logger.info("     done %s" % cid)
        crewreports = [x[0] for x in map(lambda s:s.split('.'), os.listdir(path)) if x[1].lower() == 'pdf' and x[0].isdigit()]
        if self.numthreads > 1 and len(crewreports) > 500:
            self._services.logger.info("Will start email process: %d mails, %d threads, ppid=%d" % (len(crewreports), self.numthreads, os.getpid()))
            crewreports = [crewreports[i::self.numthreads] for i in range(self.numthreads)]
            for i in range(self.numthreads):
                pid = basics_fork(BASICS_ATFORK_NONE)
                if not pid:
                    for cid in crewreports[i]:
                        self._services.logger.info("In child: %d: %d, %r" % (os.getpid(), len(crewreports[i]), crewreports[i]))
                        doEmail(cid)
                    os.kill(os.getpid(), 9)
                else:
                    pids.append(pid)
        else:
            for cid in crewreports:
                doEmail(cid)
        self._services.logger.info("Waiting for %d child processes to finish" % len(pids))
        for pid in pids:
            self._services.logger.info("Waiting for %d" % pid)
            os.waitpid(pid, 0)
        self._services.logger.info("All emails sent")

        
        return CallNextHandlerResult()
        
class SalaryCustomHandler(MessageHandlerBase):
    """ This messagehandler is designed to operate on manual salary jobs,
        i.e. jobs submitted from the salary application.
        It checks if the job time period is inside the period loaded by
        the report server. If not, a custom report server is started
        which loads a plan period corresponding to the requested job
        time period.

        Parameters:

            commands        Comma separated list of commands supported by
                            the salary module, e.g. start_run. 
                            Job requests whose commands parameter is not 
                            in the list are ignored by this handler.
                            Default: "start_run,start_retro"

            customServer    The alias name of the custom report server.
                            E.g. rs_latest_custom

            RSWorker        The name of the default report worker process.
                            E.g. SAS_RS_WORKER_LATEST_BATCH

            RSWorkerCustom  The name of the custom report worker process.
                            E.g. SAS_RS_WORKER_LATEST_CUSTOM

    """
    def __init__(self, commands="start_run,start_retro,release_run", 
            customServer=None, 
            RSWorker=None,
            RSWorkerCustom=None,
            name=None):
        super(SalaryCustomHandler, self).__init__(name)
        self.sleeper = CustomJobSleeper()
        self.commands = [x.strip() for x in commands.split(",")]
        self.customServer = customServer
        self.RSWorker = RSWorker
        self.RSWorkerCustom = RSWorkerCustom
        if not (customServer and RSWorker and RSWorkerCustom):
            raise errors.ChannelConfigError("customServer, RSWorker and RSWorkerCustom must be specified")

    def start(self, services):
        super(SalaryCustomHandler, self).start(services)

        # Find the plan period of the default report server
        try:
            config = IntgServiceConfig()
            k, self.svrStartExpr = config.getProperty("reportserver/%s/data_model/period_start" % self.RSWorker)
            k, self.svrEndExpr = config.getProperty("reportserver/%s/data_model/period_end" % self.RSWorker)
            services.logger.debug("%s period_start: %s" % (self.RSWorker, self.svrStartExpr))
            services.logger.debug("%s period_end: %s" % (self.RSWorker, self.svrEndExpr))
        except Exception, e:
            raise errors.ChannelConfigError("Failed finding default report server plan period: %s" % str(e))
        try:
            self.custom_rw = CustomReportWorker(config, self.RSWorkerCustom)
        except errors.ChannelConfigError, ce:
            # The initialization of the CustomReportWorker object might raise
            # ChannelConfigError in case DIG configuration is incomplete.
            raise
        except Exception, e:
            raise errors.ChannelConfigError("Could not create CustomReportWorker: %s" % e)

    def stop(self):
        if self.sleeper.isBlocking:
            self._services.logger.info("Stopping custom report worker.")
            self.custom_rw.stop()

    def handle(self, message):
        try:
            params = message.content.params
            report = params["report"]
        except:
            raise errors.MessageError('Expects message to be job request.')

        if not 'commands' in params:
            if 'SalaryServerInterface' in report:
                self._services.logger.warning("Keyword 'commands' missing. Ignoring message %s" % str(params))
                return CallNextHandlerResult()
            else:
                cmd = self.commands[0]
        else:
            cmd = params['commands']
        if not cmd in self.commands:
            self._services.logger.debug("Ignoring msg with commands='%s'" % cmd)
            return CallNextHandlerResult()

        try:    
            now = AbsTime(carmentime.toCarmenTime(self._services.now()))
            now_month_start = now.month_floor()
            now_month_end = now.month_ceil()
            now_week_start = now.week_floor()
            now_week_end = now.week_ceil()
            now_days = int(now)/1440
            now_month_start_days = int(now_month_start)/1440
            now_month_end_days = int(now_month_end)/1440
            now_week_start_days = int(now_week_start)/1440
            now_week_end_days = int(now_week_end)/1440

            startExpr = self.svrStartExpr.replace('now_month_start', str(now_month_start_days))
            startExpr = startExpr.replace('now_month_end', str(now_month_end_days))
            startExpr = startExpr.replace('now_week_start', str(now_week_start_days))
            startExpr = startExpr.replace('now_week_end', str(now_week_end_days))
            startExpr = startExpr.replace('now', str(now_days))
            endExpr = self.svrEndExpr.replace('now_month_start', str(now_month_start_days))
            endExpr = endExpr.replace('now_month_end', str(now_month_end_days))
            endExpr = endExpr.replace('now_week_start', str(now_week_start_days))
            endExpr = endExpr.replace('now_week_end', str(now_week_end_days))
            endExpr = endExpr.replace('now', str(now_days))

            svrFirstdate = eval(startExpr)
            svrLastdate = eval(endExpr)
        except Exception, e:
            raise errors.ChannelConfigError("Failed evaluating default report server plan period: %s" % str(e))

        # Determine the plan period required for processing this request
        firstdate = None
        lastdate = None
        if 'firstdate' in params and 'lastdate' in params:
            # A period is given explicitly in parameters
            try:
                firstdate = int(AbsTime(str(params['firstdate'])))/1440
                lastdate = int(AbsTime(str(params['lastdate'])))/1440
            except:
                raise errors.MessageError("Bad dates: fistdate=%r, lastdate=%r" % (params['firstdate'], params['lastdate']))
        elif 'runid' in params:
            # A period is given implicitly through a previous run
            runid = params['runid']
            search = dave.DaveSearch('salary_run_id',[("runid", '=', runid),])
            for run in self._services.getDaveConnector().runSearch(search):
                firstdate = run['firstdate']
                lastdate = run['lastdate']
            if firstdate is None or lastdate is None:
                raise errors.MessageError("Cannot process %s command: runid %s not found in database" % (cmd, runid))
        elif 'monthsBack' in params:
            monthsBack = int(params['monthsBack'])
            (y, m, d, H, M) = self._services.now().timetuple()[:5]
            this_month_start = AbsTime(y, m, 1, 0, 0)
            firstdate = int(this_month_start.addmonths(-1*monthsBack))/1440
            lastdate = int(this_month_start.addmonths(-1*(monthsBack - 1)))/1440
        else:
            self._services.logger.error("Cannot determine required job time period for command %s" % (cmd))
            return CallNextHandlerResult()

        # Check if the job time period is inside the period loaded by the
        # report server.
        self._services.logger.debug("Job period: %s-%s" % (AbsTime(firstdate*1440), AbsTime(lastdate*1440)))
        self._services.logger.debug("Server plan period: %s-%s" % (AbsTime(svrFirstdate*1440), AbsTime(svrLastdate*1440)))
        self._services.logger.debug("Default server plan period: %s-%s" % (AbsTime(now_month_start_days*1440), AbsTime(now_month_end_days*1440)))
        if firstdate < now_month_start_days or lastdate > now_month_end_days:
            # Required plan period is outside that of the default report
            # server. We need to start a server with a custom period and
            # redirect the request to it.

            # Check first if another custom request is already in progress,
            # if yes we must wait until it is finished.
            if self.sleeper.isBlocking:
                self.sleeper.nSleeping += 1
                self._services.logger.info("Suspending custom job. There are now %d suspended jobs" % (self.sleeper.nSleeping))
                return SleepResult(callback=self.__wakeupCustom, target=self.sleeper)
            self.sleeper.isBlocking = True
            # Put sleeper object in message metadata to make it available
            # for subsequent handlers
            message.metadata.update({metaCustomSleeper: self.sleeper})

            self._services.logger.info("Starting custom report worker.")
            self.custom_rw.start(now_days, firstdate, lastdate)

            # If the custom reportworker stops running during the first 10 seconds: raise an exception
            for _ in range(10):
                time.sleep(1)
                custom_rw_status = self.custom_rw.status()
                if not custom_rw_status.startswith("running"):
                    raise errors.NotStartedError("Custom report worker %s could not be started" % self.custom_rw.process)
            
            self._services.logger.debug("Custom report worker: %s" % self.custom_rw)

            message.metadata.update({metaCustomWorkerProcess: self.custom_rw})

            # Redirect request to custom server
            params.update({'server': self.customServer})

        return CallNextHandlerResult()

    def __wakeupCustom(self, message):
        self.sleeper.nSleeping -= 1
        self._services.logger.info("Suspended job woke up. There are now %d suspended jobs" % (self.sleeper.nSleeping))
        return self.handle(message)


class StopCustomServer(MessageHandlerBase):
    """ Stop a custom report server worker if started """
    def __init__(self, name=None):
        super(StopCustomServer, self).__init__(name)
    
    def handle(self, message):
        if metaCustomWorkerProcess in message.metadata:
            self._services.logger.info("Stopping custom report worker.")
            custom_rw = message.metadata[metaCustomWorkerProcess]
            custom_rw.stop()

            # Wake up any custom jobs waiting in line
            sleeper = message.metadata[metaCustomSleeper]
            self._services.logger.info("Waking up %d custom jobs waiting in line" % (sleeper.nSleeping))
            sleeper.isBlocking = False
            return WakeupResult(callback=self.__finish, target=sleeper)

        return self.__finish(message)

    def __finish(self, message):
        return CallNextHandlerResult()

class CustomJobSleeper:
    """ Sleep target, used for serializing custom salary jobs """
    def __init__(self):
        self.isBlocking = False
        self.nSleeping = 0


class CustomReportWorker:
    """Factory/help class for Custom Report worker processes."""

    #  logfile_template = '$CARMTMP/logfiles/reportworker.%s.$USER.$HOSTNAME'
    #  logfile_template_start = '$CARMTMP/logfiles/reportworker.%s.studio.$HOSTNAME'
    logfile_template = '/var/carmtmp/logfiles/reportworker.%s.${USER}.%s'
    logfile_template_start = '/var/carmtmp/logfiles/startup.reportworker.%s.${USER}.%s'

    def __init__(self, config, process, program='reportserver'):
        """Collect configuration data."""
        self.studio = os.path.expandvars('$CARMSYS/bin/studio')
        self.config = config
        self.process = process # e.g. SAS_RS_WORKER_LATEST_CUSTOM1
        self.program = program
        try:
            portal_service = self.get_config_fallback('portal_service')
        except:
            portal_service = self.get_config('portal')

        self.node = self.get_node(portal_service)
        self.portal_url = self.get_url(portal_service)
        self.rule_set = self.get_config_fallback('rule_set')
        self.parameter_file = self.get_config_fallback('parameter_file')
        self.hostname = self.get_config('hosts/%s@hostname' % self.node)
        self.logfile = os.path.expandvars(self.logfile_template % (self.process, platform.uname()[1]))
        self.logfile_start = os.path.expandvars(self.logfile_template_start % (self.process, platform.uname()[1]))

        # Popen object
        self.proc = None

    def get_args(self):
        """Return command arguments for starting the report worker process."""
        return [self.studio, '-b', ' '.join((
                'initplans',
                'python',
                'carmensystems/studio/Tracking/reportWorkerStudio.py',
                self.portal_url,
                self.rule_set,
                self.parameter_file,
                self.process,
                self.hostname,
                self.logfile,
            ))]

    def __str__(self):
        """Print status and command line for report worker (for diagnostics)."""
        return '%s %s [%s]' % (self.process, self.status(), ' '.join(self.get_args()))

    def status(self):
        """Return state of the process."""
        msg = 'not running'
        try:
            status = self.proc.poll()
            if status is None:
                msg = 'running with pid %s' % self.proc.pid
            else:
                if status < 0:
                    msg = 'terminated by signal %s' %  -status
                else:
                    msg = 'finished with return code %s' % status
        except:
            pass
        return msg

    def stop(self):
        """Stop (if not already stopped)."""
        if not self.proc is None:
            status = self.proc.poll()
            if status is None:
                os.kill(self.proc.pid, signal.SIGTERM)

    def start(self, now_days, firstdate, lastdate):
        """Start report worker and return a Popen object."""
        env = os.environ.copy()
        env['REL_START'] = "%+d" % (firstdate - now_days - 69)
        env['REL_END'] = "%+d" % (lastdate - now_days + 10)
        env['SERVER_MODE'] = "1"
        env['APPLICATION'] = 'ReportWorker'
        env['PRODUCT'] = 'CctServer'
        env['DAVE_FETCH_THREADS'] = '0'
        logfd = open(self.logfile_start, "a")
        print >>logfd, "Custom report worker starting"
        args = self.get_args()
            #args = ['/bin/bash','-c', 'source $CARMUSR/etc/carmenv.sh && %s' % ' '.join(args)]
        self.proc = subprocess.Popen(args, stdout=logfd, 
                stderr=subprocess.STDOUT, env=env)
        return self.proc

    def get_config(self, item):
        """Return configuration value or raise ChannelConfigError."""
        k, value = self.config.getProperty(item)
        if value:
            return value
        raise errors.ChannelConfigError("Could not get configuration item '%s'." % item)
        
    def get_config_fallback(self, item):
        """Return configuration value using fallback method. If value can't be
        retrieved raise ChannelConfigError."""
        k, value = self.config.getProperty("%s/%s/%s" % (self.program, self.process, item))
        if not value:
            k, value = self.config.getProperty("%s/%s" % (self.program, item))
        if value:
            return value
        raise errors.ChannelConfigError("Could not get configuration item '%s' (using fallback)." % item)

    def get_node(self, service):
        """Return DIG node (e.g. dig_node). Raise ChannelConfigError if not found."""
        for s, p, h, u in self.config.getServices():
            if s == service:
                return h
        raise errors.ChannelConfigError("Could not find node name for service '%s'." % service)

    def get_url(self, item):
        """Return URL for the service. Raise ChannelConfigError if not found."""
        value = self.config.getServiceUrl(item)
        if value:
            return value
        raise errors.ChannelConfigError("Could not find URL for service '%s'." % item)
        
