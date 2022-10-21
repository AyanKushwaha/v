"""
This module presents an interface that can be used by e.g. reports.
"""

# imports ================================================================{{{1
import logging
import os
import warnings

import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import salary.ec.ec_perdiem_statement_mailer.Conf as conf
import utils.TimeServerUtils

from AbsTime import AbsTime
from RelTime import RelTime
from carmensystems.dave import dmf
from utils.ServiceConfig import ServiceConfig

from tm import TM
from utils.rave import RaveIterator
from cmath import log
from distutils import errors
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import os
from smtplib import SMTP
from carmensystems.basics.atfork.atfork import basics_fork, BASICS_ATFORK_NONE
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult
from datetime import datetime, timedelta

# constants and initialization ==========================================={{{1
log = logging.getLogger('salary.ec.ec_perdiem_statement_mailer.ECMailApi')
seq_salary_run = 'seq_salary_run'


# classes ================================================================{{{1

# SalaryException --------------------------------------------------------{{{2
class SalaryException(Exception):
    """ Custom Exception class for the salary system. """
    msg = ''
    def __init__(self, msg):
        self.msg = msg 
        log.error("SalaryException: %s" % msg)
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg


# SalaryAlreadyReleasedException -----------------------------------------{{{2
class SalaryAlreadyReleasedException(SalaryException):
    """ Custom Exception, we found a released run and don't have to search
    anymore. """
    pass


# SalaryWarning ----------------------------------------------------------{{{2
class SalaryWarning(UserWarning):
    """Custom warning class for warnings from the salary system."""
    pass


# Times ------------------------------------------------------------------{{{2
class Times:
    """Holds AbsTime datamembers calculated at last refresh()
    """
    def __init__(self, monthsBack=1):
        self.timeserver = utils.TimeServerUtils.TimeServerUtils(useSystemTimeIfNoConnection=True)
        self.months_back = monthsBack
        self.refresh()

    def refresh(self):
        """Refresh current time from timeserver and recalculate data members.
        """
        now_datetime = self.timeserver.getTime()
        (y, m, d, H, M) = now_datetime.timetuple()[:5]
        self.now = AbsTime(y, m, d, H, M)

        # Start of this month
        self.this_month_start = AbsTime(y, m, 1, 0, 0)

        # Start and end of previous month
        self.month_start = self.this_month_start.addmonths(-self.months_back)
        self.month_end = self.this_month_start.addmonths(1 - self.months_back)

        log.debug("Times:\n%s" % str(self))

    def __str__(self):
        """ For basic tests """
        return '\n'.join((
            "\tnow              : %s" % (self.now),
            "\tmonth_start      : %s" % (self.month_start),
            "\tmonth_end        : %s" % (self.month_end),
            "\tmonths_back      : %s" % (self.months_back),
            "\tthis_month_start : %s" % (self.this_month_start),
        ))


# exported functions ====================================================={{{1

# appendBasicData --------------------------------------------------------{{{2
def appendBasicData(runid, crewid, extperkey, extartid, amount):
    """Create a new record in 'salary_basic_data'."""
    log.debug("appendBasicData(%d, %s, %s, %s, %s)" % (runid, crewid, extperkey, extartid, amount))
    try:
        r_runid = TM.salary_run_id[(runid,)]
        r_crewid = TM.crew[(crewid,)]
        r_basicdata = TM.salary_basic_data.create((r_runid, extperkey, extartid))
        r_basicdata.amount = amount
        r_basicdata.crewid = r_crewid
    except:
        log.error("appendBasicData(%d, %s, %s, %s, %s) - Failed." % (runid, crewid, extperkey, extartid, amount))
        raise


# appendExtraData --------------------------------------------------------{{{2
def appendExtraData(runid, crewid, intartid, amount):
    """Create a new record in 'salary_extra_data'."""
    log.debug("appendExtraData(%d, %s, %s, %s)" % (runid, crewid, intartid, amount))
    try:
        r_runid = TM.salary_run_id[(runid,)]
        r_crewid = TM.crew[(crewid,)]
        r_extradata = TM.salary_extra_data.create((r_runid, r_crewid, intartid))
        r_extradata.amount = amount
    except:
        log.error("appendExtraData(%d, %s, %s, %s) - Failed." % (runid, crewid, intartid, amount))
        raise


