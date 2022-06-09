# changelog {{{2
# [acosta:07/134@09:22] First version
# }}}

"""
Interface 44.5 Bought Days and Compensation Days
"""

import carmensystems.rave.api as rave
import salary.conf as conf
import salary.run as run

from utils.fmt import NVL
from tm import TM
from salary.reasoncodes import REASONCODES
from salary.compconv import FDCache, QACCCache
from salary.api import SalaryException, warn
from RelTime import RelTime


# Module variable, keeps cache used to find if crew is FC
# NOTE: We are making the assumption that a crew member does not change
# NOTE: his/her main function i.e. an FC crew will not become CC or vice versa.
isFlightCrew = None
isCimberCabinCrew = None


class CompDaysEntry:
    """ One object per extperkey, each object contains a number of counters,
    one for each account type. """

    def __init__(self, empno, post):
        """ Create an empty object, add information in 'post' argument to
        counters. """
        self.empno = empno
        self.crewid = post.crew.id
        self.is_fd = isFlightCrew(self.crewid, post.tim)
        self.is_qa_cc = isCimberCabinCrew(self.crewid, post.tim)
        self.bought = 0
        self.bought_bl = 0
        self.bought_comp = 0
        self.bought_8 = 0
        self.bought_forced = 0
        self.f7s = 0
        self.f0_f3 = 0
        self.f31_f33 = 0
        self.f32 = 0
        self.f35 = 0
        self.f38 = 0
        self.sold = 0

    def updateCounters(self, p):
        """ Update counters. """
        account = p.account.id
        amount = p.amount
        amount = -amount
        if account == 'F7S':
            self.f7s += amount
        elif account in ('F31', 'F33'):
            self.f31_f33 += amount
        elif account == 'F32':
            self.f32 += amount
        elif account == 'F35':
            self.f35 += amount
        elif account == 'F0' or account.startswith('F3'):
            # F0 and F3* except F31, F33, and, F35
            self.f0_f3 += amount
        elif account == 'F38':
            self.f38 += amount
        elif account == 'BOUGHT':
            self.bought += amount
        elif account == 'BOUGHT_BL':
            self.bought_bl += amount
        elif account == 'BOUGHT_COMP':
            self.bought_comp += amount
        elif account == 'BOUGHT_8':
            self.bought_8 += amount
        elif account == 'BOUGHT_FORCED':
            self.bought_forced += amount
        elif account == 'SOLD':
            self.sold += amount
        else:
            pass


