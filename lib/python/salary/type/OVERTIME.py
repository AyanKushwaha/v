"""
Interface 44.3 Overtime and Allowances
"""

import logging
import os
from tempfile import mkstemp

import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
from RelTime import RelTime

import salary.Overtime as Overtime
import salary.accounts as accounts
import salary.api as api
import salary.conf as conf
import salary.run as run
import utils.Names
from salary.Budgeted import BudgetedRunDataHandler
from salary.Overtime import OvertimeManager
from salary.reasoncodes import REASONCODES
from tm import TM
from utils.fmt import minutes

log = logging.getLogger('salary.type.OVERTIME')
username = utils.Names.username()


class OvertimeRun(run.GenericRun):
    def run(self, create_report=True):
        """Overriding Base class in order to be able to create
        a OvertimeStatement at the same time as the run."""
        runid = run.GenericRun.run(self)
        if create_report:
            if self.rundata.admcode == 'R':
                fd, retro_fn = mkstemp(dir=os.environ['CARMTMP'], suffix='.tmp')
                tmpfile = os.fdopen(fd, "w")
                for crewid in set([d.crewid for d in self.data]):
                    print >>tmpfile, crewid
                tmpfile.close()
            else:
                retro_fn = None
            ix = run.IndexFile(runid, self.rundata)

            args = {
                'firstdate': str(int(self.rundata.firstdate)),
                'lastdate': str(int(self.rundata.lastdate)),
                'starttime': str(int(self.rundata.starttime)),
                'extsys': self.rundata.extsys_for_rave(),
                'note': self.rundata.note or '',
                'admcode': self.rundata.admcode,
                'fromStudio': 'FALSE',
            }
            if not retro_fn is None:
                args['retrofile'] = retro_fn
            log.debug('Creating Overtime Statement report.')
            api.runReport('report_sources.include.OvertimeStatement', runid, args=args)
            ix.add(filename=api.reportBaseName(runid, '.pdf'))
            if self.rundata.extsys_for_rave() == 'DK' and not self.isCC4EXNG:
                # Give the Convertible OT report a name that is similar to the OT
                # statement, so that symbolic links will be created (in mmi.py).
                # The name of the Convertible OT report will be like:
                # '00003342ConvertibleOvertime.pdf'
                basename = api.reportBaseName(runid, ext='.pdf',
                        subtype=conf.convertible_overtime_subtype)
                conv_report_filename = conversionReport(self.rundata, basename)
                ix.add(filename=basename)
            if not retro_fn is None:
                os.unlink(retro_fn)
            ix.write(api.reportFileName(runid, ext='.html'))
        else:
            log.debug('Omitting Overtime Statement report creation.')
        return runid

    def rosters(self):
        # part of the "interface"
        whereExprs = ('salary.%%salary_system%%(%s) = "%s"' % (self.rundata.firstdate, self.rundata.extsys_for_rave()),
                      'not salary.%crew_excluded%')
        salary_iterator = rave.iter('iterators.roster_set', where=whereExprs)

        # Set parameter to limit search for records within start -> end
        old_salary_month_start = rave.param(conf.startparam).value()
        rave.param(conf.startparam).setvalue(self.rundata.firstdate)
        old_salary_month_end = rave.param(conf.endparam).value()
        rave.param(conf.endparam).setvalue(self.rundata.lastdate)
        try:
            rosters = OvertimeManager(conf.context, salary_iterator).getOvertimeRosters()
        finally:
            rave.param(conf.startparam).setvalue(old_salary_month_start)
            rave.param(conf.endparam).setvalue(old_salary_month_end)
        if len(rosters) == 0:
            raise api.SalaryException("No matching rosters found.")
        return rosters

    def CALM_OTFC(self, rec):
        """ Canlendar month / Flight crew OT for SKS"""
        if rec.isFlightCrew:
            if self.hours100(rec.getCalendarMonth()) + self.hours100(rec.getCalendarMonthPartTimeExtra()) > 0:
                return self.hours100(rec.getCalendarMonth())
            else:
                return self.hours100(rec.getOvertime())

    def OTPT(self, rec):
        return self.hours100(rec.getCalendarMonthPartTimeExtra())

    def CALW(self, rec):
        """ Calendar week (42 hrs) """
        return self.hours100(rec.getCalendarWeek())

    def DUTYP(self, rec):
        """ Duty pass SH, Duty pass LH, CO after free weekend"""
        if rec.isCC4EXNG:
            return 0
        return self.hours100((rec.getDutyPass() or RelTime(0)) + 
                             (rec.getLateCheckout() or RelTime(0)))
    
    def LRHIGH(self, rec):
        """ Loss of rest high. """
        return self.times100(rec.getLossRestHigh())

    def LRLOW(self, rec):
        """ Loss of rest low. """
        return self.times100(rec.getLossRestLow())

    def MDC(self, rec):
        """ Maitre de Cabin """
        return self.hours100(rec.getMDC())

    def MDCSH(self, rec):
        """ Maitre de Cabin, short haul """
        return self.hours100(rec.getMDCShortHaul())

    def MDCLH(self, rec):
        """ Maitre de Cabin, long haul """
        return self.hours100(rec.getMDCLongHaul())

    def OT(self, rec):
        if rec.isFlightCrew:
            return 0
        return self.hours100(rec.getOvertime())

    def OTFC(self, rec):
        if not rec.isFlightCrew:
            return 0
        return self.hours100(rec.getOvertime())
    
    def SCC(self, rec):
        if rec.isCC4EXNG:
            return self.hours100(rec.getSCCAll())
        return self.hours100(rec.getSCC())

    def SCCNOP(self, rec):
        if rec.isCC4EXNG:
            return 0
        return self.hours100(rec.getSCCNOP())

    def OTPTC(self, rec):
        if rec.getMertidParttimeCc() > RelTime(0):
            return self.hours100(rec.getMertidParttimeCc())
        elif rec.getMertidParttimeCcLong() > RelTime(0):
            return self.hours100(rec.getMertidParttimeCcLong())
        else:
            return 0

    def OT_CO_LATE_FC(self, rec):
        """This overtime is applied to all FD except CJ incl. SK.  Ref Jira SKCMS-691"""
        return rec.get_OT_FD_hours100_netto()

    def SNGL_SLIP_LONGHAUL(self, rec):
        if rec.isFlightCrew:
            return self.times100(rec.getSnglSlipLonghaul())
        else:
            return 0