# appendRunIdData --------------------------------------------------------{{{2
def appendRunIdData(rec):
    """Create a new record in 'salary_run_id'."""
    log.debug("appendRunIdData(%s)" % (rec))
    try:
        r_runid = TM.salary_run_id.create((rec.runid,))
        r_runid.starttime = rec.starttime
        r_runid.runtype = rec.runtype
        r_runid.admcode = TM.salary_admin_code[(rec.admcode,)]
        r_runid.selector = rec.selector
        r_runid.firstdate = rec.firstdate
        r_runid.lastdate = rec.lastdate
        r_runid.extsys = rec.extsys
        if rec.note is None:
            r_runid.note = rec.note
        else:
            r_runid.note = rec.note[:60]
    except:
        log.error("appendRunIdData(%s) - Failed." % (rec))
        raise


# checkPlanningPeriod ----------------------------------------------------{{{2
def checkPlanningPeriod(func):
    """Checks that the report worker has loaded the correct period. If not, fail immediately.
    
    Originally, this was because the custom report workers may be incorrectly re-used, but it
    is wise to do this check even if the original problem is solved, because the selection
    of report worker may be infrastructure/configuration dependent.
    """
    def check(rundata, *args, **kwargs):
        if not hasattr(rundata, 'noCheckPP') or not rundata.noCheckPP:
            start, end = rave.eval('fundamental.%loaded_data_period_start%','fundamental.%loaded_data_period_end%')
            if rundata.firstdate < start or rundata.lastdate > end:
                raise SalaryException("Incorrect planning period (%s-%s) for run (%s-%s)" % (start, end, rundata.firstdate, rundata.lastdate))
        return func(rundata, *args, **kwargs)
    return check


# getAdminCodeDescription ------------------------------------------------{{{2
def getAdminCodeDescription(admcode):
    """ Return textual description of admin code """
    log.debug("getAdminCodeDescription(%s)" % (admcode,))
    try:
        return TM.salary_admin_code[admcode,].description
    except:
        log.error("getAdminCodeDescription(%s) - Failed." % (admcode,))
        raise


# getArticleIdMap --------------------------------------------------------{{{2
def getActivityArticleIdMap(intartFilter, extsys, date):
    """
    Gets all external article ids for crew activities.
    """

    log.debug("getActivityArticleIdMap(%s, %s)" % (extsys, date))
    f = ["(extsys=%s)" % (extsys,),
         "(intartid=%s)" % intartFilter,
         "(validto>=%s)" % (date,),
         "(validfrom<=%s)" % (date,)]
    searchStr = "(&" + ''.join(f) + ")"
    log.debug("getActivityArticleIdMap(...) Search filter is '%s'" % (searchStr,))
    return list(a for a in TM.salary_crew_activity.search(searchStr))


# getAllArticleIds -------------------------------------------------------{{{2
def getAllArticleIds(intartid, extsys, firstdate=None, lastdate=None):
    """
    Gets all unique external article ids for an internal article id.
    NOTE: Returns list
    """
    log.debug("getAllArticleIds(%s, %s, %s, %s)" % (intartid, extsys, firstdate, lastdate))
    f = ["(intartid=%s)" % (intartid,), "(extsys=%s)" % (extsys,)]
    if firstdate:
        f.append("(validto>=%s)" % (firstdate,))
    if lastdate:
        f.append("(validfrom<=%s)" % (lastdate,))
    searchStr = "(&" + ''.join(f) + ")"
    log.debug("getAllArticleIds(...) Search filter is '%s'" % (searchStr,))
    # Return list of unique article ids valid in interval
    return list(set(a.extartid for a in TM.salary_article.search(searchStr)))


# getArticleIds ----------------------------------------------------------{{{2
def getArticleIds(articlelist, extsys, date):
    """
    Translation from our article ID's to theirs.  Date is an AbsTime object
    """
    log.debug("getArticleIds(%s, %s, %s)" % (articlelist, extsys, date))
    d = {}
    for value in articlelist:
        artno = _getArticleFor(value, extsys, date)
        d[value] = artno
    return d


# getCostCenter ----------------------------------------------------------{{{2
def getCostCenter(rd):
    """Return cost center (KOSTL) for SAP files."""
    log.debug("getCostCenter(%s)" % rd)
    if rd.extsys in ('DK', 'NO'):
        return conf.cost_center
    return ''


# getExternalArticleId ---------------------------------------------------{{{2
def getExternalArticleId(record, internalArticleId):
    """ Translation from our article ID to their. """
    log.debug("getExternalArticleId(%s, %s)" % (record, internalArticleId))
    return _getArticleFor(internalArticleId, record.extsys, record.firstdate)


