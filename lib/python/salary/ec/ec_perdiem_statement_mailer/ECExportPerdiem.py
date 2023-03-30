"""
This module contains the logic for running and exporting PerDiem and OverTime.
These functions can be called from either a batch job or from a user interface.
"""

# imports ================================================================{{{1
import logging
import os
import datetime
import time

import salary.ec.ec_perdiem_statement_mailer.ECMailApi as api
import salary.ec.ec_perdiem_statement_mailer.Conf as conf
import utils.xmlutil as xml

from AbsTime import AbsTime
from RelTime import RelTime
from utils.fmt import NVL
from tempfile import mkstemp
from tm import TM
import traceback
import carmensystems.rave.api as rave

# exports ================================================================{{{1
__all__ = ['export', 'report', 'run']


# logging ================================================================{{{1
log = logging.getLogger('salary.run')


# classes ================================================================{{{1

# GenericReport ----------------------------------------------------------{{{2
class GenericReport(dict):
    """
    Base class for creating report with totals of a specific run.  This report
    will be sent by mail.
    """
    def __init__(self, rundata):
        dict.__init__(self)
        self.rundata = rundata
        for b in api.getRecordsFor(rundata.runid):
            (count, sum) = self.get(b.extartid, (0, 0))
            count += 1
            sum += b.amount
            self[b.extartid] = (count, sum)

    def report(self):
        raise NotImplementedError('report must be implemented by subclass.')


# GenericRun -------------------------------------------------------------{{{2
class GenericRun(object):
    """
    This is a base class for the run type classes in the 'salary.type' package.
    Such a class should implement the methods:

        rosters(self)
                        returning a list objects with roster values.

        save(self, rec, type, value)
                        saving a crew record

        And, for each articletype, a method with the same name as the internal
        article ID, that returns a value.

        e.g.:
        # def LRHIGH(self, rec):
        #    ...
        #    return a_value
    """
    def __init__(self, rundata, articles=[], extra_articles=[], article_types=None):
        self.articles = articles
        self.articleCodes = {}
        self.extra_articles = extra_articles
        self.articleTypes = article_types
        self.rundata = rundata
        self.data = BasicData()
        self.extradata = ExtraData()
        if not 'isCC4EXNG' in dir(self):
            self.isCC4EXNG = True

    def __str__(self):
        return 'Generic Run'

    def commit_changes(self):
        """Commit changes to model and create Validity Check report."""
        try:
            runid = api.getNextRunId()
            self.rundata.save(runid)
        except:
            # Adjust run id sequence number and try again
            api.setRunIdSeqNo()
            runid = api.getNextRunId()
            self.rundata.save(runid)
        self.data.save(runid)
        self.extradata.save(runid)
        self.validity_check(runid)
        return runid

    def get_codes(self):
        """ Create dictionary of article codes for speedy lookup. """
        articles_to_be_removed = []
        for a in self.articles:
            try:
                articleId = api.getExternalArticleId(self.rundata, a)
                self.articleCodes[a] = articleId
            except api.SalaryException:
                articles_to_be_removed.append(a)
                pass

        for a in articles_to_be_removed:
            self.articles.remove(a)
            log.warning("Remove %s from valid articles" % a)

    def get_article_type(self, article):
        """ Get type of article, to determine which field to put the value in
            'amount' : e.g. an monetary amount, SEK1000
            'number' : e.g. a quantity of something, 10:00 -> 10 (hours)

            None is interpreted as 'number' """

        if self.articleTypes != None:
            return self.articleTypes[article]
        else:
            return None

    def run(self):
        """ This is the entry point. """
        fail_msg = "No rosters qualified for %s found." % self
        if self.rundata.admcode == 'N':
            self.normal()
        elif self.rundata.admcode == 'T':
            self.test()
        else:
            fail_msg = "Unknown run type '%s'." % self.rundata.admcode
        # This is commented to enable generating files with no data, e.g. for the per diem jobs
        # if not self.data and not self.extradata:
        #     raise api.SalaryException(fail_msg)
        return self.commit_changes()

    def _normal_test(self):
        self.get_codes()
        r = self.rosters()
        self.save_run(r)

    def save_run(self, rosters):
        for crew in rosters:
            for a in self.articles:
                func = getattr(self, a)
                value = func(crew)
                if value is not None and int(value) != 0:
                    self.save(crew, a, value)
            for e in self.extra_articles:
                func = getattr(self, e)
                value = func(crew)
                if value is not None and int(value) != 0:
                    self.save_extra(crew, e, value)

    # Right now, both these are the same
    normal = _normal_test
    test = _normal_test

    def release(self):
        """Perform release activities, specific for this run type."""
        pass

    def rosters(self):
        """Sub classes need to implement this."""
        raise NotImplementedError("rosters() part of the interface and must be implemented.")

    def validity_check(self, runid):
        """Run the validity check report."""
        try:
            return api.runReport(conf.validity_check_report, runid, args="PLAN=1",
                    filename=api.reportFileName(runid, ext=".pdf",
                        subtype=conf.validity_check_subtype))
        except Exception, e:
            traceback.print_exc()
            log.warning("Failed running validity check for '%s'. [%s]" % (self.rundata.runid, e))

    def save(self, rec, article, value):
        """ Save a record.
            If an article type is found for the article it is appended to the
            extartid, i.e. 042:amount as opposed to 042"""
        extartid = self.articleCodes[article]
        articleType = self.get_article_type(article)
        if articleType != None:
            extartid = extartid + ':' + articleType
        self.data.append(rec.crewId, rec.empNo, extartid, value)

    def save_extra(self, rec, article, value, offset=None):
        """ Save extra data.
            If a day offset is supplied, it is appended to the extartid,
            i.e. 04201 for extartid 042 the second day of the period """

        # Build article id by combining extartid and day number,
        # i.e. extartid 'apa' for first day in period yields 'apa01'
        if offset == None:
            extartid = self.articleCodes[article]
        else:
            extartid = self.articleCodes[article] + "%02d" % offset
        self.extradata.append(rec.crewId, extartid, value)


    def times100(self, value):
        """ Return integer where value is multiplicated with 100 """
        if int(NVL(value)) == 0:
            return 0
        return int(round(value * 100.0))

    def hours100(self, value):
        """ Return integer from a RelTime where value is the number of hours
        (2 decimals) multiplicated with 100 """
        if int(NVL(value)) == 0:
            return 0
        (hhh, mm) = (value, 0) if type(value) == int else value.split()
        return int(round((hhh + (mm / 60.0)) * 100.0))

    def minutes100(self, value):
        """ Return integer from a RelTime where value is the number of minutes
        (2 decimals) multiplicated with 100 """
        if int(NVL(value)) == 0:
            return 0
        (hhh, mm) = value.split()
        return 6000 * hhh + 100 * mm


