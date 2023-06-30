
import os
import time
import Cui
import carmensystems.rave.api as rave
import logging
from datetime import datetime
from datetime import timedelta
from AbsTime import AbsTime
from salary.ec.ECPerDiem import PerDiemRosterManager
from salary.ec.ECSupervis import SupervisRosterManager
from salary.ec.ECOvertime import OvertimeRosterManager
from utils.fmt import NVL
from tm import TM
from shutil import copyfile

salary_systems = {
    'NO': 'NO',
    'SE': 'SE',
    'DK': 'DK',
    'CN': 'CN',
    'HK': 'HK',
    'JP': 'JP'
}

salary_perdim_article = {
    'SE': ['MEAL', 'PERDIEM_SALDO', 'PERDIEM_TAX_DAY', 'PERDIEM_TAX_DOMESTIC', 'PERDIEM_TAX_INTER'],
    'NO': ['MEAL_C', 'MEAL_F', 'PERDIEM_SALDO', 'PERDIEM_TAX_DAY', 'PERDIEM_TAX_DOMESTIC', 'PUBL_HOLIDAY_COMP'],
    'DK': ['MEAL_C', 'MEAL_F', 'PERDIEM_SALDO', 'PERDIEM_TAX', 'PERDIEM_NO_TAX'],
    'CN': ['PERDIEM_SALDO'],
    'HK': ['PERDIEM_SALDO'], 
    'JP': ['PERDIEM_SALDO']
}
salary_supervis_article = {
    'DK': ['INST_LCI_LH', 'INST_LCI', 'INST_CLASS', 'INST_SKILL_TEST', 'INST_SIM', 'INST_SIM_SKILL_BR', 'INST_LIFUS_ACT', 'INST_NEW_HIRE', 'INST_CC', 'INST_ETOPS_LIFUS_ACT', 'INST_ETOPS_LC_ACT', 'INST_CC_LCS_LINK'],
    'NO': ['SIM_INSTR_FIXED', 'INST_NEW_HIRE', 'INST_SIM_SKILL_BR', 'INST_LIFUS_ACT', 'INST_CLASS', 'INST_SIM', 'INST_SKILL_TEST', 'INST_CC', 'INST_LCI', 'INST_LCI_LH', 'INST_ETOPS_LIFUS_ACT', 'INST_ETOPS_LC_ACT', 'INST_CC_LCS_LINK'],
    'SE': ['INST_CLASS', 'INST_LCI', 'INST_CC', 'INST_LCI_LH', 'INST_LIFUS_ACT', 'INST_NEW_HIRE', 'INST_SIM', 'INST_SIM_SKILL_BR', 'INST_SKILL_TEST', 'SIM_INSTR_FIXED', 'INST_ETOPS_LIFUS_ACT', 'INST_ETOPS_LC_ACT'],
    'CN': [],
    'HK': [],
    'JP': []
}
salary_overtime_article = {
    'DK': ['SCC', 'SCCSVS', 'SNGL_SLIP_LONGHAUL','ABS_PR_LOA_D'],
    'NO': ['SCC', 'SCCSVS', 'MDCSH', 'SCCNOP', 'MDCLH', 'SNGL_SLIP_LONGHAUL','ABS_PR_LOA_D'],
    'SE': ['SNGL_SLIP_LONGHAUL', 'SCC','ABS_PR_LOA_D'],
    'HK': [], 
    'CN': [],
    'JP': []
}


CARMDATA = os.getenv("CARMDATA")
REPORT_PATH = '/samba-share/reports/SALARY_EC/'
#RELEASE_PATH = '/opt/Carmen/CARMDATA/carmdata/SALARY_NL/salary_month/Original_Salary_Files'
RELEASE_PATH = '/samba-share/reports/SALARY_EC/HR/'
# Start of salary month parameter
startparam = 'salary.%salary_month_start_p%'

# End of salary month parameter
endparam = 'salary.%salary_month_end_p%'

# Which context should be used
rave_context = 'sp_crew'

# Rave iterator
rave_iterator = 'iterators.roster_set'