class CompDaysIterator:
    """ Get Compensation Days Info """
    def __init__(self, rd):
        # init the Cache used by CompDaysEntry
        global isFlightCrew
        if isFlightCrew is None:
            isFlightCrew = FDCache(None, rd.lastdate)
        global isCimberCabinCrew
        if isCimberCabinCrew is None:
            isCimberCabinCrew = QACCCache(None, rd.lastdate)
        self.empnoMap = {}
        # [acosta:09/287@17:53] Changed the conditions to include records based
        # on some thoughts I had in connection to a couple of issues reported
        # from the customer.  Reset job will always create an entry that is on
        # the first of next month at 0:00, so it's better to let that "summary
        # record" be included in this month's salary run. Letting the "summary
        # record" (OUT Payment) stay on the 1st of the next month assures that
        # it will always be "on top" in all listings.
        ### posts = TM.account_entry.search("(&(tim>=%s)(tim<%s)(|(reasoncode=%s)(reasoncode=%s)))" % (
        if rd.extsys == 'S3':   # this means we are running a compdays subrun from a daily allowances run
            self.search_str = "(|(&(tim>%s)(tim<=%s)(!(account=BOUGHT))(!(account=BOUGHT_8))(!(account=BOUGHT_FORCED))(!(account=BOUGHT_BL))(!(account=SOLD))(|(reasoncode=%s)(reasoncode=%s)))(&(tim>=%s)(tim<%s)(|(account=BOUGHT)(account=BOUGHT_8)(account=BOUGHT_FORCED)(account=BOUGHT_BL)(account=SOLD))(|(reasoncode=%s)(reasoncode=%s))))" % (
                rd.firstdate,
                rd.lastdate,
                REASONCODES['PAY'],
                REASONCODES['PAY_CORR'],
                rd.firstdate,
                rd.lastdate,
                REASONCODES['BOUGHT'],
                REASONCODES['SOLD']
            )
            posts = TM.account_entry.search(self.search_str)
            for p in posts:
                if p.account.id in ('BOUGHT', 'BOUGHT_8', 'BOUGHT_FORCED', 'BOUGHT_BL', 'SOLD'):
                    # no time shift for S3 BOUGHT, BOUGHT_8, BOUGHT_FORCED, BOUGHT_BL and SOLD entries,
                    # as they are always inside the month
                    (extsys, empno) = self._crewinfo(p.crew.id, p.tim)
                else:
                    # shifting the entry one day back, as it has been reported on
                    # the first of the next month
                    (extsys, empno) = self._crewinfo(p.crew.id, p.tim - RelTime(1440))
                if empno and extsys == rd.extsys_for_rave():
                    self.empnoMap.setdefault(empno, CompDaysEntry(empno, p)).updateCounters(p)
        else:
            self.search_str = "(|(&(!(account=SOLD))(tim>%s)(tim<=%s)(|(reasoncode=%s)(reasoncode=%s)))(&(account=SOLD)(tim=%s)(reasoncode=%s)))" % (
                rd.firstdate,
                rd.lastdate,
                REASONCODES['PAY'],
                REASONCODES['PAY_CORR'],
                rd.lastdate,
                REASONCODES['PAY'],
            )
            posts = TM.account_entry.search(self.search_str)
            for p in posts:
                ### Since entry is the 1st in next month, we need to adjust it, to the prev month, before looking for crewinfo.
                ### Otherwise, if crew retires this month, we will get an error, because extperkey cannot be found. SASCMS-1245
                (extsys, empno) = self._crewinfo(p.crew.id, p.tim - RelTime(1440))
                if empno and extsys == rd.extsys_for_rave():
                    self.empnoMap.setdefault(empno, CompDaysEntry(empno, p)).updateCounters(p)

    def __iter__(self):
        """ Return list of objects. """
        return iter(self.empnoMap.values())

    def _crewinfo(self, crewid, date):
        """ Convert from crewid to extperkey. """
        empno = None
        base = None
        for x in TM.crew[(crewid,)].referers('crew_employment', 'crew'):
            if x.validfrom <= date and date < x.validto:
                empno = x.extperkey
                base = x.base.id
                break
        if empno is None:
            #raise SalaryException("No extperkey found for crew with ID = '%s'." % (crewid))
            # Just ignore retired crew (WP int 94)
            warn("No extperkey found for crew with ID = '%s'." % (crewid))
            return (None, None)
        if base is None:
            raise SalaryException("No base found for crew with ID = '%s'." % (crewid))
        extsys = None
        salary_region_search = "(&(region='%s')(validfrom<=%s)(validto>%s))" % (base, date, date)
        for x in TM.salary_region.search(salary_region_search):
            extsys = x.extsys
            break
        if extsys is None:
            raise SalaryException("No salary system found for crew with ID = '%s' and base = '%s'." % (crewid, base))
        return (extsys, empno)

    def __len__(self):
        return len(self.empnoMap)