# RunData ----------------------------------------------------------------{{{2
class RunData(dict):
    """
    Container for parameters and flags for a run.

    Examples:
       Case 1 - create simple object
       -----------------------------
       rd = RunData()    # Default values (no runid)
       rd = RunData(3)   # Values from runid = 3
       rd = RunData(**{'admcode': "N", 'runid': 3}) # Values from dict
       rd = RunData(admcode="N", runid=3)           # Named values

       Case 2 - create object with values from temporary table
       -------------------------------------------------------
       rd = RunData.fromTempRec(temptable_record)

       Case 3 - create object with values from persistent table
       --------------------------------------------------------
       rd = RunData.fromTableRec(table_record)

       rd.set(admcode="R")                     # Change single value
       rd.set(admcode="N", exportformat="CSV") # Change several values

       rd.save()                               # Save to persistent table
    """

    # Available field names
    _fieldlist = ('admcode', 'exportformat', 'extsys', 'firstdate', 'lastdate',
                  'note', 'runid', 'runtype', 'selector', 'spooldir', 'starttime', 'fromStudio', 'monthsBack', 'noCheckPP', 'sendMail')

    def __init__(self, **k):
        """ Use some reasonable default values. """
        dict.__init__(self)
        if 'runid' in k:
            self.runid = int(k['runid'])
        else:
            self.runid = None
        self.admcode = k.get('admcode', None)
        self.extsys = k.get('extsys', None)
        self.note = k.get('note', None)
        self.runtype = k.get('runtype', conf.allowedRunTypes[0])
        self.selector = k.get('selector', "")

        # Non persistent
        self.monthsBack = int(k.get('monthsBack', 1))
        t = Times(self.monthsBack)

        # Persistent (contd.)
        self.lastdate = AbsTime(k.get('lastdate', t.month_end))
        self.firstdate = AbsTime(k.get('firstdate', t.month_start))
        self.starttime = AbsTime(k.get('starttime', t.now))

        # Non-persistent fields
        self.fromStudio = k.get('fromStudio', False)
        self.spooldir = k.get('spooldir', conf.exportDirectory)
        self.exportformat = k.get('exportformat', conf.allowedExportFormats[0])
        self.noCheckPP = k.get('noCheckPP', False)
        self.sendMail = k.get('sendMail', False)

    def __getattr__(self, name):
        if name in self._fieldlist:
            return self[name]
        else:
            raise AttributeError("Attribute %s does not exist for %s" % 
                    (name, self.__class__.__name__))

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]

    def __str__(self):
        """ For basic tests. """
        arr = []
        void = []
        arr.append("<RunData")
        for key in self:
            if key in self._fieldlist:
                if self[key] is None:
                    void.append(key)
                else:
                    arr.append('%s="%s"' % (key, self[key]))
        if void:
            arr.append('_void="%s"' % (','.join(void)))
        arr.append("/>")
        return '  '.join(arr)

    def save(self, runid):
        """ Save record to database. """
        self.runid = runid
        api.appendRunIdData(self)

    def set(self, **d):
        """ Change one or a couple of values. """
        for (k, v) in d.iteritems():
            if k in self._fieldlist:
                self[k] = v

    def extsys_for_db(self):
        """work-around to be able to use two salary systems for SE: PALS and HrPlus"""
        return self.extsys

    def extsys_for_rave(self):
        """work-around to be able to use two salary systems for SE: PALS and HrPlus"""
        if (self.extsys == 'S2') or (self.extsys == 'S3'):
            return 'SE'
        else:
            return self.extsys