logging.basicConfig()
log = logging.getLogger('ECSalaryReport')


class ECReport():
    def __init__(self, salary_system='all', report_start_date=None, report_end_date=None, release=True, test=False, studio=False):
        self.salary_system = salary_system
        self.release = release # Is it required or deprecated
        self.test = test
        if report_start_date:
            # Expected format is like "10Nov20"
            self.start = datetime.strptime(report_start_date,"%d%b%Y") if type(report_start_date) is str else report_start_date
        else:
            last_month_date = datetime.now().replace(day=1) - timedelta(days=(datetime.now().day +1))
            self.start = datetime(year=last_month_date.year, month=last_month_date.month , day=1)
        if report_end_date:
            # Expected format is like "01Dec20"
            self.end = datetime.strptime(report_end_date,"%d%b%Y")
        else:
            self.end = datetime(year=datetime.now().year, month=datetime.now().month, day=1)
        self.firstdate = AbsTime('01' + self.start.strftime('%b') + self.start.strftime('%Y'))
        self.lastdate = AbsTime('01' + self.end.strftime('%b') + self.end.strftime('%Y'))
        self.report_path = REPORT_PATH
        self.salary_article_tm =  get_article_table(pstart=self.firstdate, pend=self.lastdate)
        self.studio = studio

        if self.test:
            log.setLevel(logging.DEBUG)
        log.debug("ECReport config with firstdate: {0}  and lastdate: {1}".format(self.firstdate, self.lastdate))


    def generate(self, crew_ids=[]):
        # call PerDiemRun,PerDiemTaxRun,...
        start_t = time.time()
        entries = { 'NO': [], 'SE': [], 'DK': [], 'CN': [], 'HK': [], 'JP': [] }
        runs = []
        runs.append(PerDiemRun(salary_system=self.salary_system, crew_ids=crew_ids, salary_article_tm=self.salary_article_tm, \
            report_start_date=self.start,report_first_absdate=self.firstdate,report_end_date=self.end, report_last_absdate=self.lastdate, release=self.release, test=self.test).run())
        runs.append(SupervisRun(salary_system=self.salary_system, crew_ids=crew_ids, salary_article_tm=self.salary_article_tm, \
            report_start_date=self.start,report_first_absdate=self.firstdate,report_end_date=self.end, report_last_absdate=self.lastdate, release=self.release, test=self.test).run())
        runs.append(OvertimeRun(salary_system=self.salary_system, crew_ids=crew_ids, salary_article_tm=self.salary_article_tm, \
            report_start_date=self.start,report_first_absdate=self.firstdate,report_end_date=self.end, report_last_absdate=self.lastdate, release=self.release, test=self.test).run())
        for co in entries.keys():
            for run in runs:
                if len(run[co]) > 0:
                    entries[co].extend(run[co])
        if not os.path.exists(REPORT_PATH):
            os.makedirs(REPORT_PATH)
        if self.release and not os.path.exists(RELEASE_PATH):
            os.makedirs(RELEASE_PATH)
        for co in entries.keys():
            log.debug("SalaryECReport generated for {0} => {1} entries".format(co, len(entries[co])))
        csv_files = createCSV(entries, self.release, self.studio)
        exec_time = round(time.time() - start_t, 2)
        log.info("SalaryECReport generating took: {0}".format(exec_time))
        return [ REPORT_PATH + csv for csv in csv_files ]