class CompDaysRun(run.GenericRun):
    """ Create a salary run for Comp Days and Balances. """

    def rosters(self):
        """ part of the 'interface' """
        iterator = CompDaysIterator(self.rundata)
        if len(iterator) == 0:
            import os
            schema = os.environ.get("SCHEMA", "### NO SCHEMA FOUND")
            raise SalaryException(str(
                "No comp-days found for query run."
                " Hint: Has salary been run for period...?"
                "  - search_str: %s" % iterator.search_str)
                + str(" Schema is: %s" % schema)
            )
        return iterator

    def save(self, rec, type, value):
        """ part of the 'interface' """
        self.data.append(rec.crewid, rec.empno, self.articleCodes[type], value)

    # Note: all values are already multiplied with 100 (from Rave)

    def BOUGHT(self, rec):
        return rec.bought

    def BOUGHT_BL(self, rec):
        return rec.bought_bl

    def BOUGHT_COMP(self, rec):
        return rec.bought_comp

    def BOUGHT_FORCED(self, rec):
        return rec.bought_forced

    def BOUGHT_8(self, rec):
        return rec.bought_8

    def BOUGHT_8_CC(self, rec):
        if rec.is_fd:
            return 0
        return rec.bought_8

    def BOUGHT_8_FC(self, rec):
        if rec.is_fd:
            return rec.bought_8
        return 0

    def F0_F3(self, rec):
        return rec.f0_f3

    def F31_F33(self, rec):
        return rec.f31_f33

    def F7S(self, rec):
        return rec.f7s

    def BOUGHT_CC(self, rec):
        if rec.is_fd:
            return 0
        return self.BOUGHT(rec)

    def BOUGHT_BL_CC(self, rec):
        if rec.is_fd:
            return 0
        return self.BOUGHT_BL(rec)

    def F0_F3_CC(self, rec):
        if rec.is_fd:
            return 0
        return self.F0_F3(rec)

    def F31_F33_CC(self, rec):
        if rec.is_fd:
            return 0
        return self.F31_F33(rec)

    def F35_CC(self, rec):
        # Only for CC
        if rec.is_fd:
            return 0
        return rec.f35

    def F7S_CC(self, rec):
        if rec.is_fd:
            return 0
        return self.F7S(rec)

    def SOLD(self, rec):
        return -rec.sold

    def SOLD_CC(self, rec):
        # Only for CC (DK)
        # [acosta:09/349@11:12] See SASCMS-1201, account 691 should be reported
        # with sign inverted.
        if rec.is_fd:
            return 0
        return self.SOLD(rec)

    def SOLD_FC(self, rec):
        if rec.is_fd:
            return self.SOLD(rec)
        return 0

    def BOUGHT_FC(self, rec):
        if rec.is_fd:
            return self.BOUGHT(rec)
        return 0

    def BOUGHT_BL_FC(self, rec):
        if rec.is_fd:
            return self.BOUGHT_BL(rec)
        return 0

    def F0_F3_FC(self, rec):
        if rec.is_fd:
            return self.F0_F3(rec)
        return 0

    def F31_F33_FC(self, rec):
        if rec.is_fd:
            return self.F31_F33(rec)
        return 0

    def F7S_FC(self, rec):
        if rec.is_fd:
            return self.F7S(rec)
        return 0


