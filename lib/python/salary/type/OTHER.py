"""
Other transactions
"""

# imports ================================================================{{{1
import salary.conf as conf
import carmensystems.rave.api as rave

from utils.rave import RaveIterator
from salary.api import SalaryException, warn
from salary.run import GenericRun
from salary.Overtime import OvertimeManager
from salary.reasoncodes import REASONCODES
from salary.compconv import FDCache
from tm import TM
from RelTime import RelTime
from AbsTime import AbsTime
from salary.Budgeted import BudgetedRunDataHandler

# Module variable, keeps cache used to find if crew is FC
# NOTE: We are making the assumption that a crew member does not change
# NOTE: his/her main function i.e. an FC crew will not become CC or vice versa.
isFlightCrew = None

# InstructorIterator ====================================================={{{1
class InstructorIterator(RaveIterator):
    def __init__(self, rd):
        iterator = RaveIterator.iter('iterators.roster_set', where=(
            'salary.%%salary_system%%(%s) = "%s"' % (rd.firstdate, rd.extsys_for_rave()),
            'salary.%inst_has_any_allowance%',
        ))
        fields = {
            'crewId': 'crew.%id%',
            'empNo': 'crew.%employee_number%',
            'lifus_act': 'salary.%inst_lifus_act%',
            'pc_opc': 'salary.%inst_pc_opc%',
            'pc_opc_bd': 'salary.%inst_pc_opc_bd%',
            'type_rating': 'salary.%inst_type_rating%',
            'type_rating_bd': 'salary.%inst_type_rating_bd%',
            'crm': 'salary.%inst_crm%',
            'lci_sh': 'salary.%inst_lci_sh%',
            'lci_lh': 'salary.%inst_lci_lh%',
            'classroom': 'salary.%inst_class%',
            'cc': 'salary.%inst_cc%',
            'skill_test': 'salary.%inst_skill_test%',
            'sim': 'salary.%inst_sim%',
            'sim_skill_bd': 'salary.%inst_sim_skill_brief_debrief%',
            'new_hire_follow_up_act': 'salary.%inst_new_hire_follow_up_act%',
            'etops_lifus_act': 'salary.%inst_etops_lifus_act%',
            'etops_lc_act': 'salary.%inst_etops_lc_act%',
        }
        RaveIterator.__init__(self, iterator, fields)


class CompDaysEntry:
    """ One object per extperkey, each object contains a number of counters,
    one for each account type. """


    def __init__(self, empno, post):
        """ Create an empty object, add information in 'post' argument to
        counters. """
        self.empNo = empno
        self.crewId = post.crew.id
        self.is_fc = isFlightCrew(self.crewId, post.tim)
        self.bought = 0
        self.bought_8 = 0
        self.bought_forced = 0
        self.f7s = 0
        self.f0_f3 = 0
        self.f31_f33 = 0
        self.f32 = 0
        self.f35 = 0
        self.f38 = 0
        self.sold = 0
        self.updateCounters(post)

    def updateCounters(self, p):
        """ Update counters. """
        account = p.account.id
        amount = p.amount
        amount = -amount
        if account == 'F7S':
            self.f7s += amount
        elif account in ('F31', 'F33'):
            self.f31_f33 += amount
        elif account in ('F32'):
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

        self.empnoMap = {}
        # [acosta:09/287@17:53] Changed the conditions to include records based
        # on some thoughts I had in connection to a couple of issues reported
        # from the customer.  Reset job will always create an entry that is on
        # the first of next month at 0:00, so it's better to let that "summary
        # record" be included in this month's salary run. Letting the "summary
        # record" (OUT Payment) stay on the 1st of the next month assures that
        # it will always be "on top" in all listings.
        ### posts = TM.account_entry.search("(&(tim>=%s)(tim<%s)(|(reasoncode=%s)(reasoncode=%s)))" % (
        posts = TM.account_entry.search("(&(tim>%s)(tim<=%s)(|(reasoncode=%s)(reasoncode=%s)))" % (
                rd.firstdate,
                rd.lastdate,
                REASONCODES['PAY'],
                REASONCODES['PAY_CORR'],
        ))
        for p in posts:
            ### Since entry is the 1st in next month, we need to adjust it, to the prev month, before looking for crewinfo.
            ### Otherwise, if crew retires this month, we will get an error, because extperkey cannot be found. SASCMS-1245
            (crew_extsys, empno) = self._crewinfo(p.crew.id, p.tim - RelTime(1440))
            if empno is None:
                continue
            if crew_extsys == rd.extsys_for_rave():
                if empno in self.empnoMap:
                    self.empnoMap[empno].updateCounters(p)
                else:
                    self.empnoMap[empno] = CompDaysEntry(empno, p)

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
        for x in TM.salary_region.search("(&(region=%s)(validfrom<=%s)(validto>%s))" % (base, date, date)):
            extsys = x.extsys
            break
        if extsys is None:
            raise SalaryException("No salary system found for crew with ID = '%s' and base = '%s'." % (crewid, base))
        return (extsys, empno)

    def __len__(self):
        return len(self.empnoMap)


