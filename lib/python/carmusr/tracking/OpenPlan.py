############################################################

############################################################
import Errlog
import Cui
import Cfh
import Gui
import carmstd.cfhExtensions
import tempfile
from carmstd.carmexception import CarmException
import tm
import Crs
import StartTableEditor
import traceback
import copy
import AbsDate
import AbsTime
import RelTime
import time
import re
import Variable
import carmensystems.studio.Tracking.OpenPlan as OpenPlanSys
import carmensystems.studio.Tracking.PlanMonitor
import utils.ServiceConfig as ServiceConfig
import os
from utils.TimeServerUtils import now
from carmusr.application import isDayOfOps
import carmusr.application as application

class CfhCheckString(Cfh.String):
    def __init__(self, *args):
        Cfh.String.__init__(self, *args)
        self._check_methods = []
    def register_check(self,check_func, arg=None):
        if check_func not in self._check_methods:
            self._check_methods.append([check_func, arg])

    def check(self,text):
        message = Cfh.String.check(self, text)
        if message:
            return message
        for func,arg in self._check_methods:
            if arg:
                message = func(arg)
            else:
                message = func()
            if message:
                return message
        return None
    
    
class CfhUpperCaseString(CfhCheckString):
    """A wrapper for Cfh.String which always gives upper case """
    def __init__(self, *args):
        CfhCheckString.__init__(self, *args)
        
    def check(self, text):
        message = CfhCheckString.check(self,text)
        self.assign(text.upper())
        return message

class CfhCheckDone(Cfh.Done):
    def __init__(self, *args):
        Cfh.Done.__init__(self, *args)
        self._check_methods = []
    def register_check(self,check_func, arg=None):
        if check_func not in self._check_methods:
            self._check_methods.append([check_func, arg])
            
    def action(self):
        for func,arg in self._check_methods:
            if arg:
                message = func(arg)
            else:
                message = func()
            if message:
                break
        else:
            Cfh.Done.action(self)
        
class CallFuncOnClick(Cfh.Function):
    """
    Cfh.Function class which calls registered functions on call
    """
    def __init__(self, *args):
        Cfh.Function.__init__(self, *args)
        self._funcs=[]
        self._check_methods=[]
        
    def register_function(self,func,arg=None):
        if func not in self._funcs:
            self._funcs.append([func,arg])
            
    def register_check(self,func,arg=None):
        if func not in self._check_methods:
            self._check_methods.append([func,arg]) 
    
    def action(self):
        for func,arg in self._check_methods:
            if arg:
                message  = func(arg)
            else:
                message  = func()
            if message:
                return #We have an error, don't call functions
        for func,arg in self._funcs:
            if arg:
                func(arg)
            else:
                func()
    