# getExtraRecordsFor -----------------------------------------------------{{{2
def getExtraRecordsFor(runid):
    """ Get all records for a specific Run-ID """
    log.debug("getExtraRecordsFor(%s)" % runid)
    TM('salary_extra_data', 'salary_run_id')
    return TM.salary_run_id[runid,].referers('salary_extra_data', 'runid')


# getDailyRecordsFor -----------------------------------------------------{{{2
def getDailyRecordsFor(runid):
    """ Get all day-by-day records for a specific Run-ID.
        The data is indexed by crewid, external article id and
        day offset, i.e. daily['12345']['tst']['000'] is the
        record for crewid '12345', external article id 'tst' for the
        first day in the period. """

    daily = {}
    for rec in getExtraRecordsFor(runid):
        try:
            # Unpack extartid and day offset from intartid:
            # 'apa001' => 'apa0' and '01'
            offset = int(rec.intartid[-2:])
            extartid = rec.intartid[:-2]
            extperkey = rec.crewid.id
            if not extperkey in daily:
                daily[extperkey] = {}
            if not extartid in daily[extperkey]:
                daily[extperkey][extartid] = []
            daily[extperkey][extartid].append((offset, int(rec.amount)))
        except:
              log.error("getDailyRecordsFor(%d, %s) - Failed." % (runid, rec)) # Fix it !
    return daily


# getLastOvertimeRunId ---------------------------------------------------{{{2
def getLastOvertimeRunId(firstdate, lastdate, region, type):
    """ Get last overtime run id """
    maxdate = firstdate
    lastrunid = None
    # ignore Test runs and Retro runs
    searchString = '(&(!(admcode=R))(!(admcode=T))(firstdate>=%s)' % firstdate
    searchString += '(lastdate<=%s)(runtype=%s)(extsys=%s))' % (lastdate, type, region)
    for r in TM.salary_run_id.search(searchString):
        if r.starttime >= maxdate: 
            maxdate = r.starttime
            lastrunid = r.runid
    return lastrunid


# getNextRunId ----------------------------------------------------------{{{2
def getNextRunId():
    """ Get next available run id """
    log.debug("getNextRunId()")
    try:
        next_run_id = dmf.BorrowConnection(TM.conn()).getNextSeqValue(seq_salary_run)
    except:
        # This is to enable salary file from the test menu in the history user,
        # where the salary run id sequence is not available
        max_run_id = -1
        for r in TM.salary_run_id:
            if r.runid >= max_run_id: 
                max_run_id = r.runid
                next_run_id = max_run_id + 1
    return next_run_id


# getPerDiemGroup --------------------------------------------------------{{{2
def getPerDiemGroup(salarysys, retrofile=None, context='sp_crew'):
    """Return list of (base, maincat, alpha_group), each entry in the list
    will produce a separate PerDiem statement (PDF). This to reduce the 
    number of pages in each report. See MDLRAVE-1314."""
    ret = []
    for base in conf.bases.get(salarysys, [salarysys]):
        for maincat in ('CC', 'FD'):
            for agroup in conf.alphabet_groups:
                ret.append((base, maincat, agroup))
    return ret


# getRecordsFor ----------------------------------------------------------{{{2
def getRecordsFor(runid):
    """ Get all records for a specific Run-ID """
    log.debug("getRecordsFor(%s)" % runid)
    TM('salary_basic_data', 'salary_run_id')
    return TM.salary_run_id[runid,].referers('salary_basic_data', 'runid')


# getRecordsForCrewId ----------------------------------------------------{{{2
def getRecordsForCrewId(crewid, runid=None, firstdate=None, lastdate=None,
                        extartids=()):
    """
    Get all records for specific crew.
    NOTE: Returns iterator - to get list use list(getRecordsForCrewId(...))
    """
    def match(r):
        try:
            return (
                (runid is None or r.runid.runid == runid)
                and
                (firstdate is None or r.runid.firstdate >= firstdate)
                and
                (lastdate is None or r.runid.lastdate <= lastdate)
                and
                (not extartids or r.extartid in extartids)
            )
        except:
            return False
    log.debug("getRecordsForCrewId(%s, %s, %s, %s)" % (crewid, runid, firstdate, lastdate))
    TM('crew', 'salary_basic_data')
    return (x for x in TM.crew[(crewid,)].referers('salary_basic_data', 'crewid')
            if match(x))


