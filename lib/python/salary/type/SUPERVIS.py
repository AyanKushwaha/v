

"""
Interface 44.2 Instructor's Allowance
"""

# imports ================================================================{{{1
import salary.conf as conf
import carmensystems.rave.api as rave

from utils.fmt import NVL
from utils.rave import RaveIterator
from salary.api import SalaryException
from salary.run import GenericRun


# InstructorIterator ====================================================={{{1
class InstructorIterator(RaveIterator):
    def __init__(self, rd):
        iterator = RaveIterator.iter('iterators.roster_set', where=(
            'salary.%%salary_system%%(%s) = "%s"' % (
                rd.firstdate, 
                rd.extsys if rd.extsys != 'S3' else 'SE'),
            'salary.%inst_has_any_allowance%',
        ))
        fields = {
            'crewid': 'crew.%id%',
            'empno': 'crew.%employee_number%',
            'lifus_act': 'salary.%inst_lifus_act%',
            'lpc_opc': 'salary.%inst_lpc_opc_or_ots%',
            'lpc_opc_ots_bd': 'salary.%inst_lpc_opc_or_ots_bd%',
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
            'cc_qa': 'salary.%inst_supernum_release%',
            'sim_instr_fixed': 'salary.%sim_instr_fixed%',
            'etops_lifus_act': 'salary.%inst_etops_lifus_act%',
            'etops_lc_act': 'salary.%inst_etops_lc_act%',
        }
        RaveIterator.__init__(self, iterator, fields)


# InstructorsAllowanceRun ================================================{{{1
class InstructorsAllowanceRun(GenericRun):
    def __init__(self, rundata, articles=[]):
        articles = ['INST_LCI', 'INST_LCI_LH', 'INST_LIFUS_ACT', 'INST_LPC_OPC_OTS',
                'INST_LPC_OPC_OTS_BD', 'INST_TYPE_RATING', 'INST_TYPE_RATING_BD',
                'INST_CLASS', 'INST_CRM', 'INST_CC', 'INST_SKILL_TEST','INST_SIM', 'INST_SIM_SKILL_BR','INST_NEW_HIRE','INST_CC_QA',
                'SIM_INSTR_FIXED', 'INST_ETOPS_LIFUS_ACT', 'INST_ETOPS_LC_ACT']
        GenericRun.__init__(self, rundata, articles)

    def rosters(self):
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
        if len(rosters) == 0:
            raise SalaryException("No matching rosters found.")
        return rosters

    def save(self, rec, type, value):
        self.data.append(rec.crewid, rec.empno, self.articleCodes[type], value)

    def INST_LCI(self, rec):
        """Instructor's allowance (SH)."""
        return self.times100(rec.lci_sh)

    def INST_LCI_LH(self, rec):
        """Instructor's allowance (LH)."""
        return self.times100(rec.lci_lh)

    def INST_LIFUS_ACT(self, rec):
        return self.times100(rec.lifus_act)
        #return self.hours100(rec.lifus_act)

    def INST_ETOPS_LIFUS_ACT(self, rec):
        return self.times100(rec.etops_lifus_act)

    def INST_ETOPS_LC_ACT(self, rec):
        return self.times100(rec.etops_lc_act)

    def INST_LPC_OPC_OTS(self, rec):
        return self.hours100(rec.lpc_opc_ots)

    def INST_LPC_OPC_OTS_BD(self, rec):
        return self.times100(rec.lpc_opc_ots_bd)


    def INST_TYPE_RATING(self, rec):
        return self.hours100(rec.type_rating)

    def INST_TYPE_RATING_BD(self, rec):
        return self.times100(rec.type_rating_bd)

    def INST_CRM(self, rec):
        return self.hours100(rec.crm)

    def INST_CLASS(self, rec):
        return self.hours100(rec.classroom)

    def INST_CC(self, rec):
        return self.hours100(rec.cc)

    def INST_SKILL_TEST(self, rec):
        return self.hours100(rec.skill_test)

    def INST_SIM(self, rec):
        return self.hours100(rec.sim)

    def INST_SIM_SKILL_BR(self, rec):
        return self.hours100(rec.sim_skill_bd)

    def INST_NEW_HIRE(self, rec):
        #return self.hours100(rec.new_hire_follow_up_act)
        return self.times100(rec.new_hire_follow_up_act)

    def INST_CC_QA(self, rec):
        return self.times100(rec.cc_qa)

    def SIM_INSTR_FIXED(self, rec):
        return self.times100(rec.sim_instr_fixed)


# DK ====================================================================={{{1
class DK(InstructorsAllowanceRun):
    """ For Danish crew. """
    def __str__(self):
        return "Instructor's Allowance for Danish Crew."


# NO ====================================================================={{{1
class NO(InstructorsAllowanceRun):
    """ For Norwegian crew. """
    def __str__(self):
        return "Instructor's Allowance for Norwegian Crew."


# SE ====================================================================={{{1
class SE(InstructorsAllowanceRun):
    """ For Swedish crew. """
    def __str__(self):
        return "Instructor's Allowance for Swedish Crew."


# S3 ====================================================================={{{1
class S3(InstructorsAllowanceRun):
    """ For Swedish crew. """
    def __init__(self, rundata, articles=[]):
        articles = ['INST_CLASS', 'INST_LCI', 'INST_CC', 'INST_CRM', 'INST_LCI_LH',
            'INST_LIFUS_ACT', 'INST_NEW_HIRE', 'INST_SIM', 'INST_SIM_SKILL_BR', 'INST_SKILL_TEST',
            'SIM_INSTR_FIXED', 'INST_ETOPS_LIFUS_ACT', 'INST_ETOPS_LC_ACT']
        InstructorsAllowanceRun.__init__(self, rundata, articles)

        # self.accumulated_rosters will likely become an iterator later.
        # We use a list instead of None here, as we try to iterate over it
        # in ALLOWNCE_M.py without checking if there is anything inside.
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
        return "Instructor's Allowance for Swedish Crew."


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    # BASIC TESTING
    from AbsTime import AbsTime
    import salary.run as run
    iterator = InstructorIterator(run.RunData(firstdate=AbsTime(2012, 12, 1, 0, 0), lastdate=AbsTime(2013, 1, 1, 0, 0), runtype='SUPERVIS', extsys="DK"))
    rosters = iterator.eval(conf.context)
    for r in rosters:
        print r.crewid, r.lifus_act


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