class ECGenericRun():
    """
    This is a base class for the run type classes in the 'salary.type' package.
    Such a class should implement the methods:

        rosters(self)
                        returning a list objects with roster values.

    """
    def __init__(self, salary_system=None, salary_article_tm=None, report_start_date=None, \
                report_first_absdate=None, report_end_date=None, report_last_absdate=None, release=True, \
                test=False, articles=[], extra_articles=[], article_types=None):
        self.salary_system = salary_system
        self.test = test
        if report_start_date:
            self.start = report_start_date
        else:
            last_month_date = datetime.now().replace(day=1) - timedelta(days=(datetime.now().day +1))
            self.start = datetime(year=last_month_date.year, month=last_month_date.month , day=1)
        if report_end_date:
            self.end = report_end_date
        else:
            self.end = datetime(year=datetime.now().year, month=datetime.now().month, day=1)
        if report_first_absdate:
            self.firstdate = report_first_absdate
        else:
            self.firstdate = AbsTime('01' + self.start.strftime('%b') + self.start.strftime('%Y'))
        if report_last_absdate:
            self.lastdate = report_last_absdate
        else:
            self.lastdate = AbsTime('01' + self.end.strftime('%b') + self.end.strftime('%Y'))
        if salary_article_tm:
            self.salary_article_tm = salary_article_tm
        else:
            self.salary_article_tm = get_article_table(pstart=self.firstdate, pend=self.lastdate)
        self.report_path = REPORT_PATH
        self.release = release
        self.articles = articles
        self.articleCodes = {}
        self.extra_articles = extra_articles
        self.articleTypes = article_types
        # self.rundata = rundata

    def __str__(self):
        return 'Generic Run'

    def get_article_type(self, article):
        """ Get type of article, to determine which field to put the value in
            'amount' : e.g. an monetary amount, SEK1000
            'number' : e.g. a quantity of something, 10:00 -> 10 (hours)

            None is interpreted as 'number' """

        if self.articleTypes != None:
            return self.articleTypes[article]
        else:
            return None

    def run_info(self, report_type='ECReport'):
        log.info('''
#########################################################
# ECReport {type} report
# Report salary system  : {report_salary_system}
# Execution date        : {dt}
# Report start date     : {report_start_date}
# Report end date       : {report_end_date}
# Report files located in {report_path}
# {release_info}
#########################################################'''.format(
            type=report_type,
            dt=datetime.now(),
            report_start_date=self.firstdate,
            report_end_date=self.lastdate,
            report_path=REPORT_PATH,
            report_salary_system=self.salary_system,
            release_info='Released to : {dst}'.format(dst=RELEASE_PATH if self.release else 'Report not released')
            ))

    def rosters(self, rave_expr, roster_manager, crew_ids=[]):
        if not rave_expr or rave_expr == None or rave_expr == '':
            raise NotImplementedError("rosters can not be generated without rave_expr")
        if len(crew_ids) == 0:
            if self.salary_system != None and self.salary_system.lower() == 'all':
                where_expr = (rave_expr)
            else:
                where_expr=('salary.%%salary_system%%(%s) = "%s"' % (self.firstdate, self.salary_system) , rave_expr)
            salary_iterator = rave.iter(rave_iterator, where=where_expr)
            old_salary_month_start = rave.param(startparam).value()
            rave.param(startparam).setvalue(self.firstdate)
            old_salary_month_end = rave.param(endparam).value()
            rave.param(endparam).setvalue(self.lastdate)
            try:
                if roster_manager == 'perdiem':
                    rosters = PerDiemRosterManager(rave_context, salary_iterator).getPerDiemRosters()
                elif roster_manager == 'supervis':
                    rosters = SupervisRosterManager(rave_context, salary_iterator).getSupervisRosters()
                elif roster_manager == 'overtime':
                    rosters = OvertimeRosterManager(rave_context, salary_iterator).getOvertimeRosters()
                else:
                    raise NotImplementedError("rosters can not be generated without roster_manager")
            finally:
                rave.param(startparam).setvalue(old_salary_month_start)
                rave.param(endparam).setvalue(old_salary_month_end)
        else:
            rosters = []
            for crew_id in crew_ids:
                where_expr=('crew.%%id%% = "%s"' % str(crew_id), \
                    rave_expr)
                log.debug("Roster rave where expression: {0}".format(where_expr))
                salary_iterator = rave.iter(rave_iterator, where=where_expr)
                old_salary_month_start = rave.param(startparam).value()
                rave.param(startparam).setvalue(self.firstdate)
                old_salary_month_end = rave.param(endparam).value()
                rave.param(endparam).setvalue(self.lastdate)
    
                try:
                    rosters.append(PerDiemRosterManager(rave_context, salary_iterator).getPerDiemRosters()[0])
                except Exception:
                    log.error("Crew id: {0} not found".format(crew_id))
            rave.param(startparam).setvalue(old_salary_month_start)
            rave.param(endparam).setvalue(old_salary_month_end)
        return rosters