class DK(OvertimeRun):
    def __init__(self, record):
        articles = ['LRHIGH', 'LRLOW', 'MDCLH', 'MDCSH', 'OT', 'SCC', 'SCCNOP', 'OTFC', 'OTPT', 'OTPTC',
                    "OT_FC_CJ", "OT_FP_CJ", "OT_CC_QA", "OT_CO_LATE_FC", 'SCCQA', "SNGL_SLIP_LONGHAUL"]
        extra_articles = []
        self.now, self.isCC4EXNG, = rave.eval('fundamental.%now%', 'system_db_parameters.%%agreement_valid%%("4exng_cc_ot", %s)' % record.firstdate)
        if not self.isCC4EXNG:
            extra_articles = ['X_CONVERTIBLE_OT']
        OvertimeRun.__init__(self, record, articles, extra_articles)

    def save_extra(self, rec, artid, value):
        self.extradata.append(rec.crewId, artid, value)

    def release(self):
        for record in api.getExtraRecordsFor(self.rundata.runid):
            if record.intartid == 'X_CONVERTIBLE_OT' and not self.isCC4EXNG:
                balance = self.get_balance(record.crewid.id) / 100
                f0days, remain = divmod(record.amount + balance, conf.convertible_time)
                self.add2account(record.crewid, f0days, 'F0')
                self.add2account(record.crewid, record.amount, 'F0_BUFFER')
                self.add2account(record.crewid, -conf.convertible_time * f0days, 'F0_BUFFER')

    def get_balance(self, crew):
        return accounts.balance(crew, 'F0_BUFFER', self.rundata.starttime)

    def LRHIGH(self, rec):
        return 0 if rec.apply_QA_CC_CJ else OvertimeRun.LRHIGH(self, rec)

    def LRLOW(self, rec):
        return 0 if rec.apply_QA_CC_CJ else OvertimeRun.LRLOW(self, rec)

    def MDCLH(self, rec):
        return 0 if rec.apply_QA_CC_CJ else OvertimeRun.MDCLH(self, rec)

    def MDCSH(self, rec):
        return 0 if rec.apply_QA_CC_CJ else OvertimeRun.MDCSH(self, rec)

    def OTPTC(self, rec):
        return 0 if rec.apply_QA_CC_CJ else OvertimeRun.OTPTC(self, rec)

    def OTFC(self, rec):
        return 0 if rec.apply_QA_CC_CJ else OvertimeRun.CALM_OTFC(self, rec)
                
    def OTPT(self, rec):
        return 0 if rec.apply_QA_CC_CJ else OvertimeRun.OTPT(self, rec)
    
    def OT(self, rec):
        if rec.apply_QA_CC_CJ:
            return 0
        if rec.isFlightCrew or rec.isConvertible:
            return 0
        else:
            return OvertimeRun.OT(self, rec)

    def OT_CO_LATE_FC(self, rec):
        """DK should have 30min == 100, 60 min == 200, etc- i.e. double of SE and NO """
        return OvertimeRun.OT_CO_LATE_FC(self, rec) * 2

    def SCC(self, rec):
        return 0 if rec.apply_QA_CC_CJ else OvertimeRun.SCC(self, rec)

    def SCCNOP(self, rec):
        return 0 if rec.apply_QA_CC_CJ else OvertimeRun.SCCNOP(self, rec)

    def SCCQA(self, rec):
        return self.times100(rec.getSCCQA())

    def X_CONVERTIBLE_OT(self, rec):
        if not rec.isConvertible:
            return 0
        return minutes(rec.getOvertime())


    def OT_FC_CJ(self, rec):
        """Overtime Cimber flight captain"""
        return self.times100(rec.get_sum_OT_QA()) if rec.apply_QA_CC_CJ and rec.isFC else 0

    def OT_FP_CJ(self, rec):
        """Overtime Cimber flight pilot"""
        return self.times100(rec.get_sum_OT_QA()) if rec.apply_QA_CC_CJ and rec.isFP else 0

    def OT_CC_QA(self, rec):
        """Overtime Cimber cabin crew"""
        return self.times100(rec.get_sum_OT_QA()) if rec.apply_QA_CC_CJ and not rec.isFlightCrew else 0

    def __str__(self):
        return 'Danish overtime'

    def add2account(self, crewref, amount, account):
        if int(amount) != 0:
            log.debug('add2account(%s, %s, %s)' % (
                crewref, amount, account))
            entrytime = self.now
            si = "Converted (%s)" % self.rundata.runid
            if account == 'F0':
                reasoncode = REASONCODES['IN_CONV']
            else:
                if amount < 0:
                    reasoncode = REASONCODES['OUT_CONV']
                else:
                    # Let the Convertible OT entry come before the conversion
                    entrytime = self.now - RelTime(1)
                    si = "Convertible OT (%s)" % self.rundata.runid
                    reasoncode = REASONCODES['IN_ADMIN']
            rec = TM.account_entry.create((TM.createUUID(),))
            rec.crew = crewref
            rec.tim = self.now
            rec.account = TM.account_set[(account,)]
            rec.source = "salary.type.OVERTIME"
            rec.amount = amount * 100
            rec.man = True
            rec.rate = (100, -100)[amount < 0]
            rec.published = True
            rec.reasoncode = reasoncode
            rec.entrytime = entrytime
            rec.username = username
            rec.si = si