# Times ------------------------------------------------------------------{{{2
class Times(object):
    """A variant of api.Times(), no times will be fetched unless asked for."""
    def __init__(self, months_back=1):
        self.__t = None
        self.months_back = months_back

    def __getattr__(self, x):
        if self.__t is None:
            self.__t = api.Times(self.months_back)
        return getattr(self.__t, x)


# BasicData --------------------------------------------------------------{{{2
class BasicData(list):
    """
    List of basic data records.
    To keep referential integrity, the saving is delayed until after all data
    is collected.
    """
    def append(self, crewid, extperkey, extartid, amount):
        """ Add record to list, but only if value is different from None or
        zero (0). """
        if amount is not None and int(amount) != 0:
            list.append(self, BasicDataRecord(crewid, extperkey, extartid, amount))

    def save(self, runid):
        for r in self:
            r.save(runid)


# ExtraData --------------------------------------------------------------{{{2
class ExtraData(BasicData):
    """
    List of extra data records.
    To keep referential integrity, the saving is delayed until after all data
    is collected.
    """
    def append(self, crewid, intartid, amount):
        """ Add record to list, but only if value is different from None or
        zero (0). """
        if amount is not None and int(amount) != 0:
            list.append(self, ExtraDataRecord(crewid, intartid, amount))


# BasicDataRecord --------------------------------------------------------{{{2
class BasicDataRecord:
    """
    Container for basic data (crew, extperkey, extartid, amount).
    """
    def __init__(self, crewid, extperkey, extartid, amount):
        self.crewid = crewid
        self.extperkey = extperkey
        self.extartid = extartid
        self.amount = amount

    def __str__(self):
        return '<BasicDataRecord crewid="%s" extperkey="%s" extartid="%s" amount="%s">' % (
                self.crewid, self.extperkey, self.extartid, self.amount)

    def save(self, runid):
        """ Save the record. """
        try:
            api.appendBasicData(runid, self.crewid, self.extperkey, self.extartid, self.amount)
        except Exception as e:
            print "-- DEBUG:ERROR: run:BasicDataRecord:save: Exception: ", e


# ExtraDataRecord --------------------------------------------------------{{{2
class ExtraDataRecord:
    """
    Container for extra data (r_runid, r_crewid, intartid, amount).
    """
    def __init__(self, crewid, intartid, amount):
        self.crewid = crewid
        self.intartid = intartid
        self.amount = amount

    def __str__(self):
        return '<ExtraDataRecord crewid="%s" intartid="%s" amount="%s">' % (
                self.crewid, self.intartid, self.amount)

    def save(self, runid):
        """ Save the record. """
        api.appendExtraData(runid, self.crewid, self.intartid, self.amount)