class PerDiemRun(ECGenericRun):
    def __init__(self, salary_system=None, crew_ids=[], salary_article_tm=None, report_start_date=None, report_first_absdate=None, report_end_date=None, report_last_absdate=None, release=True, test=False):
        ECGenericRun.__init__(self, salary_system, salary_article_tm, report_start_date, report_first_absdate, report_end_date, report_last_absdate, release, test)
        self.crew_ids = crew_ids
        self.rave_expr = 'not salary.%crew_excluded% and not salary.%ec_rank_excluded%'
        log.debug("PerDiemRun config with firstdate: {0}  and lastdate: {1}".format(report_first_absdate, report_last_absdate))
        

    # run the perdiem and return the entries
    def run(self):
        self.run_info(report_type='PerdiemRun')
        rosters = self.rosters(rave_expr=self.rave_expr, roster_manager='perdiem', crew_ids=self.crew_ids)
        log.debug("Perdiem rosters length is: {0}".format(len(rosters)))
        # entries { 'salary_system_country': [(Currency Code,Issue Date,Type,User ID,Value,Reference ID,Number of units,Operation)] }
        # definition: {'COUNTRY_CODE' :[(Currency Code: DKK, Issue Date: 27/07/2020, Type: 2020, User ID: 1525, Value: 500.00, Notes  : 100006037,,)]}
        # example: {'DK': [(DKK,27/07/2020,2020,1525,500.00,100006037,,)]}
        entries = { 'NO': [], 'SE': [], 'DK': [], 'CN': [], 'HK': [], 'JP': [] }
        for crew in rosters:      
            if crew.salarySystem in salary_systems.keys():
                for a in salary_perdim_article[crew.salarySystem]:
                    func = getattr(self, a)
                    value = func(crew)
                    if value is not None and int(value) != 0:
                        entries[crew.salarySystem].append((crew.homeCurrency, self.start.strftime('%d/%m/%Y'), self.salary_article_tm[crew.salarySystem][a], crew.empNo, value/ 100.0 if self.salary_article_tm[crew.salarySystem][a] != '3234' else '', '', value/ 150000.0 if self.salary_article_tm[crew.salarySystem][a] == '3234' else '', ''))
                
                for e in self.extra_articles:
                    func = getattr(self, e)
                    value = func(crew)
                    if value is not None and int(value) != 0:
                        entries[crew.salarySystem].append((crew.homeCurrency, self.start.strftime('%d/%m/%Y'), self.salary_article_tm[crew.salarySystem][a], crew.empNo, value/ 100.0 if self.salary_article_tm[crew.salarySystem][a] != '3234' else '', '', value/ 150000.0 if self.salary_article_tm[crew.salarySystem][a] == '3234' else '', ''))
            
            else:
                log.debug("No salary system for crew {0}".format(crew.crewId))
        return entries
    

    def MEAL_C(self, rec):
        # DK: 1540, positive in normal cases
        # NO: 3705, positive in normal cases
        if rec.mainFunc == 'C':
            return times100(rec.getMealReduction())
        return 0

    def MEAL_F(self, rec):
        # DK: 1530, positive in normal cases
        # NO: 3700, positive in normal cases
        if rec.mainFunc == 'F':
            return times100(rec.getMealReduction())
        return 0

    def MEAL(self, rec):
        #SE: Now reported positive as requested in SKPROJ-499
        return times100(rec.getMealReduction())

    def PERDIEM_SALDO(self, rec):
        # DK: 1550
        # S3: 713 saldo - it can be positive or negative
        # NO: 3065, note that the value is negated
        # HK, CN, JP
        saldo = times100(rec.getPerDiemCompensation())
        if self.salary_system == 'NO' or (self.salary_system.lower() == 'all' and rec.salarySystem == 'NO'):
            return -saldo
        else:
            return saldo
    
    def PERDIEM_TAX(self, rec):
        # DK: 2989
        return times100(rec.getPerDiemCompensationForTax())

    def PERDIEM_NO_TAX(self, rec):
        # DK: 1548
        return times100(rec.getPerDiemCompensationWithoutTax())

    def PERDIEM_TAX_DAY(self, rec):
        # NO: 4084
        # SE: 395
        if self.salary_system == 'NO' or (self.salary_system.lower() == 'all' and rec.salarySystem == 'NO'):
            return times100(rec.getPerDiemForTaxOneDayNO())
        if self.salary_system == 'SE' or (self.salary_system.lower() == 'all' and rec.salarySystem == 'SE'):
            return times100(rec.getPerDiemForTaxOneDaySKS())
        else:
            raise NotImplementedError("PERDIEM_TAX_DAY article is only for SE and NO.")

    def PERDIEM_TAX_DOMESTIC(self, rec):
        # NO: 4078
        # SE: 396
        if self.salary_system == 'NO' or (self.salary_system.lower() == 'all' and rec.salarySystem == 'NO'):
            return times100(rec.getPerDiemForTaxDomesticNO())
        if self.salary_system == 'SE' or (self.salary_system.lower() == 'all' and rec.salarySystem == 'SE'):
            return times100(rec.getPerDiemForTaxDomesticSKS())
        else:
            raise NotImplementedError("PERDIEM_TAX_DOMESTIC article is only for SE and NO.") 

    def PERDIEM_TAX_INTER(self, rec):
        # SE: 397
        return times100(rec.getPerDiemForTaxInternationalSKS())

    def PUBL_HOLIDAY_COMP(self, rec):
        return times100(rec.getPublHolidayComp())
    