# getRecordsForExtPerKey -------------------------------------------------{{{2
def getRecordsForExtPerKey(extperkey, runid=None, firstdate=None, lastdate=None):
    """
    Get all records for specific crew 
    NOTE: Returns iterator, to get list use list(getRecordsForExtPerKey(...))
    """
    log.debug("getRecordsForExtPerKey(%s, %s, %s, %s)" % (extperkey, runid, firstdate, lastdate))
    f = ["(extperkey=%s)" % (extperkey,)]
    if runid:
        f.append("(runid=%d)" % (runid,))
    if firstdate:
        f.append("(runid.firstdate>=%s)" % (firstdate,))
    if lastdate:
        f.append("(runid.lastdate<=%s)" % (lastdate,))
    filter = "(&" + ''.join(f) + ")"
    log.debug("getRecordsForExtPerKey(...). Search filter is '%s'"  % (filter,))
    return TM.salary_basic_data.search(filter)


# getRunIdData -----------------------------------------------------------{{{2
def getRunIdData(runid):
    """ Return data from the database for a specific Run-ID. """
    log.debug("getRunIdData(%d)" % (runid))
    try:
        return TM.salary_run_id[(runid,)]
    except:
        log.error("getRunIdData(%d) - Failed." % (runid,))
        raise


# getUnreleasedRun -------------------------------------------------------{{{2
def getUnreleasedRun(rundata):
    """ Return runid for the latest unreleased run. """
    log.debug("getUnreleasedRun(%s)" % (rundata))
    try:
        return max(_unreleasedRuns(rundata))
    except (ValueError, SalaryAlreadyReleasedException), e:
        log.info("No unreleased run found for %s %s" % (rundata.runtype, rundata.extsys))
        return None


# initDirectory ----------------------------------------------------------{{{2
def initDirectory(dir):
    """Create directory if not already exists."""
    if not os.path.exists(dir):
        try:
            log.info("Creating directory '%s'." % (dir))
            os.makedirs(dir, 0775)
        except Exception, e:
            raise SalaryException('Unable to create directory "%s". %s' % (dir, e))
    if os.access(dir, os.F_OK) == 0 and os.access(dir, os.W_OK) == 0:
        raise SalaryException('Unable to write to directory "%s"' % (dir))


# now_rave_time ----------------------------------------------------------{{{2
def now_rave_time():
    """Return current Rave time."""
    log.debug("now_rave_time()")
    now, = rave.eval('fundamental.%now%')
    return now


# releaseExportFile ------------------------------------------------------{{{2
def releaseExportFile(rd, expfile):
    """Release an export file by creating a softlink to the file with a
    different name."""
    log.debug("releaseExportFile(%s, %s)" % (rd, expfile))
    try:
        sc = ServiceConfig()
        filename = sc.getProperties(conf.release_conf_fmt % (
            conf.release_file_names[rd.runtype][rd.extsys]))[0][1]
        directory = sc.getProperties(conf.release_conf_fmt % (
            conf.release_dir))[0][1]
        initDirectory(directory)
        filepath = os.path.join(directory, filename)
        try:
            os.unlink(filepath)
        except OSError:
            pass
        os.symlink(expfile, filepath)
        log.debug("File '%s' has been linked to '%s'." % (expfile, filepath))
        # To make this consistent with 'run.export()'
        return filepath
    except:
        log.error("releaseExportFile(%s, %s) - Failed." % (rd, expfile))
        raise


# releaseRun -------------------------------------------------------------{{{2
def releaseRun(rd):
    """Release run by setting 'releasedate' to now."""
    log.debug("releaseRun(%s)" % rd)
    t = Times()
    TM.salary_run_id[(rd.runid,)].releasedate = t.now
    log.debug("Runid %d released" % (rd.runid))


# reportBaseName ---------------------------------------------------------{{{2
def reportBaseName(runid, ext='.pdf', subtype=''):
    """Generate a file name for a report output file based on runid."""
    return ''.join((reportPrefix(runid), subtype, ext))


def reportDirectory():
    """Create directory if not existing."""
    dir = conf.reportDirectory or os.path.join(os.environ['CARMTMP'], "www")
    initDirectory(dir)
    return dir

def crewStatementsDirectory():
    """Create directory if not existing."""
    dir = conf.crewStatementsDirectory or os.path.join(os.environ['CARMTMP'], "crewstatements")
    initDirectory(dir)
    return dir