class LoadFilterSelectionTracking(Cfh.Box):
    """The filter dialog used in tracking studios"""
    def __init__(self, param_collection, *args):
        Cfh.Box.__init__(self, *args)
        self.now_time = param_collection.NOW

        months=["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        months_selections = ";"+";".join(months)
        year = int(self.now_time.ddmonyyyy()[5:9])
        years = [str(year-1),str(year),str(year+1)]
        years_selection = ";"+";".join(years)

        # Fields for open period
        self.start_year = CfhCheckString(self, "START_YEAR", 4,
                                        param_collection.START_YEAR)
        self.start_year.setMandatory(True)
        self.start_year.setMenuString(years_selection)

        self.end_year = CfhCheckString(self, "END_YEAR", 4,
                                      param_collection.END_YEAR)
        self.end_year.setMandatory(True)
        self.end_year.setMenuString(years_selection)
              
        self.start_month = CfhUpperCaseString(self, "START_MONTH", 3,
                                              param_collection.START_MONTH)
        self.start_month.setMandatory(1)
        self.start_month.setMenuOnly(1)
        self.start_month.setMenuString(months_selections)
        

        self.end_month = CfhUpperCaseString(self, "END_MONTH", 3,
                                            param_collection.END_MONTH)
        self.end_month.setMandatory(1)
        self.end_month.setMenuOnly(1)
        self.end_month.setMenuString(months_selections)

        
        # Field for selection filter method 
        self.planningarea = Cfh.String(self, "PLANNINGAREA", 10,
                                       param_collection.PLANNING_AREA)
        self.planningarea.setMandatory(1)
        self.planningarea.setMenuOnly(1)
        # Don't forget to define matching filtersting in get_area_filter_exp below

        planning_areas=["ALL", "ALL_SK", "SKD", "SKI", "SKN", "SKS", "SVS"]

        pa_selections = ";"+";".join(planning_areas)
        self.planningarea.setMenuString(pa_selections)

        # Warning labels, two lines by using two strings
        self.warning = Cfh.String(self, "WARNING",160, "")
        self.warning.setEditable(0)
        self.warning.setStyle(Cfh.CfhSLabelNormal)
        
        # OK and CANCEL buttons
        self.ok = CfhCheckDone(self,"B_OK")
        # I am not sure that cancel works in this construct
        self.quit = Cfh.Cancel(self,"B_CANCEL")

        self.save = CallFuncOnClick(self,"B_SAVE")
        self.save.register_function(param_collection.saveDefaults)

        self.clear = CallFuncOnClick(self,"B_RESET")
        self.clear.register_function(param_collection.resetDefaults)

        form_layout = """
FORM;LOAD_FILTER_FORM;Open Plan Load Filter
BANNER;Please select period and area; 1
GROUP
COLUMN;7
LABEL;Start:
COLUMN;7
FIELD;START_MONTH;``
COLUMN
FIELD;START_YEAR;``
GROUP
COLUMN;7
LABEL;End:
COLUMN;7
FIELD;END_MONTH;``
COLUMN
FIELD;END_YEAR;``
GROUP
COLUMN;7
LABEL;Area:
COLUMN
FIELD;PLANNINGAREA;``
GROUP
COLUMN;45
FIELD;WARNING;``
BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
BUTTON;B_SAVE;`Set As Default`;`_Save`
BUTTON;B_RESET;`Clear Defaults`;`_Clear`
"""
        
        load_form_file = tempfile.mktemp()
        f = open(load_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(load_form_file)
        os.unlink(load_form_file)

    def show(self, *a):
        rv = Cfh.Box.show(self, *a)
        self.start_year.register_check(self.show_warnings)
        self.end_year.register_check(self.show_warnings)
        self.start_month.register_check(self.show_warnings)
        self.end_month.register_check(self.show_warnings)
        self.ok.register_check(self.check_ok_click)
        self.save.register_check(self.check_ok_click)

        if os.environ['CARMSYSTEMNAME'].endswith('MIRROR'):
            Gui.GuiWarning("This is a Production-Mirror\nDo not use unless you have written instruction to do so.")
        return rv

    def get_period(self):
        """
        Gets period from values in form
        """
        try:
            start_month = self.start_month.getValue()
            start_year = str(int(self.start_year.getValue())) #Check that its a number
            end_month = self.end_month.getValue()
            end_year = str(int(self.end_year.getValue())) #Check that its a number
            start_time = AbsTime.AbsTime('1'+start_month+start_year)
            end_time = AbsTime.AbsTime('2'+end_month+end_year)
            end_time = end_time.month_ceil()-RelTime.RelTime('00:01')
            return (start_time, end_time)
        except:
            return (None,None)

    def get_warnings(self):
        """
        Checks period and gives a warning
        """
        (start_time, end_time) = self.get_period()
        if start_time and end_time:
            if end_time < self.now_time:
                return "Historic period! Accumulators will not be updated"
        return ""
    
    def get_errors(self):
        """
        Checks period for errors
        """
        (start_time, end_time) = self.get_period()
        one_day = RelTime.RelTime(1, 0, 0)
        if start_time and end_time:
            if isDayOfOps and (start_time < self.now_time.month_floor()):
                return "Start a Stand-Alone Studio to view or edit historic data"
            if start_time > end_time:
                return "Start-time must be smaller then end-time"

            if start_time < self.now_time:
                # not too long historic data (3 months * 31 days = 93)
                historic_days = int((min(self.now_time,end_time)-start_time)/one_day)
                if historic_days > 93:
                    return "Trying to open too much historic data"

            if end_time > self.now_time:
                future_days = int((end_time-max(self.now_time,start_time))/one_day)
                sr_time = self.now_time.month_ceil().addmonths(1)
                if start_time >= sr_time:
                    # After scheduled release the rosters should contain very little data and we can open large periods
                    if future_days > 1100:
                        return "Trying to open too much future data"
                else:
                    # Not too much future data if we open published rosters (7 months * 31 days = 217)
                    if future_days > 217:
                        return "Trying to open too much data. Try a shorter period or a period after %s"%sr_time
        else:
            return "Invalid start or end time."
        return ""
    
    def show_warnings(self):
        """
        Displays warnings or errors in dialog
        """
        # Clear warning
        self.warning.assign("")
        error = self.get_errors()
        if error:
            self.warning.assign(error)
            return 
        warning = self.get_warnings()
        if warning:
            self.warning.assign(warning)

    def check_ok_click(self):
        """
        If period contains errors, displays the error message and halts ok-action
        """
        error = self.get_errors()
        self.warning.assign(error)
        return error

    def getValues(self):
        """
        Function returning the values set in the form. 
        """
        return (self.start_year.getValue(),
                self.start_month.getValue(),
                self.end_year.getValue(),
                self.end_month.getValue(), 
                self.planningarea.getValue())
        

class LoadFilterSelectionReportWorker(Cfh.Box):
    """The filter dialog used when loading report worker studio filters in studio"""
    def __init__(self, now_time, default_rw='SAS_RS_WORKER_LATEST_BATCH1'):
        Cfh.Box.__init__(self, "LOAD_RW", "Load ReportWorker plan")
        self.now_time = CfhCheckString(self, "NOW_TIME", 9, str(now_time))
        self.now_time.setMandatory(True)
        
        self.report_worker = CfhUpperCaseString(self, "REPORT_WORKER", 32, default_rw)
        self.report_worker.setMandatory(True)
        self.report_worker.setMenuString(';'.join(self.getReportWorkers()))
        
        self.start_date = CfhCheckString(self, "START_DATE",9, str(AbsTime.AbsTime(now_time).month_floor()))
        self.end_date = CfhCheckString(self, "END_DATE",9,  str(AbsTime.AbsTime(now_time).month_ceil()))
        
        # OK and CANCEL buttons
        self.ok = CfhCheckDone(self,"B_OK")
        # I am not sure that cancel works in this construct
        self.quit = Cfh.Cancel(self,"B_CANCEL")

        form_layout = """
FORM;LOAD_RW;Load ReportWorker plan
BANNER;Please select report worker and parameters; 1
GROUP
COLUMN;7
LABEL;Now time:
COLUMN;7
FIELD;NOW_TIME;``
GROUP
COLUMN;8
LABEL;Report worker:
COLUMN;22
FIELD;REPORT_WORKER;``
GROUP
COLUMN;12
LABEL;Custom RW start:
COLUMN;7
FIELD;START_DATE;
GROUP
COLUMN;12
LABEL;Custom RW end:
COLUMN;7
FIELD;END_DATE;``
GROUP
COLUMN;25
BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
"""
        load_form_file = tempfile.mktemp()
        f = open(load_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(load_form_file)
        os.unlink(load_form_file)
        
    def getReportWorkers(self):
        from utils.ServiceConfig import ServiceConfig as C
        c = C()
        return [str(x[0].split('/')[-1]) for x in c.getProperties("programs/reportserver/process")]
        
    def check_ok_click(self):
        print "Hipp"

    def show(self, *a):
        rv = Cfh.Box.show(self, *a)
        self.ok.register_check(self.check_ok_click)
        return rv
    
    def getValues(self):
        """
        Function returning the values set in the form. 
        """
        return (self.now_time.getValue(),
                self.report_worker.getValue(),
                self.start_date.getValue(),
                self.end_date.getValue())
        
class LoadFilterSelectionCrew(Cfh.Box):
    """The filter dialog used when loading a single crew in studio"""
    def __init__(self, now_time, crew_id=""):
        Cfh.Box.__init__(self, "LOAD_CREWID", "Load single-crew plan")
        
        self.crew_id_1 = CfhUpperCaseString(self, "CREW_ID_1", 5, crew_id)
        self.crew_id_1.setMandatory(True)
        self.crew_id_2 = CfhUpperCaseString(self, "CREW_ID_2", 5, "")
        self.crew_id_3 = CfhUpperCaseString(self, "CREW_ID_3", 5, "")
        self.crew_id_4 = CfhUpperCaseString(self, "CREW_ID_4", 5, "")
        self.crew_id_5 = CfhUpperCaseString(self, "CREW_ID_5", 5, "")
        
        self.start_date = CfhCheckString(self, "START_DATE",9, str(AbsTime.AbsTime(now_time).month_floor()))
        self.start_date.setMandatory(True)
        self.end_date = CfhCheckString(self, "END_DATE",9,  str(AbsTime.AbsTime(now_time).month_ceil()))
        self.end_date.setMandatory(True)
        
        # OK and CANCEL buttons
        self.ok = CfhCheckDone(self,"B_OK")
        # I am not sure that cancel works in this construct
        self.quit = Cfh.Cancel(self,"B_CANCEL")

        form_layout = """
FORM;LOAD_RW;Load single-crew plan
BANNER;Please choose crew and dates; 1
GROUP
COLUMN;7
LABEL;Crew ID:
COLUMN;7
FIELD;CREW_ID_1;``
FIELD;CREW_ID_2;``
FIELD;CREW_ID_3;``
FIELD;CREW_ID_4;``
FIELD;CREW_ID_5;``
GROUP
COLUMN;12
LABEL;Start date:
COLUMN;7
FIELD;START_DATE;
GROUP
COLUMN;12
LABEL;End date:
COLUMN;7
FIELD;END_DATE;``
GROUP
COLUMN;25
BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
"""
        load_form_file = tempfile.mktemp()
        f = open(load_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(load_form_file)
        os.unlink(load_form_file)
        
    def check_ok_click(self):
        print "Hipp"

    def show(self, *a):
        rv = Cfh.Box.show(self, *a)
        self.ok.register_check(self.check_ok_click)
        return rv
    
    def getValues(self):
        """
        Function returning the values set in the form. 
        """
        return (",".join([self.crew_id_1.getValue(), 
                          self.crew_id_2.getValue(),
                          self.crew_id_3.getValue(),
                          self.crew_id_4.getValue(),
                          self.crew_id_5.getValue()]),
                self.start_date.getValue(),
                self.end_date.getValue())
        
class OpenPlanParameterHandler:
    def __init__(self):
        """
        Init the parameterclass
        """    
        self._config = ServiceConfig.ServiceConfig()
        self.PERIOD_START = None
        self.PERIOD_END = None
        self.DB_PERIOD_START = None
        self.DB_PERIOD_END = None
        self.PERIOD_PRE = None
        self.PERIOD_POST = None
        self.PLANNING_AREA = None
        self._filterdialog = None
        self._user_canceled = False
        self.NOW = None
        self.START_YEAR = None
        self.START_MONTH = None
        self.END_YEAR = None
        self.END_MONTH = None
        self.CREW_ID = None

        self._planning_area_name = 'PlanArea'
        self._start_month_name = 'PlanStartMonth'
        self._start_year_name = 'PlanStartYear'
        self._end_month_name = 'PlanEndMonth'
        self._end_year_name = 'PlanEndYear'
        self._resource_location = 'planning_filter'

    
    def setupPlanPeriod(self,USING_ALERT):
        """
        Sets the planning area using flag to determine if to show dialog or not
        """
        # Get current day from studio to use time server if it's in use
        self.NOW = AbsTime.AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea,
                                                         "WINDOW", "fundamental.%now%"))
        # Get varibles from Resources
        self.PLANNING_AREA = self.getResource(self._resource_location,self._planning_area_name) \
                             or "ALL" # In case not found
        self.START_YEAR = self.getResource(self._resource_location,self._start_year_name) or \
                          self.NOW.ddmonyyyy(True)[5:9]
        self.START_MONTH = self.getResource(self._resource_location,self._start_month_name) or \
                           self.NOW.ddmonyyyy(True)[2:5]
        self.END_YEAR = self.getResource(self._resource_location,self._end_year_name) or \
                        self.NOW.ddmonyyyy(True)[5:9]
        self.END_MONTH = self.getResource(self._resource_location,self._end_month_name) or \
                         self.NOW.ddmonyyyy(True)[2:5]
        self._user_canceled = False
        #Give the dialog if needed!
        if USING_ALERT:
            # Get values from CARMSYS which reads <period_start> and <period_end>
            # from $CARMUSR/datamodel/data_model.xml. We want to start at the
            # first day of the month!
            (start_of_period, end_of_period) = OpenPlanSys.getPeriodStartAndEnd()
            self.PERIOD_START = start_of_period.month_floor()
            self.PERIOD_END = end_of_period
            print "PERIOD_START %s, PERIOD_END %s" % (self.PERIOD_START, self.PERIOD_END)
        elif os.environ.get('SINGLE_CREW_PLAN',''):
            crew = os.environ.get('SINGLE_CREW_PLAN','')
            # If crew ID(s) were specified in the environment, do not show the dialog 
            if len(crew) > 1:
                self.setupPlanPeriodFromEnvironment()
                self.CREW_ID = crew
            else:
                flt = LoadFilterSelectionCrew(now())
                flt.show(1)
                if flt.loop() <> Cfh.CfhOk:
                    self._user_canceled = True
                crewId,starttime,endtime = flt.getValues()
                self.PERIOD_START = AbsTime.AbsTime(starttime)
                self.PERIOD_END = AbsTime.AbsTime(endtime)
                self.PLANNING_AREA = os.environ.get('PLANNING_AREA','ALL')
                self.CREW_ID = crewId
        elif self.planPeriodSpecified():
            # The environment specifies the plan to use. Do not show dialog.
            self.setupPlanPeriodFromEnvironment()
        else:
            # Setup period by START_/END_MONTH and START_/END_YEAR variables
            self.updatePeriodFromSettings()
            
            if self._filterdialog is None:
                self._filterdialog = LoadFilterSelectionTracking(self, "Load_filter_diag")
                Errlog.log("FileHandlingExt:: Initializing tracking dialog")
            
            self._filterdialog.show(1)
            if self._filterdialog.loop() <> Cfh.CfhOk:
                #Register that user pressed cancel
                self._user_canceled = True
                # Unpack results
            self.updatePeriodAndArea()
        # Change color of pp background dependant on environment for admins
        setCustomColors()
            
    def planPeriodSpecified(self):
        return bool(os.environ.get('PERIOD_START','')) or bool(os.environ.get('PERIOD_END',''))
    
    def setupPlanPeriodFromEnvironment(self):
        if self.planPeriodSpecified():
            if os.environ.get('PERIOD_START',''):
                self.PERIOD_START = AbsTime.AbsTime(os.environ['PERIOD_START'])
                self.PERIOD_END = AbsTime.AbsTime(os.environ.get('PERIOD_END',str((AbsTime.AbsTime(self.PERIOD_START)+RelTime.RelTime(1)).month_ceil())))
            else:
                self.PERIOD_END = AbsTime.AbsTime(os.environ['PERIOD_END'])
                self.PERIOD_START = AbsTime.AbsTime(os.environ.get('PERIOD_START',str((AbsTime.AbsTime(self.PERIOD_START)+RelTime.RelTime(-1)).month_floor())))
        else:
                self.PERIOD_START = AbsTime.AbsTime(os.environ.get('PERIOD_START',str(AbsTime.AbsTime(now()).month_floor())))
                self.PERIOD_END = AbsTime.AbsTime(os.environ.get('PERIOD_END',str((AbsTime.AbsTime(self.PERIOD_START)+RelTime.RelTime(1)).month_ceil())))
        self.PLANNING_AREA = os.environ.get('PLANNING_AREA','ALL')

    def setupDbPeriod(self,USING_ALERT,preBuffer):
        """
        Sets the database period
        """
        # Calculate DB buffers
        self.PERIOD_PRE = preBuffer
        self.PERIOD_POST = self.getResource("config","DataPeriodDbPost")
        self.DB_PERIOD_START = self.PERIOD_START - \
                               RelTime.RelTime(int(self.PERIOD_PRE)*24*60)
        self.DB_PERIOD_END = self.PERIOD_END + \
                             RelTime.RelTime(int(self.PERIOD_POST)*24*60) + \
                             RelTime.RelTime(24*60-1)

        
    def get_area_filter_exp(self):
        """
        Converts between area and filter-expression
        """
        user_selection={'ALL':('ALL','###','###'),
                        'ALL_SK':('SK_','###','###'),
                        'SKI':('SKI','###','###'),
                        'SKS':('SKS','SKI','AL'),
                        'SKD':('SKD','SKI','AL'),
                        'SKN':('SKN','SKI','AL'),
                        'SVS':('SVS','###','###')}
        try:
            return user_selection[self.PLANNING_AREA]
        except KeyError:
            # Return all as default case
            return ('ALL', '###', '###')
        
    def updatePeriodAndArea(self):
        """
        Updates params with current choosen filter values
        """
        if self._filterdialog and not self.Canceled():
            (START_YEAR, START_MONTH, END_YEAR, END_MONTH, PLANNING_AREA) = \
                         self._filterdialog.getValues()
            # To prevent "strange" behavior when studio tries to save string
            # Form string is wrapped C-string and this caused problems
            self.PLANNING_AREA = copy.deepcopy(PLANNING_AREA)
            self.START_YEAR = copy.deepcopy(START_YEAR)
            self.START_MONTH = copy.deepcopy(START_MONTH)
            self.END_YEAR = copy.deepcopy(END_YEAR)
            self.END_MONTH = copy.deepcopy(END_MONTH)
            self.updatePeriodFromSettings()
            
    def updatePeriodFromSettings(self):
        self.PERIOD_START = AbsTime.AbsTime('1'+self.START_MONTH+self.START_YEAR)
        self.PERIOD_END = AbsTime.AbsTime('1'+self.END_MONTH+self.END_YEAR)
        self.PERIOD_END = ((self.PERIOD_END.adddays(1)).month_ceil()).adddays(-1)
        
    def saveDefaults(self):
        """
        Saves current values in personal resources. Called when click on Set As Default in form
        
        """
        self.updatePeriodAndArea()
        
        self.setResource(self._resource_location,self._start_year_name,self.START_YEAR,
                         "Default start year")
        self.setResource(self._resource_location,self._start_month_name,self.START_MONTH,
                         "Default start month")
        self.setResource(self._resource_location,self._end_year_name,self.END_YEAR,
                         "Default end year")
        self.setResource(self._resource_location,self._end_month_name,self.END_MONTH,
                         "Default end month")
        self.setResource(self._resource_location,self._planning_area_name,self.PLANNING_AREA,
                         "Planners personal area")
        
    def resetDefaults(self):
        """
        Resets the resources to blank. Called when click on Reset Defaults in form
        """
        self.setResource(self._resource_location, self._start_year_name,"","Default start year")
        self.setResource(self._resource_location, self._start_month_name,"","Default start month")
        self.setResource(self._resource_location, self._end_year_name,"","Default end year")
        self.setResource(self._resource_location, self._end_month_name,"","Default end month")
        self.setResource(self._resource_location, self._planning_area_name, "", "Planners personal area")
        
    def getResource(self,module,property):
        """
        Reads personal resource from module/property
        """
        return  Crs.CrsGetModuleResource(module,
                                           Crs.CrsSearchModuleDef,
                                           property)
    
    def setResource(self,module,property,value,description=""):
        """
        Sets personal resource
        """
        Crs.CrsSetModuleResource(module, property,value,description)
        
    def getProperty(self, property):
        """
        Gets property from configuration
        """
        (_, item) = self._config.getProperty(property)
        return item
    
    def Canceled(self):
        """
        True if user canceled dialog
        """
        return self._user_canceled

    def get_plan_area(self):
        """
        Returns the plan area.
        """
        plan_area = ""
        if self.PLANNING_AREA is None:
            # Loading a scenario
            try:
                plan_area = OpenPlanSys.getPlanningAreaScenario()
            except:
                pass
        else:
            plan_area = self.PLANNING_AREA
        if not plan_area:
            plan_area = "ALL"
        return plan_area

def loadPlan(script=None):
    """
    Wrapper function for studios load plan, to pop up studio visible
    before showing the open plan dialog
    """
    Cui.CuiSetVisible(Cui.gpc_info, 1)
    #OpenPlanSys.loadPlan()

    if script is not None:
        exec("import %s" %(script))

    
def loadReportWorkerPlan():
    import __main__
    flt = LoadFilterSelectionReportWorker(now())
    flt.show(1)
    if flt.loop() <> Cfh.CfhOk:
        return
    nowtime,rw,starttime,endtime = flt.getValues()
    nowAbs = AbsTime.AbsTime(nowtime)
    startAbs = AbsTime.AbsTime(starttime)
    endAbs = AbsTime.AbsTime(endtime)
    os.environ["REL_START"] = "%+d" % (int(startAbs - nowAbs)/1440 - 7)
    os.environ["REL_END"] = "%+d" % (int(endAbs - nowAbs)/1440 + 7)
    print "REL_START",os.environ["REL_START"]
    print "REL_END",os.environ["REL_END"]
    os.environ['SIMULATED_REPORTSERVERNAME'] = rw
    import carmensystems.studio.Tracking.PlanMonitor as PlanMonitor
    import modelserver as M
    class TimeUpdaterDummy:
        def __init__(self):
            self.timeClient = self
        def getTime(self, *a):
            print "getTime",a
            y,m,d,_,_ = nowAbs.split()
            return time.mktime((y,m,d,12,0,0,0,0,0))
            
    c = ServiceConfig.ServiceConfig()
    print c.getProperty("reportserver/%s/data_model/period_start" % rw)
    print c.getProperty("reportserver/%s/data_model/period_end" % rw)
    PlanMonitor._connectToAlertServer = 0
    PlanMonitor._planMonitor = PlanMonitor.PlanMonitor("StudioEditor")
    PlanMonitor._planMonitor.timeupdater = TimeUpdaterDummy()
    print "***",PlanMonitor._planMonitor.determinPeriodStart(c, nowAbs, rw, "reportserver", "xxx")
    PlanMonitor._planMonitor.load(c, setupTimeRefresh=True, programName="reportserver", process=rw)
    PlanMonitor._initialState = M.TableManager.instance().getState()
    
def loadSingleCrewPlan():
    old = os.environ.get('SINGLE_CREW_PLAN')
    try:
        os.environ['SINGLE_CREW_PLAN'] = '1'
        OpenPlanSys.loadPlan()
    finally:
        if old:
            os.environ['SINGLE_CREW_PLAN'] = old
        else:
            del os.environ['SINGLE_CREW_PLAN']

def setCustomColors():
    '''
    Set studio background color based on environment and user role
    DEV  - Green
    TEST - Yellow
    PROD - Red

    Role - Only for administrators
    '''

    FUNCTION = '::setCustomColors::'
    MODULE = '::OpenPlan'
    Errlog.log(MODULE+FUNCTION+" Entered in " + os.getenv("CARMSYSTEMNAME"))
    
    try:
        csys  = os.getenv("CARMSYSTEMNAME")
        crole = os.getenv("CARMROLE")
        if (application.isTracking or application.isDayOfOps) and crole in ["Administrator"]:
            if csys in ["PROD"]:
                # Light red
                Cui.CuiCrcSetParameterFromString('studio_config.%pp_background_color_p%', '20')
            elif csys in ["PROD_TEST"]:
                # Light yellow
                Cui.CuiCrcSetParameterFromString('studio_config.%pp_background_color_p%', '13')
            elif csys in ["CMSDEV"]:
                # Light green
                Cui.CuiCrcSetParameterFromString('studio_config.%pp_background_color_p%', '17')
            return

    except:
        Errlog.log(MODULE+FUNCTION+"Could not set custom studio colors")
        traceback.print_exc()
    
    