class SupervisRun(ECGenericRun):
    def __init__(self, salary_system=None, crew_ids=[], salary_article_tm=None, report_start_date=None, report_first_absdate=None, report_end_date=None, report_last_absdate=None, release=True, test=False):
        ECGenericRun.__init__(self, salary_system, salary_article_tm, report_start_date, report_first_absdate, report_end_date, report_last_absdate, release, test)
        self.crew_ids = crew_ids
        self.rave_expr = 'salary.%inst_has_any_allowance% and not salary.%ec_rank_excluded%'
        log.debug("SupervisRun config with firstdate: {0}  and lastdate: {1}".format(report_first_absdate, report_last_absdate))

    def run(self):
        self.run_info(report_type='SupervisRun')
        rosters = self.rosters(rave_expr=self.rave_expr, roster_manager='supervis', crew_ids=self.crew_ids)
        log.debug("Supervis rosters length is: {0}".format(len(rosters)))
        # entries { 'salary_system_country': [(Currency Code,Issue Date,Type,User ID,Value,Reference ID,Number of units,Operation)] }
        # definition: {'COUNTRY_CODE' :[(Currency Code: DKK, Issue Date: 27/07/2020, Type: 2020, User ID: 1525, Value: None, Notes  : 100006037, Number of units: 12.25,)]}
        # example: {'DK': [(DKK,27/07/2020,2020,1525,,100006037,12.25,)]}
        entries = { 'NO': [], 'SE': [], 'DK': [], 'CN': [], 'HK': [], 'JP': [] }
        for crew in rosters:
            if crew.salarySystem in salary_systems.keys():
                for a in salary_supervis_article[crew.salarySystem]:
                    func = getattr(self, a)
                    unit_number = func(crew)
                    if unit_number is not None and int(unit_number) != 0:
                        try: 
                            entries[crew.salarySystem].append((crew.homeCurrency, self.start.strftime('%d/%m/%Y'), self.salary_article_tm[crew.salarySystem][a], crew.empNo, '', '', unit_number/100.0, ''))
                        except Exception as e:
                            log.error("Crew {0} in salary group {1} does not have valid salary article for {2}".format(crew.crewid, crew.salarySystem, a))
                for e in self.extra_articles:
                    func = getattr(self, e)
                    unit_number = func(crew)
                    if unit_number is not None and int(unit_number) != 0:
                        entries[crew.salarySystem].append((crew.homeCurrency, self.start.strftime('%d/%m/%Y'), self.salary_article_tm[crew.salarySystem][a], crew.empNo, '', '', unit_number/100.0, ''))
            else:
                log.debug("No salary system for crew {0}".format(crew.crewId))
        return entries

    def INST_LCI(self, rec):
        """Instructor's allowance (SH)."""
        return times100(rec.lci_sh)

    def INST_LCI_LH(self, rec):
        """Instructor's allowance (LH)."""
        return times100(rec.lci_lh)

    def INST_LIFUS_ACT(self, rec):
        return times100(rec.lifus_act)
        #return hours100(rec.lifus_act)

    def INST_ETOPS_LIFUS_ACT(self, rec):
        return times100(rec.etops_lifus_act)
    def INST_ETOPS_LC_ACT(self, rec):
        return times100(rec.etops_lc_act)

    def INST_PC_OPC(self, rec):
        return hours100(rec.pc_opc)

    def INST_PC_OPC_BD(self, rec):
        return times100(rec.pc_opc_bd)

    def INST_TYPE_RATING(self, rec):
        return hours100(rec.type_rating)

    def INST_TYPE_RATING_BD(self, rec):
        return times100(rec.type_rating_bd)

    def INST_CLASS(self, rec):
        return hours100(rec.classroom)

    def INST_CC(self, rec):
        return hours100(rec.cc)

    def INST_SKILL_TEST(self, rec):
        return hours100(rec.skill_test)

    def INST_SIM(self, rec):
        return hours100(rec.sim)

    def INST_SIM_SKILL_BR(self, rec):
        return hours100(rec.sim_skill_bd)

    def INST_NEW_HIRE(self, rec):
        #return hours100(rec.new_hire_follow_up_act)
        return times100(rec.new_hire_follow_up_act)

    def INST_CC_QA(self, rec):
        return times100(rec.cc_qa)

    def SIM_INSTR_FIXED(self, rec):
        return times100(rec.sim_instr_fixed)

    def INST_CC_LCS_LINK(self, rec):
        return times100(rec.cc_lcs_link)