# RunFiles ---------------------------------------------------------------{{{2
class RunFiles:
    """
    This class is responsible for all file i/o to the export file.
    The output file is opened at the first write.
    """
    def __init__(self, r, is_release=False):
        self.rundata = r
        self.__is_open = False
        self.fh = None
        self._initSpoolDir()

        if is_release and self.rundata.extsys == 'S3' and self.rundata.runtype == 'PERDIEM':
            st = time.strptime(str(self.rundata.starttime), '%d%b%Y %H:%M')
            self.name = os.path.expandvars("$CARMDATA/REPORTS/SALARY_RELEASE/pdiem_cms_se_%04d%02d%02d_1.dat" % (st.tm_year, st.tm_mon, st.tm_mday))
        else:
            self.name = self.getNextFileName("%s%06d" % (self.rundata.extsys, self.rundata.runid))
        log.info("RunFiles: Output files will be placed in directory '%s'" % (r.spooldir))

    def __str__(self):
        """ For basic tests. """
        return ' '.join((self.name,
            ("(handle)", "(no handle")[self.fh is None],
            ("(closed)", "(open)")[self.__is_open],
        ))

    def close(self):
        """ Close open file (if open). """
        if self.__is_open:
            try:
                self.fh.close()
                self.__is_open = False
            except Exception, e:
                raise api.SalaryException('Unable to close file "%s". %s' % (self.name, e))

    def getNextFileName(self, stem):
        """ Construct a sequential file name. """
        extensions = [''] + conf.fileExtensions.values()
        for i in xrange(1, 100):
            challenge = "%s/%s-%02d" % (self.rundata.spooldir, stem, i)
            for e in extensions:
                # If e.g. X-01.html is occupied try with X-02
                if os.path.exists(challenge + e):
                    break
            else:
                filename = challenge + conf.fileExtensions.get(self.rundata.exportformat, "")
                log.info("RunFiles: Output filename is '%s'" % (filename,))
                return filename
        raise api.SalaryException("Too many files with this name: %s" % (stem))

    def write(self, text):
        """ Write to a text file, open the file if not already open. """
        if not self.__is_open:
            try:
                self.fh = open(self.name, "w")
                self.__is_open = True
            except Exception, e:
                raise api.SalaryException('Unable to open file "%s" for appending. %s' % (self.name, e))
        print >>self.fh, text

    # private methods ----------------------------------------------------{{{3
    def _initSpoolDir(self):
        """ Create spool directory if not already existing. """
        api.initDirectory(self.rundata.spooldir)


# SalaryRecord ------------------------------------------------------------{{{2
class SalaryRecord:
    """
    This class loads a plugin format specification (files Record_XX_XX.py)
    for the chosen record type.  The plugin is responsible for the actual
    formatting.
    """
    def __init__(self, runfiles):
        """ runfiles is a RunFiles object. """
        self.runfiles = runfiles
        self.recordformatter = self.loadModule(runfiles.rundata)
        log.debug("SalaryRecord: '%s'" % (self.__str__()))

    def __str__(self):
        """ For basic tests. """
        return "%s --> extsys = (%s), format = (%s)" % (
            self.runfiles.name,
            self.runfiles.rundata.extsys,
            self.runfiles.rundata.exportformat
        )

    def close(self):
        self.runfiles.close()

    def loadModule(self, r):
        """
        Load plugin by looking for Python class in 'conf.fileRecordPackage'.
        The name of the module is decided by the extsys and exportformat fields
        of the rundata struct.
        """
        modName = "%s_%s" % (r.extsys, r.exportformat)
        try:
            module = __import__("%s.%s" % (conf.fileRecordPackage, modName), (), (), modName)
            obj = getattr(module, modName)
            # Return instance
            return obj(self.runfiles)
        except:
            log.error("SalaryRecord: Could not load module %s." % (modName,))
            raise

    def write_pre(self):
        """ Write out preamble for the record. """
        if hasattr(self.recordformatter, "pre"):
            val = self.recordformatter.pre()
            if not val is None:
                self.runfiles.write(val)

    def write_post(self):
        """ Write out postamble for the record. """
        if hasattr(self.recordformatter, "post"):
            val = self.recordformatter.post()
            if not val is None:
                self.runfiles.write(val)

    def write(self, extperkey, extartid, amount):
        """ Write record in appropriate record format. """
        val = self.recordformatter.record(extperkey, extartid, amount)
        if not val is None:
            self.runfiles.write(val)