# OtherTranscationsRun ==================================================={{{1
class OtherTransactionsRun(GenericRun):
    def __init__(self, rundata, articles=[]):
        instructor_article_types = { 'INST_LCI'        : 'number',
                                     'INST_LCI_LH'     : 'number',
                                     'INST_LIFUS_ACT'  : 'number',
                                     'INST_CLASS'      : 'number',
                                     'INST_CRM'        : 'number',
                                     'INST_CC'         : 'number',
                                     'INST_SKILL_TEST' : 'number',
                                     'INST_SIM'        : 'number',
                                     'INST_SIM_SKILL_BR'     : 'number',
                                     'INST_NEW_HIRE'   : 'number' }
        self.instructor_articles = instructor_article_types.keys()

        temp_crew_article_types = { 'TEMPCREW' : 'number' }
        self.isCC4EXNG, = rave.eval('system_db_parameters.%%agreement_valid%%("4exng_cc_ot", %s)' % rundata.firstdate)
        if not self.isCC4EXNG:
            temp_crew_article_types['TEMPCREWOT'] = 'number'
        self.temp_crew_articles = temp_crew_article_types.keys()

        comp_days_article_types = { 'BOUGHT'   : 'number',
                                    'F0_F3'    : 'number',
                                    'F31_F33'  : 'number',
                                    'F7S'      : 'number',
                                    'BOUGHT_8' : 'number',
                                    'BOUGHT_FORCED' : 'number' }
        self.comp_days_articles = comp_days_article_types.keys()

        article_types = instructor_article_types.copy()
        article_types.update(temp_crew_article_types)
        article_types.update(comp_days_article_types)
        articles = article_types.keys()

        GenericRun.__init__(self, rundata, articles, article_types = article_types)

    def _normal_test(self):
        self.budgeted_run_data_handler = BudgetedRunDataHandler(self.rundata)
        GenericRun._normal_test(self)

    normal = _normal_test
    test = _normal_test

    def instructor_rosters(self):
        old_salary_month_start = rave.param(conf.startparam).value()
        old_salary_month_end = rave.param(conf.endparam).value()
        rave.param(conf.startparam).setvalue(self.rundata.firstdate)
        rave.param(conf.endparam).setvalue(self.rundata.lastdate)
        try:
            iterator = InstructorIterator(self.rundata)
            rosters = iterator.eval(conf.context)
        finally:
            rave.param(conf.startparam).setvalue(old_salary_month_start)
            rave.param(conf.endparam).setvalue(old_salary_month_end)
        return rosters

    def temp_crew_rosters(self):
        # part of the "interface"
        salary_iterator_where = 'not salary.%%crew_excluded%% and salary.%%salary_system%%(%s) = "%s"' % (
            self.rundata.firstdate,
            self.rundata.extsys_for_rave())
        salary_iterator = rave.iter(
                'iterators.roster_set',
                where=salary_iterator_where)

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
        return rosters

    def comp_days_rosters(self):
        """ part of the 'interface' """
        iterator = CompDaysIterator(self.rundata)
        return iterator

    def rosters(self):
        rosterslist = []
        for (articles, func) in [(self.instructor_articles, self.instructor_rosters),
                                 (self.temp_crew_articles, self.temp_crew_rosters),
                                 (self.comp_days_articles, self.comp_days_rosters)]:
            roster = func()
            if len(roster) > 0:
                rosterslist.append((articles, roster))

        if len(rosterslist) == 0:
            raise SalaryException("No matching rosters found.")
        return rosterslist

    def save_run(self, rosterslist):
        for (articles, roster) in rosterslist:
            for crew in roster:
                for intartid in articles:
                    func = getattr(self, intartid)
                    total = 0
                    for (offset, value) in func(crew):
                        if value is not None and int(value) != 0:
                            self.save_extra(crew, intartid, value, offset)
                            total = total + value
                    self.save(crew, intartid, total)

    def makeDayList(self, rec, value):
        last_scheduled_day = self.budgeted_run_data_handler.getLastScheduledDay(rec.crewId)
        offset = int(last_scheduled_day - self.rundata.firstdate) / (24 * 60)
        return [(offset, value)]

    def INST_LCI(self, rec):
        """Instructor's allowance (SH)."""
        return self.makeDayList(rec, self.times100(rec.lci_sh))

    def INST_LCI_LH(self, rec):
        """Instructor's allowance (LH)."""
        return self.makeDayList(rec, self.times100(rec.lci_lh))

    def INST_LIFUS_ACT(self, rec):
        #return self.times100(rec.lifus_act)
        return self.makeDayList(rec, self.hours100(rec.lifus_act))

    def INST_ETOPS_LIFUS_ACT(self, rec):
        #return self.times100(rec.lifus_act)
        return self.makeDayList(rec, self.hours100(rec.etops_lifus_act))
    def INST_ETOPS_LC_ACT(self, rec):
        #return self.times100(rec.lifus_act)
        return self.makeDayList(rec, self.hours100(rec.etops_lc_act))

    def INST_CRM(self, rec):
        return self.makeDayList(rec, self.hours100(rec.crm))

    def INST_CLASS(self, rec):
        return self.makeDayList(rec, self.hours100(rec.classroom))

    def INST_CC(self, rec):
        return self.makeDayList(rec, self.hours100(rec.cc))

    def INST_SKILL_TEST(self, rec):
        return self.makeDayList(rec, self.hours100(rec.skill_test))

    def INST_SIM(self, rec):
        return self.makeDayList(rec, self.hours100(rec.sim))

    def INST_SIM_SKILL_BR(self, rec):
        return self.makeDayList(rec, self.hours100(rec.sim_skill_bd))

    def INST_NEW_HIRE(self,rec):
        return self.makeDayList(rec, self.hours100(rec.new_hire_follow_up_act))


    def TEMPCREW(self, rec):
        return enumerate([ self.hours100(x) for x in rec.getTempCrewHoursDaily() ])

    def TEMPCREWOT(self, rec):
        if rec.isTemporary:
            return self.makeDayList(rec, self.hours100(rec.getOvertime()))
        return []

    def BOUGHT(self, rec):
        return self.makeDayList(rec, rec.bought)

    def BOUGHT_8(self, rec):
        return self.makeDayList(rec, rec.bought_8)

    def BOUGHT_FORCED(self, rec):
        return self.makeDayList(rec, rec.bought_forced)

    def F0_F3(self, rec):
        return self.makeDayList(rec, rec.f0_f3)

    def F31_F33(self, rec):
        return self.makeDayList(rec, rec.f31_f33)

    def F7S(self, rec):
        return self.makeDayList(rec, rec.f7s)

# S2 ====================================================================={{{1
class S2(OtherTransactionsRun):
    """ For Swedish crew. """
    def __str__(self):
        return "Other transactions for Swedish Crew."