class OvertimeRun(ECGenericRun):
    def __init__(self, salary_system=None, crew_ids=[], salary_article_tm=None, report_start_date=None, report_first_absdate=None, report_end_date=None, report_last_absdate=None, release=True, test=False):
        ECGenericRun.__init__(self, salary_system, salary_article_tm, report_start_date, report_first_absdate, report_end_date, report_last_absdate, release, test)
        self.crew_ids = crew_ids
        self.rave_expr = 'not salary.%crew_excluded% and not salary.%ec_rank_excluded%'
        log.debug("OvertimeRun config with firstdate: {0}  and lastdate: {1}".format(report_first_absdate, report_last_absdate))
        self.cached_PR_data = self.generate_PR_acc_data()
    def run(self):
        self.run_info(report_type='OvertimeRun')
        rosters = self.rosters(rave_expr=self.rave_expr, roster_manager='overtime', crew_ids=self.crew_ids)
        log.debug("Supervis rosters length is: {0}".format(len(rosters)))
        # entries { 'salary_system_country': [(Currency Code,Issue Date,Type,User ID,Value,Reference ID,Number of units,Operation)] }
        # definition: {'COUNTRY_CODE' :[(Currency Code: DKK, Issue Date: 27/07/2020, Type: 2020, User ID: 1525, Value: None, Notes  : 100006037, Number of units: 12.25,)]}
        # example: {'DK': [(DKK,27/07/2020,2020,1525,,100006037,12.25,)]}
        entries = { 'NO': [], 'SE': [], 'DK': [], 'CN': [], 'HK': [], 'JP': [] }
        for crew in rosters:
            if crew.salarySystem in salary_systems.keys():
                for a in salary_overtime_article[crew.salarySystem]:
                    func = getattr(self, a)
                    unit_number = func(crew)
                    if unit_number is not None and int(unit_number) != 0:
                        try: 
                            entries[crew.salarySystem].append((crew.homeCurrency, self.start.strftime('%d/%m/%Y'), self.salary_article_tm[crew.salarySystem][a], crew.empNo, '', '', unit_number/100.0, ''))
                        except Exception as e:
                            log.error("Crew {0} in salary group {1} does not have valid salary article for {2}".format(crew.crewId, crew.salarySystem, a))
                for e in self.extra_articles:
                    func = getattr(self, e)
                    unit_number = func(crew)
                    if unit_number is not None and int(unit_number) != 0:
                        entries[crew.salarySystem].append((crew.homeCurrency, self.start.strftime('%d/%m/%Y'), self.salary_article_tm[crew.salarySystem][a], crew.empNo, '', '', unit_number/100.0, ''))
            else:
                log.debug("No salary system for crew {0}".format(crew.crewId))
        return entries


    def MDCSH(self, rec):
        """ Maitre de Cabin, short haul """
        return hours100(rec.getMDCShortHaul())

    def MDCLH(self, rec):
        """ Maitre de Cabin, long haul """
        return hours100(rec.getMDCLongHaul())

    def SCC(self, rec):
        if rec.isCC4EXNG:
            return hours100(rec.getSCCAll())
        return hours100(rec.getSCC())

    def SCCSVS(self, rec):
        return hours100(rec.getSCCSVS())

    def SNGL_SLIP_LONGHAUL(self, rec):
        if rec.isFlightCrew:
            return times100(rec.getSnglSlipLonghaul())
        else:
            return 0
    def ABS_PR_LOA_D(self, rec):
        check=0
        check=no_of_PR_days(self, rec.crewId)
        return check
    
    def SCCNOP(self, rec):
        if rec.isCC4EXNG:
            return 0
        return hours100(rec.getSCCNOP())
    
    #Caching Data
    def generate_PR_acc_data(self):
        startMonth = datetime.now().replace(month=1)
        endMonth=startMonth.replace(month=self.end.month)
        start_month_date=datetime(startMonth.year, startMonth.month, 1).strftime('%d%b%Y  %H:%M')
        end_month_date = datetime(startMonth.year, endMonth.month, 1).strftime('%d%b%Y  %H:%M')
        reasoncode_query = '(|(reasoncode=OUT Roster)(reasoncode=OUT Correction))'
        accountName= 'PR'
        PR_Transactions = TM.account_entry.search("(&(tim>{start_date})(tim<{end_date})(account={account}){reasoncode})".format(
            start_date=start_month_date,
            end_date=end_month_date,
            account=accountName,
            reasoncode=reasoncode_query
        ))
        tnx_dict = {}
        for tnx in PR_Transactions:
            tnx_dict.setdefault(tnx.crew.id, [])
            tnx_dict[tnx.crew.id].append({
                'tnx_dt' :  tnx.tim,
                'PR_amount' : tnx.amount
            })
        return(tnx_dict)