class DK(CompDaysRun):
    def __init__(self, rundata):
        # Set parameter to limit search for records within start -> end
        old_salary_month_start = rave.param(conf.startparam).value()
        rave.param(conf.startparam).setvalue(rundata.firstdate)
        old_salary_month_end = rave.param(conf.endparam).value()
        rave.param(conf.endparam).setvalue(rundata.lastdate)
        try:
            self.rostervals = {}
            rosters, = rave.eval(
                "sp_crew",
                rave.foreach(
                    "iterators.roster_set",
                    "crew.%id%",
                    "salary.%is_SKD%",
                    "salary_overtime.%is_QA_FD_or_CJ%",
                    "report_overtime.%is_FC%",
                    "report_overtime.%sum_bought_comp_days_qa_fd_netto%",
                ))
            for roster in rosters:
                ix, crew_id, is_dk, is_qa_fd_or_cj, is_fc, netto = roster
                if is_dk:
                    self.rostervals[crew_id] = dict(is_qa_fd_or_cj=is_qa_fd_or_cj, is_fc=is_fc, netto=netto)
        finally:
            rave.param(conf.startparam).setvalue(old_salary_month_start)
            rave.param(conf.endparam).setvalue(old_salary_month_end)

        articles = [
            'BOUGHT_FC',
            'BOUGHT_BL',
            'F0_F3_FC',
            'F31_F33_FC',
            'F7S_FC',
            'BOUGHT_CC',
            'BOUGHT_CC_QA',
            'F0_F3_CC',
            'F31_F33_CC',
            'F35_CC',
            'F7S_CC',
            'SOLD_CC',
            'SOLD_CC_QA',
            'SOLD_FC',
            'BOUGHT_COMP',
            'BOUGHT_8_CC',
            'BOUGHT_8_FC',
            "BOUGHT_QA_FC_COMP",
            "BOUGHT_QA_FP_COMP",
            'BOUGHT_FORCED',
        ]
        CompDaysRun.__init__(self, rundata, articles)

    def BOUGHT_CC(self, rec):
        return 0 if rec.is_qa_cc else CompDaysRun.BOUGHT_CC(self, rec)

    def BOUGHT_CC_QA(self, rec):
        return CompDaysRun.BOUGHT_CC(self, rec) if rec.is_qa_cc else 0

    def SOLD_CC(self, rec):
        return 0 if rec.is_qa_cc else CompDaysRun.SOLD_CC(self, rec)

    def SOLD_CC_QA(self, rec):
        return CompDaysRun.SOLD_CC(self, rec) if rec.is_qa_cc else 0

    def SOLD_FC(self, rec):
        return CompDaysRun.SOLD_FC(self, rec)

    def BOUGHT_FC(self, rec):
        return self.bought_fc_delegate(rec, False)

    def BOUGHT_8_FC(self, rec):
        return self.bought_fc_delegate(rec, True)

    def bought_fc_delegate(self, rec, is_8):
        d = self.rostervals.get(rec.crewid)
        if not d or d.get("is_qa_fd_or_cj"):
            return 0
        elif is_8:
            return CompDaysRun.BOUGHT_8_FC(self, rec)
        else:
            return CompDaysRun.BOUGHT_FC(self, rec)

    def BOUGHT_QA_FC_COMP(self, rec):
        return self.bought_qa_fd_comp_netto(rec.crewid, True)

    def BOUGHT_QA_FP_COMP(self, rec):
        return self.bought_qa_fd_comp_netto(rec.crewid, False)

    def bought_qa_fd_comp_netto(self, crew_id, should_be_fc):
        d = self.rostervals.get(crew_id)
        if not d:
            return 0
        is_qa_fd_or_cj = d.get("is_qa_fd_or_cj")
        is_fc = d.get("is_fc")
        netto = d.get("netto")
        return netto * 100 if is_qa_fd_or_cj and is_fc == should_be_fc else 0

    def __str__(self):
        return 'Compensation Days (DK)'


class NO(CompDaysRun):
    def __init__(self, record):
        articles = [
            'BOUGHT_FC',
            'BOUGHT_BL',
            'F0_F3_FC',
            'F31_F33',
            'F7S_FC',
            'BOUGHT_CC',
            'F0_F3_CC',
            'F7S_CC',
            'BOUGHT_COMP',
            'BOUGHT_8_CC',
            'BOUGHT_8_FC',
            'BOUGHT_FORCED'
        ]
        CompDaysRun.__init__(self, record, articles)

    def __str__(self):
        return 'Compensation Days (NO)'


class SE(CompDaysRun):
    def __init__(self, record):
        articles = [
            'BOUGHT',
            'BOUGHT_BL',
            'F0_F3',
            'F31_F33',
            'F7S',
            'BOUGHT_COMP',
            'BOUGHT_8',
            'BOUGHT_FORCED',
            'SOLD'
        ]
        CompDaysRun.__init__(self, record, articles)

    def __str__(self):
        return 'Compensation Days (SE)'


class S3(CompDaysRun):
    def __init__(self, record):
        articles = [
            'BOUGHT',
            'BOUGHT_BL',
            'F0_F3',
            'F31_F33',
            'F7S',
            'BOUGHT_8',
            'BOUGHT_FORCED',
            'SOLD'
        ]
        CompDaysRun.__init__(self, record, articles)
        
        # self.accumulated_rosters will likely become an iterator later.
        # We use a list instead of None here, as we try to iterate over it
        # in ALLOWNCE_D.py without checking if there is anything inside.
        self.accumulated_rosters = []

    def _normal_test(self):
        self.get_codes()
        try:
            self.accumulated_rosters = self.rosters()
        except SalaryException as e:
            # "no rosters" is not considered an error here, as we are accumulating data from different runtypes
            if str(e)[:len("No comp-days found for query run.")] == "No comp-days found for query run.":
                pass
            else:
                raise
        self.save_run(self.accumulated_rosters)

    normal = _normal_test
    test = _normal_test

    def __str__(self):
        return 'Compensation Days (SE)'


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