# reportFileName ---------------------------------------------------------{{{2
def reportFileName(runid, ext=".pdf", subtype=''):
    """Generate a file name for a report output file based on runid."""
    return os.path.join(reportDirectory(), reportBaseName(runid, ext, subtype))


# reportPrefix -----------------------------------------------------------{{{2
def reportPrefix(runid):
    """Return prefix based on runid (int)."""
    return conf.report_prefix_fmt % runid


# runReport --------------------------------------------------------------{{{2
def runReport(rpt, runid, format=prt.PDF, args={}, filename=None):
    """Run PRT Report, return filename of generated report."""
    log.debug("runReport(%s, %s, format=%s, args=%s, filename=%s)" % (rpt,
        runid, format, args, filename))
    if filename is None:
        if format == prt.HTML:
            filename = reportFileName(runid, ext='.html')
        else:
            filename = reportFileName(runid)
    return prt.generateReport(rpt, filename, format, args)

def runXmlReport(rpt, runid, args={}, filename=None, render=False, outfile=None):
    """Run Report through the PRT emulation class, return filename of generated report."""
    from utils.prtmf.override import generate
    log.debug("runXmlReport(%s, %s, args=%s, filename=%s)" % (rpt,
        runid, args, filename))
    if filename is None:
        filename = reportFileName(runid, ext='.xml')
    if filename[-4:] != '.xml': filename += '.xml' 
    generate(rpt, filename, prt.PDF, args)
    if render:
        dirname = filename[:-4]
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        from utils.prtmf.render import render
        if not outfile: outfile = '%s/.pdf' % dirname
        render(filename, filename[:-4]+".pdf", False, False)
        render(filename, outfile, False, True)
        outdir = os.path.join(crewStatementsDirectory(), str(runid))
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        contents = []
        for f in os.listdir(dirname):
            contents.append(f)
            if f[-4:] == '.pdf':
                if os.path.exists(os.path.join(outdir, f)):
                    os.unlink(os.path.join(outdir, f))
                os.symlink(os.path.join(dirname, f), os.path.join(outdir, f))
                if args['fromStudio'] == False and args['sendMail'] == True:
                    CSE = CrewStatementEmailer()
                    CSE.handle(message=args, path=os.path.join(dirname, f))
        print >>file(os.path.join(dirname, "index.html"),"w"), (
          "<html><title>Index of %s</title><body><ul>" % outdir +
          '\n'.join(['<li><a href="%s">%s</a></li>' % (x,x) for x in contents]) + 
          "</ul></body></html>"
        )
    return filename


# setRunIdSeqNo ---------------------------------------------------------{{{2
def setRunIdSeqNo():
    """Set the sequence number to be the largest possible value in
    salary_run_id. Since we have some migrated data, we want our new runs to
    have sequence numbers that are larger than the largest value of the
    migrated data.  This function should only be called once, at
    installation."""
    log.debug("setRunIdSeqNo()")
    conn = dmf.BorrowConnection(TM.conn())
    conn.rquery('select max(runid) from salary_run_id', None)
    max, = conn.readRow().valuesAsList()
    conn.endQuery()
    log.debug("...setting sequence number of '%s' to '%d'." % (seq_salary_run, max))
    conn.setSeqValue(seq_salary_run, max)
    return max


# warn -------------------------------------------------------------------{{{2
def warn(msg):
    """Warn using warnings mechanism (allowing filtering etc)."""
    warnings.warn(msg, SalaryWarning, stacklevel=2)


# zap --------------------------------------------------------------------{{{2
def zap(runid):
    """ Remove all data connected to a run id """
    log.debug("zap(%d)" % (runid,))
    try:
        # Order is important
        _removeExtraData(runid)
        _removeBasicData(runid)
        _removeRunId(runid)
    except:
        log.error("zap(%d) - Failed." % (runid,))
        raise


# zapAll -----------------------------------------------------------------{{{2
def zapAll():
    """ Remove all data connected to a run id """
    log.debug("zapAll()")
    TM.salary_run_id.removeAll()
    TM.salary_basic_data.removeAll()


# private functions ======================================================{{{1

# _getArticleFor ---------------------------------------------------------{{{2
def _getArticleFor(intartid, extsys, date):
    """
    Translation from one article ID in our system to a representation in their
    system. Note that the date must be an AbsTime object.
    """
    log.debug("_getArticleFor(%s, %s, %s)" % (intartid, extsys, date))
    extartid, = rave.eval('salary.%%salary_system_article_id_for_system%%("%s", "%s", %s)' % (intartid, extsys, date))
    if not extartid:
        raise SalaryException("No external article id found for internal id '%s' in system %s for the date %s." % (intartid, extsys, date))
    return extartid