# IndexFile --------------------------------------------------------------{{{2
class IndexFile(xml.XMLElement):
    """
    Generate an HTML document with links to Overtime/Per Diem statement reports
    (in PDF format).
    """
    def __init__(self, runid, rd):
        """ Create head and start to build up HTML body element. """
        xml.XMLElement.__init__(self)
        self.tag = 'html'
        self['xmlns'] = "http://www.w3.org/1999/xhtml"
        self.head = xml.XMLElement('head')
        meta = xml.XMLElement('meta')
        meta['http-equiv'] = "Content-Type"
        meta['content'] = "text/html; charset=ISO-8859-1"
        self.head.append(meta)
        self.head.append(xml.XMLElement('title', "%s - %s (%s)" % (runid, rd.runtype, rd.extsys)))
        self.body = xml.XMLElement('body')
        self.body.append(xml.XMLElement('h1', "%s - %s (%s)" % (runid, rd.runtype, rd.extsys)))
        self.body.append(xml.XMLElement('dl', 
            xml.string('dt', 'Started at'),
            xml.dateTime('dd', rd.starttime),
            xml.string('dt', 'First date'),
            xml.date('dd', rd.firstdate),
            xml.string('dt', 'Last date'),
            xml.date('dd', rd.lastdate),
            xml.string('dt', 'Administrative Code'),
            xml.string('dd', "%s (%s)" % (rd.admcode,
                api.getAdminCodeDescription(rd.admcode))),
            xml.string('dt', 'Comment'),
            xml.string('dd', rd.note)))
        self.body.append(xml.XMLElement('h2', 'Statements:'))
        self.reports = xml.XMLElement('ul')
        self.body.append(self.reports)
        self.append(self.head)
        self.append(self.body)

    def add(self, report=None, homebase=None, rank=None, surname=None, filename=None):
        """ Add 'filename' to the list of reports. """
        if (surname is not None) and (surname == "S-Z"):
            surname = "S-&Aring;"
        L = []
        if not report is None:
            L.append(report)
        if not homebase is None:
            L.append(homebase)
        if not rank is None:
            L.append(rank)
        if not surname is None:
            L.append(surname)
        if L:
            link = ', '.join(L)
        else:
            link = filename
        self.reports.append(xml.XMLElement('li', 
            xml.XMLElement('a', link, href=filename)))

    def write(self, filename):
        """ Write the HTML document to 'filename'. """
        f = open(filename, "w")
        print >>f, str(self)
        f.close()


# functions =============================================================={{{1

# autorelease ------------------------------------------------------------{{{2
@api.checkPlanningPeriod
def autorelease(rundata):
    """Release the run with highest runid. Raises exception if:
    (1) No run was found.
    (2) An already released run was found.
    """
    log.debug('autorelease(%s)' % rundata)
    rundata = api.getUnreleasedRun(rundata)
    if rundata:
        return release(RunData.fromRunId(rundata))
    return ([], True)


# export -----------------------------------------------------------------{{{2
def export(rundata, is_release=False):
    """Export to file and return file name."""
    
    log.debug("export(%s)" % rundata)

    rundata.firstdate = TM.salary_run_id[(rundata.runid,)].firstdate
    rundata.lastdate = TM.salary_run_id[(rundata.runid,)].lastdate

    exp = SalaryRecord(RunFiles(rundata, is_release))
    exp.write_pre()
    for rec in api.getRecordsFor(rundata.runid):
        exp.write(rec.extperkey, rec.extartid, int(rec.amount))
    exp.write_post()
    exp.close()

    log.info("export() - filename is '%s'" % (exp.runfiles.name))
    return exp.runfiles.name


# job --------------------------------------------------------------------{{{2
@api.checkPlanningPeriod
def job(rundata, release_run=False, export_run=False):
    """Called from report server."""
    log.debug("job(%s)" % (rundata,))

    if rundata.runtype is None:
        raise api.SalaryException("job(): No runtype.")
    if rundata.extsys is None:
        raise api.SalaryException("job(): No extsys.")
    if rundata.admcode is None:
        rundata.admcode = "N"
    if rundata.note is None:
        rundata.note = "salary.run.job@%s" % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")

    runid = run(rundata)
    log.info("New run with runid '%d' created." % (runid,))
    if export_run:
        exportformat="CSV"
        if hasattr(rundata, "exportformat") and rundata.exportformat:
            exportformat = rundata.exportformat
        return export(RunData(runid=runid, runtype=rundata.runtype, exportformat=exportformat, extsys=rundata.extsys))
    # Save metadata, but neither export file nor any email created.
    # This step has been moved to 'release()' see CR 464.
    # Return list of reports and update-delta flag
    if release_run:
        # For some jobs e.g. AMBI we release the run immediately.
        return release(rundata)
    return ([], True)


