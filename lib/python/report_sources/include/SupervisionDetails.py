

"""
Test report to verify the Supervision interface.
"""
from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime

import Cui
import Cfh
import carmensystems.publisher.api as prt
import carmensystems.rave.api as R
import salary.conf as conf
import utils.DisplayReport as display

from report_sources.include.SASReport import SASReport
from utils.rave import RaveIterator, MiniEval

class SupervisionDetails(SASReport):

    def create(self):
        if self.arg('startDate') and self.arg('endDate'): 
            startDate = AbsTime(int(self.arg('startDate')))
            endDate = AbsTime(int(self.arg('endDate')))
        else:
            plan = MiniEval({
                'salary_month_start': 'salary.%salary_month_start%',
                'salary_month_end': 'salary.%salary_month_end%',
                }).eval('default_context')
            startDate = plan.salary_month_start
            endDate = plan.salary_month_end

        SASReport.create(self, 'Supervision Details', showPlanData=False,
            headerItems={
                'Salary month start:': startDate,
                'Salary month end:': endDate,
        })

        R.param(conf.startparam).setvalue(startDate)
        R.param(conf.endparam).setvalue(endDate)

        ms, = R.eval('salary.%salary_month_start_p%')
        me, = R.eval('salary.%salary_month_end_p%')
  
        ri = RaveIterator(RaveIterator.iter('iterators.roster_set', 
            where='salary.%inst_has_any_allowance%'), {
                'id': 'crew.%id%',
                'empno': 'crew.%employee_number%',
                'logname': 'crew.%login_name%',
                'rank': 'crew.%rank%',
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
                'supernum_release': 'salary.%inst_supernum_release%',
                'instr_extra_compensation': 'salary.%sim_instr_fixed%',
                'etops_lifus_act': 'salary.%inst_etops_lifus_act%',
                'etops_lc_act': 'salary.%inst_etops_lc_act%',

            })

        li = RaveIterator(RaveIterator.iter('iterators.leg_set', where='salary.%leg_in_period%'), {
            'id': 'leg.%flight_id%',
            'is_flight': 'leg.%is_flight_duty%',
            'code': 'report_common.%leg_code%',
            'dutycd': 'duty_code.%leg_code%',
            'st': 'leg.%start_lt%',
            'et': 'leg.%end_lt%',
            'st_utc': 'ambi.%leg_start%',
            'et_utc': 'ambi.%leg_end%',
            'adep': 'leg.%start_station%',
            'ades': 'leg.%end_station%',
            'time': 'leg.%time%',
            'inst_type': 'salary.%inst_allowance%',
            'is_pc_opc_bd': 'salary.%inst_count_pc_opc_brief_debrief%',
            'is_type_rating_bd': 'salary.%inst_count_type_rating_brief_debrief%',
            'sim_skill_bd_time': 'salary.%inst_sim_skill_bd_time%',
            'sim_skill_briefing_time': 'salary.%inst_sim_skill_briefing_time%',
            'sim_skill_debriefing_time': 'salary.%inst_sim_skill_debriefing_time%',
            })

        ri.link(li)
        rosters = ri.eval('default_context')
        header_items = ('Duty code', 'Activity', 'Start time (UTC)', 'ADEP', 'ADES', 'End time (UTC)', 'Duration', 'Type', 'SIM & Skill-Test Brief/Debrief')

        first = True
        for crew in rosters:
            if not first:
                self.newpage()
            first = False

            self.add(prt.Isolate(prt.Row(B('%s(%s) %-3.3s %s' % (crew.empno,
                crew.id, crew.rank, crew.logname)))))
            self.add(prt.Row(height=16))
            self.add(self.values(crew))
            self.add(prt.Row(height=16))
            self.add(prt.Row(*[B(x) for x in header_items]))

            for leg in crew:
                if leg.is_flight:
                    id = leg.id
                else:
                    id = leg.code

                # Simulator briefing
                if int(leg.sim_skill_briefing_time) > 0:
                    self.add(prt.Column(prt.Row(
                        leg.dutycd,
                        "B"+id[1:],
                        leg.st_utc-leg.sim_skill_briefing_time,
                        leg.adep,
                        leg.ades,
                        leg.st_utc,
                        prt.Text(leg.sim_skill_briefing_time, align=prt.RIGHT),
                        self.get_type(leg.inst_type),
                        '',
                        background=bgcolor(leg.st_utc)),
                    width=self.pageWidth))
                    
                
                self.add(prt.Column(prt.Row(
                        leg.dutycd,
                        id,
                        leg.st_utc,
                        leg.adep,
                        leg.ades,
                        leg.et_utc,
                        prt.Text(leg.time, align=prt.RIGHT),
                        self.get_type(leg.inst_type),
                        '',
                        background=bgcolor(leg.st_utc)),
                    width=self.pageWidth))

                # Simulator debriefing
                if int(leg.sim_skill_debriefing_time) > 0:
                    self.add(prt.Column(prt.Row(
                        leg.dutycd,
                        "D"+id[1:],
                        leg.et_utc,
                        leg.adep,
                        leg.ades,
                        leg.et_utc + leg.sim_skill_debriefing_time,
                        prt.Text(leg.sim_skill_debriefing_time, align=prt.RIGHT),
                        self.get_type(leg.inst_type),
                        time_no_empty(leg.sim_skill_bd_time),
                        background=bgcolor(leg.st_utc)),
                    width=self.pageWidth))

                
                self.page()

    def get_type(self, t):
        try:
            type = ('', 'A/C, LIFUS', 'PC/OPC', 'T/R', 'CLASSROOM', 'LCI SH', 'CRM', 'CC', 'SKILL-Test', 'SIM', 'LCI LH', 'New Hire Follow Up','Supernum, Release','ETOPS LC','ETOPS LIFUS')[int(str(t)[-2:])]
            return type
        except:
            return '?'

    def values(self, crew):
        return prt.Isolate(prt.Column(
            prt.Row('Simulator duty (hours)', RI(crew.sim)),
            prt.Row('Simulator & Skill-Test Brief/Debrief (hours)', RI(crew.sim_skill_bd)),
            prt.Row('Skill-Test (hours)', RI(crew.skill_test)),
            prt.Row('Instructor Extra Compensation (occurrences)', RI(crew.instr_extra_compensation)),
            prt.Row('Line Check Instructor SH (days)', RI(crew.lci_sh)),
            prt.Row('Line Check Instructor LH (days)', RI(crew.lci_lh)),
            prt.Row('LIFUS (days)', RI(crew.lifus_act)),
            prt.Row('Classroom (hours)', RI(crew.classroom)),
            prt.Row('CRM (hours)', RI(crew.crm)),
            prt.Row('CC (hours)', RI(crew.cc)),
            prt.Row('New Hire Follow Up (days)',RI(crew.new_hire_follow_up_act)),
            prt.Row('Supernum, Release (weeks)',RI(crew.supernum_release)),
            ))


