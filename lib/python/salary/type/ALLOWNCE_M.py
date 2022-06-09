"""
Monthly reported allowances
"""


import salary.conf as conf
import salary.run as run
import carmensystems.rave.api as rave
import salary.type.OVERTIME as overtime
from salary.Overtime import OvertimeRoster
import salary.type.SUPERVIS as supervis
from salary.api import SalaryException, zap


class AllowanceRoster(object):
    """
    Class fields structure:
    AllowanceRoster:
        crewid
        empno
        articles - dict:
            article: value
    """

    def __init__(self, crewid, empno):
        self.crewid = crewid
        self.empno = empno
        self.articles = {}

    def add_data(self, article, value):
        """
        Creates a new item in self.articles and writes data there,
        or finds an existing item in self.articles and adds
        a new value to an old one.
        """
        if not (article in self.articles.keys()):
            self.articles[article] = value
        else:
            # add to existing values if any
            self.articles[article] += value

    def __str__(self):
        return "AllowanceRoster: crewid = %s, empno = %s, articles = %s" % (str(self.crewid), str(self.empno), str(self.articles))


class MonthlyAllowanceRun(run.GenericRun):
    def __init__(self, rundata, articles):
        super(MonthlyAllowanceRun, self).__init__(rundata, articles)
        self.accumulated_rosters = []

    def run(self):
        runid = super(MonthlyAllowanceRun, self).run()
        return runid

    def _accumulate(self, crewid, empno, article, value):
        # find an existing roster or create a new one
        for roster in self.accumulated_rosters:
            if roster.crewid == crewid:
                break
        else:
            roster = AllowanceRoster(crewid, empno)
            self.accumulated_rosters.append(roster)
        # a roster we work with is now in a "roster" variable
        roster.add_data(article, value)

    def rosters(self):
        # run an overtime run
        s3_overtime_run = overtime.S3(self.rundata)
        try:
            s3_overtime_run.run(create_report=False)
        except SalaryException as e:
            # no rosters is not an error here
            if str(e)[:len("No rosters qualified for ")] == "No rosters qualified for ":
                pass
            else:
                raise
        else:
            for roster in s3_overtime_run.accumulated_rosters:
                self._accumulate(roster.crewId, roster.empNo, 'SCC', self.SCC(roster))
                self._accumulate(roster.crewId, roster.empNo, 'CALM_OTFC', self.CALM_OTFC(roster))
                self._accumulate(roster.crewId, roster.empNo, 'CALW', self.CALW(roster))
        # delete the overtime run - we do not need it anymore
        zap(s3_overtime_run.rundata.runid)

        # run a supervis run
        s3_supervis_run = supervis.S3(self.rundata)
        try:
            s3_supervis_run.run()
        except SalaryException as e:
            # no rosters is not an error here
            if str(e) == "No matching rosters found.":
                pass
            else:
                raise
        else:
            # supervis run gives us an iterator instead of a list of rosters
            for roster in s3_supervis_run.accumulated_rosters:
                self._accumulate(roster.crewid, roster.empno, 'INST_CLASS', self.INST_CLASS(roster))
                self._accumulate(roster.crewid, roster.empno, 'INST_LCI', self.INST_LCI(roster))
                self._accumulate(roster.crewid, roster.empno, 'INST_CC', self.INST_CC(roster))
                self._accumulate(roster.crewid, roster.empno, 'INST_CRM', self.INST_CRM(roster))
                self._accumulate(roster.crewid, roster.empno, 'INST_LCI_LH', self.INST_LCI_LH(roster))
                self._accumulate(roster.crewid, roster.empno, 'INST_LIFUS_ACT', self.INST_LIFUS_ACT(roster))
                self._accumulate(roster.crewid, roster.empno, 'INST_NEW_HIRE', self.INST_NEW_HIRE(roster))
                self._accumulate(roster.crewid, roster.empno, 'INST_SIM', self.INST_SIM(roster))
                self._accumulate(roster.crewid, roster.empno, 'INST_SIM_SKILL_BR', self.INST_SIM_SKILL_BR(roster))
                self._accumulate(roster.crewid, roster.empno, 'INST_SKILL_TEST', self.INST_SKILL_TEST(roster))
                self._accumulate(roster.crewid, roster.empno, 'SIM_INSTR_FIXED', self.SIM_INSTR_FIXED(roster))
        # delete the supervis run - we do not need it anymore
        zap(s3_supervis_run.rundata.runid)
        return self.accumulated_rosters

    def _CALM_OTFC(self, rec):
        """ Canlendar month / Flight crew OT for SKS"""
        if rec.isFlightCrew:
            if self.hours100(rec.getCalendarMonth()) + self.hours100(rec.getCalendarMonthPartTimeExtra()) > 0:
                return self.hours100(rec.getCalendarMonth())
            else:
                return self.hours100(rec.getOvertime())

    def _CALW(self, rec):
        """ Calendar week (42 hrs) """
        return self.hours100(rec.getCalendarWeek())

    def _OT(self, rec):
        if rec.isFlightCrew:
            return 0
        return self.hours100(rec.getOvertime())

    def INST_CLASS(self, rec):
        return self.hours100(rec.classroom)

    def INST_LCI(self, rec):
        """Instructor's allowance (SH)."""
        return self.times100(rec.lci_sh)

    def INST_CC(self, rec):
        return self.hours100(rec.cc)

    def INST_CRM(self, rec):
        return self.hours100(rec.crm)

    def INST_LCI_LH(self, rec):
        """Instructor's allowance (LH)."""
        return self.times100(rec.lci_lh)

    def INST_LIFUS_ACT(self, rec):
        return self.times100(rec.lifus_act)

    def INST_NEW_HIRE(self, rec):
        return self.times100(rec.new_hire_follow_up_act)

    def INST_SIM(self, rec):
        return self.hours100(rec.sim)

    def INST_SIM_SKILL_BR(self, rec):
        return self.hours100(rec.sim_skill_bd)

    def INST_SKILL_TEST(self, rec):
        return self.hours100(rec.skill_test)

    def SIM_INSTR_FIXED(self, rec):
        return self.times100(rec.sim_instr_fixed)

    def SCC(self, rec):
        if self.isCC4EXNG:
            return self.hours100(rec.sCC if rec.sCC else 0 + rec.sCCNoPurser if rec.sCCNoPurser else 0)
        else:
            return self.hours100(rec.sCC)

    def CALM_OTFC(self, rec):
        # result is being multiplied by 2 as we need a number of half-hours here
        if rec.isFlightCrew:
            return self._CALM_OTFC(rec)
        else: # SASCMS-3396
            return self.hours100(rec.getCalendarMonth())

    def CALW(self, rec):
        if rec.isCC4EXNG:
            return self._OT(rec)
        else:
            return self._CALW(rec)

    def save_run(self, rosters):
        for roster in rosters:
            for article in self.articles:
                if article in roster.articles.keys():
                    self.save(roster, article, roster.articles[article])

    def save(self, rec, article, value):
        extartid = self.articleCodes[article]
        articleType = self.get_article_type(article)
        if articleType != None:
            extartid = extartid + ':' + articleType
        self.data.append(rec.crewid, rec.empno, extartid, value)


class S3(MonthlyAllowanceRun):
    def __init__(self, rundata):
        articles = ['INST_CLASS', 'INST_LCI', 'INST_CC', 'INST_CRM', 'INST_LCI_LH', 'INST_LIFUS_ACT',
            'INST_NEW_HIRE', 'INST_SIM', 'INST_SIM_SKILL_BR', 'INST_SKILL_TEST', 'SCC', 'CALM_OTFC', 'CALW',
            'SIM_INSTR_FIXED']
        MonthlyAllowanceRun.__init__(self, rundata, articles)

    def __str__(self):
        return "Monthly reported allowances for Swedish crew"