# release ----------------------------------------------------------------{{{2
def release(rundata):
    """
    Perform release activities:
    (1) Release activities specific for the run type.
    (2) Create export file and move this to release directory.
    (3) Send email with status report.
    (4) Mark run as being released.
    """
    log.debug("release(%s)" % (rundata))
    try:
        # (1) Release activites specific for run type (might be a no-op)
        log.debug("... loading class '%s' from module '%s.%s'" % (rundata.extsys, conf.runTypePackage, rundata.runtype))
        module = __import__("%s.%s" % (conf.runTypePackage, rundata.runtype), (), (), rundata.extsys)
        c = getattr(module, rundata.extsys)
        c(rundata).release()
    except Exception, e:
        log.error("release(%s) failed [%s]." % (rundata, e))
        raise

    reports = []
    # [acosta:08/113@12:30] CR 88 - Chinese crew should not generate salary file.
    # SASCMS-504: Not sending mail for Chinese and Japanese crew
    if rundata.extsys not in ('CN', 'JP', 'HK'):
        # (2) Create export file and move to release directory
        filename = export(rundata, is_release=True)
        reports.append({
            'content-type': 'text/plain',
            'content-location': filename,    # A file name
            'destination': [("SALARY_EXPORT", {'subtype':rundata.runtype, 'rcpttype':rundata.extsys})],
        })
        log.info("Export file '%s' created." % (filename,))

        log.info("Mail created.")

    # (4) Finally, mark run as released.
    api.releaseRun(rundata)
    log.info('Run %d released.' % rundata.runid)
    
    # Return list of reports together with update-delta flag.
    return (reports, True)


# report -----------------------------------------------------------------{{{2
def report(rundata):
    """
    Create a summary report to be sent by email.
    """
    log.debug("report(%s)" % (rundata))
    try:
        log.debug("... loading class '%s' from module '%s.%s'" % ( rundata.extsys, conf.rptPackage, rundata.runtype))
        module = __import__("%s.%s" % (conf.rptPackage, rundata.runtype), (), (), rundata.extsys)
        c = getattr(module, rundata.extsys)
        return c(rundata).report()
    except Exception, e:
        traceback.print_exc()
        log.error("report(%s) failed [%s]." % (rundata, e))
        raise


# run --------------------------------------------------------------------{{{2
def run(rundata):
    """
    Run launcher, the work will be done in a file in the rec package.  If e.g.
    a PERDIEM job for 'DK' was submitted, then the method
    'salary.ec.type.ECPerDiem.DK(rundata).run()' will be called.
    Return integer (runid).
    """
    log.debug("run(%s)" % (rundata))
    try:
        # switch "salary mode" on
        old_salary_month_start_p = rave.param('parameters.%salary_month_start_p%').value()
        old_salary_month_end_p = rave.param('parameters.%salary_month_end_p%').value()
        rave.param('parameters.%salary_month_start_p%').setvalue(rundata.firstdate)
        rave.param('parameters.%salary_month_end_p%').setvalue(rundata.lastdate)
        rave.param('parameters.%is_salary_run%').setvalue(True)

        log.debug("... loading class '%s' from module '%s.%s'" % (rundata.extsys, conf.ecRunTypePackage, rundata.runtype))
        module = __import__("%s.%s" % (conf.ecRunTypePackage, rundata.runtype), (), (), rundata.extsys)
        c = getattr(module, rundata.extsys)
        return c(rundata).run()
    except Exception, e:
        traceback.print_exc()
        log.error("run(%s) failed [%s]." % (rundata, e))
        raise
    finally:
        # switch "salary mode" off
        rave.param('parameters.%salary_month_start_p%').setvalue(old_salary_month_start_p)
        rave.param('parameters.%salary_month_end_p%').setvalue(old_salary_month_end_p)
        rave.param('parameters.%is_salary_run%').setvalue(False)

def validity_check(runIdForReporting):
    return GenericRun(RunData(runid=runIdForReporting)).validity_check(runIdForReporting)

# Test functions ========================================================={{{1

# bit --------------------------------------------------------------------{{{2
def bit(*ids):
    """ Built-In Test. """
    import salary.test_salary
    salary_test_salary.test_run


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Start the MMI. """
    print autorelease(RunData(extsys="DK", runtype="PERDIEM", monthsBack=3))
    #import salary.mmi as mmi
    #mmi.Salary().form()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