class NO(OvertimeRun):
    def __init__(self, record):
        articles = ['LRHIGH', 'LRLOW', 'MDCLH', 'MDCSH', 'OT', 'SCC', 'SCCNOP', 'OTFC',
            'OTPT','OTPTC', 'OTRESCHED', "OT_CO_LATE_FC", "SNGL_SLIP_LONGHAUL"]
        self.now = rave.eval('fundamental.%now%')
        OvertimeRun.__init__(self, record, articles)
        
    def OTPTC(self, rec):
        return OvertimeRun.OTPTC(self, rec)

    def OTFC(self, rec):
        if rec.isFlightCrew:
            return self.CALM_OTFC(rec)
        
    def OTRESCHED(self, rec):
        if rec.isFlightCrew and rec.isSKN:
            return self.hours100(rec.getContributingPart(Overtime.OT_PART_LATE_CHECKOUT, False))
    
    def OTPT(self, rec):
        return OvertimeRun.OTPT(self, rec)

    def __str__(self):
        return 'Norwegian overtime'


class SE(OvertimeRun):
    def __init__(self, record):
        articles = ['CALM_OTFC', 'CALW', 'DUTYP', 'LRLOW', 'MDC', 'OTPT', 'SCC',
            "OT_CO_LATE_FC", "SNGL_SLIP_LONGHAUL"]
        OvertimeRun.__init__(self, record, articles)

    def CALM_OTFC(self, rec):
        if rec.isFlightCrew:
            return OvertimeRun.CALM_OTFC(self, rec)
        else: # SASCMS-3396
            return self.hours100(rec.getCalendarMonth())

    def CALW(self, rec):
        if rec.isCC4EXNG:
            return self.OT(rec)
        else:
            return OvertimeRun.CALW(self, rec)

    def OTPT(self, rec):
        if rec.isFlightCrew:
            return OvertimeRun.OTPT(self, rec)
        else:
            if rec.getMertidParttimeCc() > RelTime(0):
                return self.hours100(rec.getMertidParttimeCc())
            elif rec.getMertidParttimeCcLong() > RelTime(0):
                return self.hours100(rec.getMertidParttimeCcLong())
            else:
                return 0

    def __str__(self):
        return 'Swedish overtime'