# _removeRunId -----------------------------------------------------------{{{2
def _removeRunId(runid):
    """ Removes a run id """
    log.debug("_removeRunId(%d)" % (runid))
    for r in TM.salary_run_id.search('(runid=%s)' % (runid)):
        log.debug("... removing %d" % (r.runid))
        r.remove()


# _removeBasicData -------------------------------------------------------{{{2
def _removeBasicData(runid):
    """ Removes basic data for run id """
    log.debug("_removeBasicData(%d)" % (runid))
    for r in TM.salary_basic_data.search('(runid=%s)' % (runid)):
        log.debug("... removing %d" % (r.runid.runid))
        r.remove()


# _removeExtraData -------------------------------------------------------{{{2
def _removeExtraData(runid):
    """ Removes extra data for run id """
    log.debug("_removeExtraData(%d)" % (runid))
    for r in TM.salary_extra_data.search('(runid=%s)' % (runid)):
        log.debug("... removing %d" % (r.runid.runid))
        r.remove()


# _unreleasedRuns --------------------------------------------------------{{{2
def _unreleasedRuns(rundata):
    """Returns list of runs that have not been released within chosen
    period"""
    log.debug("_unreleasedRuns(%s)" % (rundata))
    L = []
    if rundata.admcode is None:
        log.debug("...setting admcode to 'N'")
        rundata.admcode = 'N'
    for r in TM.salary_run_id.search(
            '(&(runtype=%s)(extsys=%s)(firstdate<%s)(lastdate>%s)(admcode=%s))' % (
            rundata.runtype, rundata.extsys, rundata.lastdate, rundata.firstdate, rundata.admcode)):
        if r.releasedate is not None:
            raise SalaryAlreadyReleasedException('Found at least one released run (%d).' % r.runid)
        L.append(r.runid)
    return L

class CrewStatementEmailer(MessageHandlerBase):
    def __init__(self, name=None, numthreads="8", mail_host="localhost", mail_port="25", mail_displayFrom="CMS", mail_defaultFrom="carmadm@carmen.se", **kwargs):
        super(CrewStatementEmailer, self).__init__(name)
        self.smtp = mail_host
        self.smtpPort = int(mail_port)
        self.defaultFrom = mail_defaultFrom or ("%s@carmen.se" % os.environ.get("USER","nobody"))
        self.displayFrom = mail_displayFrom or "CMS"
        self.numthreads = int(str(numthreads) or "8")
        self.subjects = "EC Per Diem Statement {date} - DO NOT REPLY"
        self.bodies = "Enclosed please find you personal ECPerDiem Statement for {date}.\n\nBest regards \nSAS Crew Systems."
        print self.__dict__
        
        
    def handle(self, message, path):
        runid = message['runid']
        runtype = message['runtype']
        extsys = message['extsys']
        firstdate = message.get('firstdate','')
        
       
        path = os.path.realpath(path)
        print("Will email run %s, type %s, extsys %s" % (runid, runtype, extsys))
       
        
        subject = self.subjects
        body = self.bodies
        cid = path.split("/")[-1]
        previous_mon = datetime.now() - timedelta(days=31)
        date = previous_mon.strftime("%b%Y")
        if "{date}" in body: body = body.replace("{date}",  date)
        if "{date}" in subject: subject = subject.replace("{date}", date)
    
        msg = MIMEMultipart()
        to = "%s@sas.%s" % (cid.split(".")[0], extsys.lower())
        msg['From'] = "%s <%s>" % (self.displayFrom, self.defaultFrom)
        msg['To'] = to
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(body+"\r\n\r\n"))
        part = MIMEBase('application', "pdf")
        part.set_payload(open(path,"rb").read())
        encoders.encode_base64(part)
        mailer = SMTP(self.smtp, self.smtpPort)
        part.add_header('Content-Disposition', 'attachment; filename="ECPerDiemReport_%s_%s"' % (date, cid))
        msg.attach(part)
       print("   email  %s" % cid)
        try:
            isMailSent = mailer.sendmail(self.defaultFrom, to, msg.as_string())
        except Exception as e:
            print("mail not sent:"+str(e))
        print("     done %s" % cid)

        
        return CallNextHandlerResult()
