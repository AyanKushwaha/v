
# import carmensystems.rave.api as rave
from utils.rave import RaveIterator
from salary.api import SalaryException
import logging



logging.basicConfig()
log = logging.getLogger('ECSupervis')


class SupervisRosterManager:
    
    def __init__(self, context, iterator):
        # self.articles = ['INST_LCI', 'INST_LCI_LH', 'INST_LIFUS_ACT', 'INST_PC_OPC',
        #                 'INST_PC_OPC_BD', 'INST_TYPE_RATING', 'INST_TYPE_RATING_BD',
        #                 'INST_CLASS', 'INST_CRM', 'INST_CC', 'INST_SKILL_TEST','INST_SIM', 
        #                 'INST_SIM_SKILL_BR','INST_NEW_HIRE','INST_CC_QA', 'SIM_INSTR_FIXED',
        #                 'INST_LC_SVS', 'INST_SIM_SKILL_BR_SVS', 'INST_LIFUS_ACT_SVS','INST_GD_SVS']
        # self.articles_se = ['INST_CLASS', 'INST_LCI', 'INST_CC', 'INST_CRM', 'INST_LCI_LH',
        #                     'INST_LIFUS_ACT', 'INST_NEW_HIRE', 'INST_SIM', 'INST_SIM_SKILL_BR', 
        #                     'INST_SKILL_TEST', 'SIM_INSTR_FIXED']
        self.context = context
        self.iterator = iterator
        # self.test_fields = {
        #     'crewid': 'crew.%id%',
        #     'empno': 'crew.%employee_number%',
        #     'salary_system': 'salary.%salary_system%(salary.%salary_run_date%)',  
        # }
        self.fields = {
            'crewid': 'crew.%id%',
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
            'cc_qa': 'salary.%inst_supernum_release%',
            'sim_instr_fixed': 'salary.%sim_instr_fixed%',
            'salarySystem': 'salary.%salary_system%(salary.%salary_run_date%)',
            'homeCurrency': 'report_per_diem.%per_diem_home_currency%',
            'lifus_act_svs':  'salary.%inst_lifus_act_svs%',
            'inst_lci_svs': 'salary.%inst_lci_svs%',
            'ground_instr_svs': 'salary.%inst_is_leg_instructor_svs%',
            'sim_skill_bd_svs' : 'salary. %inst_sim_skill_brief_debrief_svs%',
        }

    def getSupervisRosters(self):
        supervisRosters = []
        # iterator = rave.iter('iterators.roster_set')
        # iterator = rave.iter(self.roster_iterator, self.fields)
        # iterator = self.roster_iterator.eval()
        iterator = RaveIterator(self.iterator, self.fields)
        supervisRosters = iterator.eval(self.context)
        if len(supervisRosters) == 0:
            raise SalaryException("No matching rosters for supervis found.")
        return supervisRosters