# Utility functions

#PR calculation for current month:- Only 3 PR days can be allocated for a certain month, 
# rest are carry forwarded to next month
def CalPRinCurrentMonth(PRperMonth):
    rem = 0
    count = 0
    for i in PRperMonth:
        val=-i
        val+=rem
        if(val>300):
            rem = val-300
            if (rem >0):
                count=300
        else:
            count=val
            rem = 0
    return count

def times100(value):
    """ Return integer where value is multiplicated with 100 """
    if int(NVL(value)) == 0:
        return 0
    return int(round(value * 100.0))

def hours100(value):
    """ Return integer from a RelTime where value is the number of hours
    (2 decimals) multiplicated with 100 """
    if int(NVL(value)) == 0:
        return 0
    (hhh, mm) = (value, 0) if type(value) == int else value.split()
    return int(round((hhh + (mm / 60.0)) * 100.0))

def minutes100(value):
    """ Return integer from a RelTime where value is the number of minutes
    (2 decimals) multiplicated with 100 """
    if int(NVL(value)) == 0:
        return 0
    (hhh, mm) = value.split()
    return 6000 * hhh + 100 * mm

#Calculates PR days allocated per crew
def no_of_PR_days(self,crew_id):
    format = "%d%b%Y %H:%M:%S:%f"
    startMonth=datetime.now().replace(month=1)
    endMonth=startMonth.replace(month=self.end.month)
    PRperMonth = []
    crew_tnx=[]
    try:
        crew_tnx=self.cached_PR_data[crew_id]
    except KeyError as ke:
        print('Key Not Found in Employee Dictionary:', ke)
    for i in range(endMonth.month - startMonth.month):
        monthStart = startMonth.month + i
        ae_tim = datetime(startMonth.year, monthStart, 1).strftime(format)
        start_month_date = AbsTime(ae_tim[:15])
        monthEnd = startMonth.month + i +1
        tim = datetime(startMonth.year, monthEnd, 1).strftime(format)
        end_month_date = AbsTime(tim[:15])
        PRamount=0
        for transaction in crew_tnx:
            if(transaction['tnx_dt']>=start_month_date and transaction['tnx_dt']<end_month_date):
                PRamount+=transaction['PR_amount']                        
        PRperMonth.append(PRamount)
    currentCount = CalPRinCurrentMonth(PRperMonth)
    return currentCount