class S3(OvertimeRun):
    def __init__(self, record):
        articles = ['CALM_OTFC', 'CALW', 'OT_CO_LATE_FC', 'SNGL_SLIP_LONGHAUL', 'DUTYP']
        OvertimeRun.__init__(self, record, articles)
        self.accumulated_rosters = []
        
    def CALM_OTFC(self, rec):
        if rec.isFlightCrew:
            return OvertimeRun.CALM_OTFC(self, rec)
        else: # SASCMS-3396
            return self.hours100(rec.getCalendarMonth())

    def CALW(self, rec):
        if rec.isCC4EXNG:
            return self.OT(rec)
        else:
            return OvertimeRun.CALW(self, rec)

    def OTPT(self, rec):
        if rec.isFlightCrew:
            return OvertimeRun.OTPT(self, rec)
        else:
            if rec.getMertidParttimeCc() > RelTime(0):
                return self.hours100(rec.getMertidParttimeCc())
            elif rec.getMertidParttimeCcLong() > RelTime(0):
                return self.hours100(rec.getMertidParttimeCcLong())
            else:
                return 0

    def _normal_test(self):
        self.get_codes()
        try:
            self.accumulated_rosters = self.rosters()
        except api.SalaryException as e:
            # "no rosters" is not considered an error here, as we are accumulating data from different runtypes
            if str(e) == "No matching rosters found.":
                pass
            else:
                raise
        self.save_run(self.accumulated_rosters)

    normal = _normal_test
    test = _normal_test


    def __str__(self):
        return 'Swedish overtime'


class S2(OvertimeRun):
    def __init__(self, record):
        #            number      number  number  number number  number
        articles = ['CALM_OTFC', 'CALW', 'DUTYP','MDC', 'OTPT', 'SCC']
        OvertimeRun.__init__(self, record, articles)
        
    def _normal_test(self):
        self.budgeted_run_data_handler = BudgetedRunDataHandler(self.rundata)
        OvertimeRun._normal_test(self)

    normal = _normal_test
    test = _normal_test

    def save_run(self, rosters):
        for crew in rosters:
            for a in self.articles:
                func = getattr(self, a)
                total = 0
                for (offset, value) in func(crew):
                    if value is not None and int(value) != 0:
                        self.save_extra(crew, a, value, offset)
                        total = total + value
                self.save(crew, a, total)

    def makeDayList(self, rec, value):
        last_scheduled_day = self.budgeted_run_data_handler.getLastScheduledDay(rec.crewId)
        offset = int(last_scheduled_day - self.rundata.firstdate) / (24 * 60)
        return [(offset, value)]

    def CALM_OTFC(self, rec):
        if rec.isFlightCrew:
            return self.makeDayList(rec, OvertimeRun.CALM_OTFC(self, rec))
        else: # SASCMS-3396
            return self.makeDayList(rec, self.hours100(rec.getCalendarMonth()))

    def CALW(self, rec):
        if rec.isCC4EXNG:
            return self.makeDayList(rec, self.OT(rec))
        else:
            return self.makeDayList(rec, OvertimeRun.CALW(self, rec))

    def DUTYP(self, rec):
        return self.makeDayList(rec, OvertimeRun.DUTYP(self, rec))
        
    def LRLOW(self, rec):
        return self.makeDayList(rec, OvertimeRun.LRLOW(self, rec))
        
    def MDC(self, rec):
        return self.makeDayList(rec, OvertimeRun.MDC(self, rec))
        
    def OTPT(self, rec):
        if rec.isFlightCrew:
            return self.makeDayList(rec, OvertimeRun.OTPT(self, rec))
        else:
            if rec.getMertidParttimeCc() > RelTime(0):
                return self.makeDayList(rec, self.hours100(rec.getMertidParttimeCc()))
            elif rec.getMertidParttimeCcLong() > RelTime(0):
                return self.makeDayList(rec, self.hours100(rec.getMertidParttimeCcLong()))
            else:
                return []

    def SCC(self, rec):
        return self.makeDayList(rec, OvertimeRun.SCC(self, rec))
        
    def __str__(self):
        return 'Swedish overtime'


class JP(DK):
    def __str__(self):
        return "Japanese overtime"


class CN(DK):
    def __str__(self):
        return "Chinese overtime"


class HK(DK):
    def __str__(self):
        return "Hong Kong overtime"


def conversionReport(rundata, basename):
    """
    Run a convertible crew report to be sent by mail, and stores it in 
      salary reports folder (CARMDATA).
    """
    # Where to store report files
    filename = os.path.join(api.reportDirectory(), basename)
    log.debug('Creating Convertible Crew report (%s).' % filename)
    return prt.generateReport('report_sources.hidden.ConvertibleCrew',
            filename, prt.PDF, 'runid=%s' % rundata.runid)


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
