
import Cui
from AbsTime import AbsTime
import carmusr.process.step_calls as step
from carmstd.date_extensions import abstime2gui_date_string

from behave import use_step_matcher
use_step_matcher('parse')


# Mainly for DEMO purposes:
@given(u'I create a "{dated_weekly}" local plan')
def step_local_plan(context, dated_weekly):
    """
    Given I create a "dated" local plan
    """
    _step_local_plan(context, dated_weekly)

@given(u'I create a "{dated_weekly}" local plan with planning area "{planning_area}"')
def step_local_plan_area(context, dated_weekly, planning_area):
    """
    Given I create a "dated" local plan with planning area "FD-340"
    """
    _step_local_plan(context, dated_weekly, planning_area)

def _step_local_plan(context, dated_weekly, planning_area=''):
    period,_planning_area,version = context.localplan.split('/')
    planning_area = planning_area or _planning_area
    byp = [('FORM', 'PLANNING_PROCESS_START'),
           ('PERIOD', period),
           ('PLANNING_AREA', planning_area),
           ('VERSION', version),
           ('SSIM_OWN', '200707_FD-340_1_OWN.ssim'),
           ('SSIM_OTHER', ''),
           ]

    if dated_weekly == 'dated':
        dated = True
        byp.append(('START_DATE', abstime2gui_date_string(AbsTime('01Jul2007'))))
        byp.append(('END_DATE', abstime2gui_date_string(AbsTime('31Jul2007'))))

    elif dated_weekly == 'weekly':
        dated = False
        byp.append(('STANDARD_WEEK_START_DATE', abstime2gui_date_string(AbsTime('01Jul2007'))))
    else:
        assert False, 'Cannot handle %s local plans' % dated_weekly
        
    byp.append(('OK', ''))

    bypw = {"WRAPPER": Cui.CUI_WRAPPER_NO_EXCEPTION}

    ret = Cui.CuiBypassWrapper("step.local_plan",
                               lambda: step.local_plan(dated=dated),
                               (byp, bypw))
    if ret:
        assert False, 'Cui.CuiBypassWrapper returned: %s' % ret


@given(u'I create a Sub-plan with Pre-booked Trips from CTF')
def step_pre_booked(context):
     byp = [('FORM', 'PLANNING_PROCESS_START'),
            ('PRE_BOOKED', "200707_FD-340_1_PRE_BOOKED.ctf"),
            ('OK', '')]
     bypw = {"WRAPPER": Cui.CUI_WRAPPER_NO_EXCEPTION}
    
     ret = Cui.CuiBypassWrapper("step.prebooked_trips_from_ctf",
                                 lambda: step.prebooked_trips_from_ctf(),
                                 (byp, bypw))
     if ret:
         assert False, 'Cui.CuiBypassWrapper returned: %s' % ret

@given(u'I create aircraft rotations')
def step_aircraft_rotations(context):
    """
    Given I create aircraft rotations
    """
    ret = step.aircraft_rotations()
    if ret:
        assert False, 'step.aircraft_rotations returned: %s' % ret

@given(u'I create an initial Sub-plan')
def step_sub_plan(context):
    """
    Given I create an initial Sub-plan
    """
    
    byp = [('FORM', 'PLANNING_PROCESS_START'),
           ('START_DATE', abstime2gui_date_string(AbsTime('01Jul2007'))),
           ('END_DATE', abstime2gui_date_string(AbsTime('31Jul2007'))),
           ('OK', '')]
    bypw = {"WRAPPER": Cui.CUI_WRAPPER_NO_EXCEPTION}
    
    ret = Cui.CuiBypassWrapper("step.weekly_sub_plan",
                               lambda: step.weekly_sub_plan(),
                               (byp, bypw))
    if ret:
        assert False, 'Cui.CuiBypassWrapper returned: %s' % ret
        

@given(u'I create slices')
def step_create_slices(context):
    """
    Given I create slices
    """
    ret = step.create_slices()
    if ret:
        assert False, 'step.create_slices returned: %s' % ret