class BackGroundColor:
    colors = ('#ffffff', '#e5e5e5')
    def __init__(self):
        self.flag = False
        self.prev_date = 0

    def __call__(self, date):
        if int(date) / 1440 != self.prev_date:
            self.flag = not self.flag
        self.prev_date = int(date) / 1440
        color = self.colors[self.flag]
        return color


bgcolor = BackGroundColor()
 

def time_no_empty(rt):
    try:
        if int(rt) == 0:
            return ''
        else:
            return prt.Text(rt, align=prt.RIGHT)
    except:
        return '?'


def no_void(value):
    if value is None:
        return ''
    return value


def B(*a, **k):
    """Bold text."""
    k['font'] = prt.Font(weight=prt.BOLD)
    return prt.Text(*a, **k)


def RI(*a, **k):
    """Text aligned right."""
    k['align'] = prt.RIGHT
    return prt.Text(*a, **k)

# runReport =============================================================={{{1
def runReport(scope='window'):
    """Run PRT Report in scope 'scope'."""
    if scope == 'plan':
        area = Cui.CuiNoArea
        context = 'sp_crew'
    else:
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, scope)
        context = 'default_context'
    # load previously used start and end dates
    try:
        start_date = R.param('parameters.%supervision_report_start_date%').value()
        end_date = R.param('parameters.%supervision_report_end_date%').value()
    except:
        start_date = None
        end_date = None
    else:
        if start_date == AbsTime('01JAN1986 0:00') or end_date == AbsTime('01JAN1986 0:00'):
            # the parameters are set to the default values - do not pass them to the form
            start_date = None
            end_date = None

    
    rptForm = display.reportFormDate('SupervisionDetails', start_date=start_date, end_date=end_date)
    rptForm.show(True)
    if rptForm.loop() == Cfh.CfhOk:
        R.param('parameters.%supervision_report_start_date%').setvalue(AbsTime(rptForm.getStartDate()))
        R.param('parameters.%supervision_report_end_date%').setvalue(AbsTime(rptForm.getEndDate()))
        args = 'startDate=%s endDate=%s context=%s scheduled=no' % (
                rptForm.getStartDate(), rptForm.getEndDate(), context)
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope,
            '../lib/python/report_sources/include/SupervisionDetails.py', 0, args)
    

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
