#

#
__version__ = "$Revision$"
"""
SelectCrewTrainingForm
Module for doing:
Searching crew_training_log for activties 
@date:25Sep2008
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
#CARMUSR Imports
import utils.CfhFormClasses as CFC
import carmusr.HelperFunctions as HF
import carmusr.CrewTableHandler as CTH

#CARMSYS Imports
import carmensystems.rave.api as R
import AbsTime
import Cui
import Errlog
import tm
from utils.dave import EC
import re
from modelserver import ReferenceError
import RelTime
import Select
import Gui
from carmstd import gui_ext

global LOG_SEARCH_FORM
LOG_SEARCH_FORM = None

global SELECT_SCHOOLPLAN_FORM
SELECT_SCHOOLPLAN_FORM = None

def start_form(area=Cui.CuiWhichArea):
    try:
        assert HF.isDBPlan()
        area = Cui.CuiAreaIdConvert(Cui.gpc_info,area)
        global LOG_SEARCH_FORM
        if LOG_SEARCH_FORM is None:
            LOG_SEARCH_FORM = CrewTrainingLogForm()
        LOG_SEARCH_FORM()
        (code, have_code, start_time, end_time) = (LOG_SEARCH_FORM.code,
                                                   LOG_SEARCH_FORM.have_code,
                                                   LOG_SEARCH_FORM.start_time,
                                                   LOG_SEARCH_FORM.end_time)
        
        select_crew(code, have_code, start_time, end_time, area)
        
    except CFC.CancelFormError, err:
        Errlog.log('SelectCrewTrainingForm:: %s'%err)
    except AssertionError:
        Errlog.log('SelectCrewTrainingForm:: Only available in database plan')

def select_crew(code, have_code, start_time, end_time, area=Cui.CuiWhichArea):
    
    area = Cui.CuiAreaIdConvert(Cui.gpc_info,area)
    CTH.update_ctl_changed_crew()
    found_matching_crew = set()
    regexp = re.compile(r'^%s'%code.replace('*','.*'))
    for log in tm.TM.crew_training_log.search('(&(tim>=%s)(tim<%s))'%(start_time,end_time)):
        if regexp.match(log.code):
            try:
                found_matching_crew.add(log.crew.id)
            except ReferenceError, err:      
                Errlog.log('SelectCrewTrainingForm:: Error ; %s'%err)
    ec = None
    try:
        ec = EC(tm.TM.getConnStr(), tm.TM.getSchemaStr())
        for log in ec.crew_training_log.search('(tim>=%s)'%int(start_time)):
            if regexp.match(log.code) and  log.tim < end_time:
                found_matching_crew.add(log.crew)
    finally:
        if ec:
            ec.close()
    all_crew = set([crew.id for crew in tm.TM.crew])
    if have_code:
        crew_list = [crew for crew in found_matching_crew if crew in all_crew] # If crew change planning area
    else:
        crew_list = [crew for crew in all_crew if crew not in found_matching_crew]
    Cui.CuiDisplayGivenObjects(Cui.gpc_info,area,  Cui.CrewMode, Cui.CrewMode,crew_list)
        
class CrewTrainingLogForm(CFC.BasicCfhForm):
    def __init__(self,title='Select by  Training Activity:'):
        CFC.BasicCfhForm.__init__(self,title)
        self._delta_y = 11
        start_time, = R.eval('fundamental.%pp_start%')
        end_time, = R.eval('fundamental.%pp_end%')

        self._find_option = {'HAVE':True, "HAVE NOT":False}
        
        self.add_filter_combo(0,0,'find_option','Find Crew Who:','HAVE',
                              options=self._find_option.keys(), upper=True)
        self.add_filter_combo(1,0,'code','Activity Code:','*',options=[],upper=True)
        self.add_label(2,0,'between','Between')
        self.add_date_combo(3,0,'start_time','Start Time:',
                            start_time.ddmonyyyy(True),date=True)              
        self.add_date_combo(4,0,'end_time','End Time:',
                            end_time.ddmonyyyy(True),date=True)
        
    @property
    def code(self):
        return self.code_field.valof()
    @property
    def have_code(self):
        return self._find_option.get(self.find_option_field.valof(),True)
    @property
    def start_time(self):
        return AbsTime.AbsTime(self.start_time_field.valof())
    @property
    def end_time(self):
        # Form is date, convert to excl time
        return AbsTime.AbsTime(self.end_time_field.valof())+RelTime.RelTime('24:00')


class SchoolplanSelectBox(CFC.BasicCfhForm):
    def __init__(self, title = 'Select by Schoolplan'):
        CFC.BasicCfhForm.__init__(self,title)

        self.add_filter_combo(0,1, "filter_method", "Filter Method", "REPLACE",
                             ["REPLACE","SUBFILTER","ADD"])

        self.add_filter_combo(2,1,"schoolplan_name","Schoolplan Nr:",'*',[], False)

        #Add reset button
        self.reset = CFC.ResetAction(self, "RESET", self.button_area, "Reset Form", "_Reset") 

    @property
    def filter_method(self):
        return self.filter_method_field.getValue()

    @property
    def schoolplan_name(self):
        return self.schoolplan_name_field.getValue()

def select_schoolplan(sel_obj, area=Cui.CuiWhichArea):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)

    global SELECT_SCHOOLPLAN_FORM
    if not SELECT_SCHOOLPLAN_FORM:
        SELECT_SCHOOLPLAN_FORM = SchoolplanSelectBox()

    # When selecting CRRs, crr_name is used.  The planner must manually
    # add the schoolplan name to the trip using Trip -> Properties.

    try:
        SELECT_SCHOOLPLAN_FORM()
        R.param('training.temp_string').setvalue(SELECT_SCHOOLPLAN_FORM.schoolplan_name)
        if sel_obj == 'crew':
            Select.select({'FILTER_METHOD': SELECT_SCHOOLPLAN_FORM.filter_method, 'training.%crew_has_course_in_pp%':'T'}, area, Cui.CrewMode)       
        else:
            Select.select({'FILTER_METHOD': SELECT_SCHOOLPLAN_FORM.filter_method, 'crr_name':SELECT_SCHOOLPLAN_FORM.schoolplan_name}, area, Cui.CrrMode)

    except CFC.CancelFormError, cf:
        Errlog.log("SelectCrewSchoolplan::select_crew:: user cancelled form")
        return 1
    except Exception, e:
        Errlog.log("SelectCrewSchoolplan::select_crew::"+str(e))
        return -1


# Only adds OFDX codes that are valid for the planning period
def add_ofdx_menus(parent_menu):
    ofdx_count = R.eval('task.%ofdx_count%')[0]
    pp_start = R.eval('fundamental.%pp_start%')[0]
    pp_end = R.eval('fundamental.%pp_end%')[0]
    for ix in range(ofdx_count):
        ofdx_valid_start = R.eval('task.%ofdx_valid%({0}, {1})'.format(ix+1, pp_start))[0]
        ofdx_valid_end = R.eval('task.%ofdx_valid%({0}, {1})'.format(ix+1, pp_end))[0]
        if ofdx_valid_start or ofdx_valid_end:
            title, = R.eval('task.%ofdx_code%({0})'.format(ix+1))
            python_expr = "MenuCommandsExt.selectCrew({{'training.%reqd_ofdx_training_missing%({0})':'true'}})".format(ix+1)
            action = 'PythonEvalExpr("{0}")'.format(python_expr.replace('"', '\\"'))
            gui_ext.add_menu_item(parent_menu=parent_menu,
                                  title=title,
                                  potency=Gui.POT_REDO,
                                  opacity=Gui.OPA_OPAQUE,
                                  action=action)