def get_article_table(pstart, pend):
    tm_articles = {
        'SE': {}, # S3
        'NO': {},
        'DK': {},
        'CN': {},
        'HK': {},
        'JP': {}
    }
    TM.loadTables(['salary_article'])
    for art in TM.salary_article.search("(&(validfrom<={pend})(validto>{pstart}))".format(pend=pend, pstart=pstart)):
        if art.extsys != 'SE':
            if art.extsys == 'S3':
                tm_articles['SE'][art.intartid] = art.extartid
            else: 
                tm_articles[art.extsys][art.intartid] = art.extartid
    return tm_articles


def createCSV(entries, release, studio, filename_prefix='Payments_CMS'):
    csv_files = []
    report_dt = datetime.now().strftime('%Y%m%d%H%M%S')
    if not os.path.exists(REPORT_PATH):
        os.makedirs(REPORT_PATH)
    if release and not os.path.exists(RELEASE_PATH):
        os.makedirs(RELEASE_PATH)
    for co in entries.keys():
        if len(entries[co]) > 0:
            if studio:
                csv_file = filename_prefix + '_' + co + '_STUDIO_' + str(report_dt) + '.csv'
            else:
                csv_file = filename_prefix + '_' + co + '_' + str(report_dt) + '.csv'
            csv_files.append(csv_file)
            log.debug("Creating csv file: {0}".format(REPORT_PATH + csv_file))
            with open(REPORT_PATH + csv_file, 'w') as f:
                # entries [(Currency Code,Issue Date,Type,User ID,Value,Reference ID,Number of units,Operation)]
                # entries [('NOK', '01/10/2020', '3065', '34961', -3604.5, '', '', '')]
                
                if studio:
                    f.write('Currency Code,Issue Date,Type,User ID,Value,Number of units'+ os.linesep ) # csv header
                else:
                    f.write('Currency Code,Issue Date,Type,User ID,Value,Reference ID,Number of units,Operation'+ os.linesep ) # csv header

                for (homeCurrency, start, article, empNo, value, n, units, o) in entries[co]:
                    # DK => D1530, D1540, D1548, D1550
                    # NO => N3150
                    if co == 'DK' and article in ['1530','1540', '1548', '1550'] and article[0] != 'D':
                        article = 'D' + article
                    elif co == 'NO' and article in ['3150'] and article[0] != 'N':
                        article = 'N' + article
                    
                    if studio:
                        f.write("{0},{1},{2},{3},{4},{5},{6}".format(homeCurrency, start, article, empNo ,value, units, os.linesep ))
                    else:
                        f.write("{0},{1},{2},{3},{4},{5},{6},{7}{8}".format(homeCurrency, start, article, empNo ,value, n, units , o, os.linesep ))
            if release:
                csv_file_not_dated = filename_prefix + '_' + co + '.csv'
                copyfile(REPORT_PATH + csv_file, RELEASE_PATH + csv_file_not_dated)
        else:
            log.debug("{0} => length: {1} =>=> {2}".format(co, len(entries[co]), entries[co]))
    log.debug("csv_files: {0}".format(csv_files))
    return csv_files
