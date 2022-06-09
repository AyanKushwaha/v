import os
import sys
import Cui
import AbsTime
import RelTime
import carmusr.planning.FileHandlingExt
import carmusr.ConfirmSave as cs

def run():
    import adhoc.ScriptRunner
    adhoc.ScriptRunner.run()

class AbstractScriptExecution:
    '''
    Structure of the life of a macro, performed the following steps
     1) Open plan
     2) Runs actions defined in self._actions
     3) Saves plan
     4) Exits studio
    '''
    def __init__(self,start_p, end_p, area_p, schema_p):
        self._start_p = start_p
        self._end_p = end_p
        self._area_p = area_p
        self._schema_p = schema_p
        self._actions = {}
        
    def __str__(self):
        return self.__class__.__name__
    
    def execute(self):
        print 'Script Runner: Starting execution of %s'%self
        self._open_plan()
        for action in self._actions:
            if self._actions[action]:
                action(*self._actions[action])
            else:
                action()
        self._save_plan()
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

    def _save_plan(self):
        print 'Script Runner: save plan'
        cs.skip_confirm_dialog = True #Set global variable in carmusr/ConfirmSave.py
        Cui.CuiSavePlans(Cui.gpc_info,Cui.CUI_SAVE_DONT_CONFIRM+Cui.CUI_SAVE_SILENT+Cui.CUI_SAVE_FORCE)

    def _open_plan(self):
        print 'Script Runner: Open plan %s %s %s %s'%(self._start_p, self._end_p,self._area_p, self._schema_p )

        # Set up the open plan dialog that will be used (a singleton)
        openPlanDialog = carmusr.planning.FileHandlingExt.PlanningDeamonFilterDialog()
        openPlanDialog.period_start = AbsTime.AbsTime(self._start_p)
        openPlanDialog.period_end = AbsTime.AbsTime(self._end_p)
        openPlanDialog.planning_area = self._area_p

        formData = {"FORM":"OPEN_DATABASE_PLAN", "PERIOD_START":" %s" % openPlanDialog.period_start ,"PERIOD_END":" %s" % openPlanDialog.period_end}

        print "Script Runner: Will try to open the following plan: %s" % (self._schema_p)
        lpString =  os.path.dirname(self._schema_p)
        flags = 0
        ret = Cui.CuiOpenSubPlan(formData, Cui.gpc_info, lpString, self._schema_p, flags)
        print "Cui.CuiOpenSubPlan returned: %s" % (ret)


class DblQualLineCheckUpdate(AbstractScriptExecution):
    def __init__(self, date, schema):
        start_period = AbsTime.AbsTime(date)
        start_p = str(start_period.month_floor())[:9]
        end_p = str((start_period + RelTime.RelTime("00:01")).month_ceil())[:9]
        AbstractScriptExecution.__init__(self, start_p, end_p, 'FD_SKI', schema)
        self._date = date
        self._actions = {self.doUpdate:None}
        
    def doUpdate(self):
        import carmusr.upd_dbl_qual as upd_dbl
        upd_dbl.run_it(self._date, True)


class BatchPublish(AbstractScriptExecution):
    def __init__(self, date, area, schema):
        start_period = AbsTime.AbsTime(date)
        start_p = str(start_period.month_floor())[:9]
        end_p = str((start_period + RelTime.RelTime("00:01")).month_ceil())[:9]

        if area in ['ALL_FD', 'ALLFD', 'FD']:
            area = "ALL FD"
        elif area in ['ALL_CC', 'ALLCC', 'CC']:
            area = "ALL CC"

        AbstractScriptExecution.__init__(self, start_p, end_p, area, schema)
        self._date = date
        self._actions = {self.run:None}
        
    def run(self):
        import carmusr.rostering.Publish
        import carmensystems.rave.api as R
        publisher = carmusr.rostering.Publish.BatchPublish()
        publisher.publish()

class HistoricPublish(BatchPublish):
    def run(self):
        import carmusr.rostering.Publish
        publisher = carmusr.rostering.Publish.HistoricPublish()
        publisher.publish()

class HistoricPublishNoSplit(BatchPublish):
    def run(self):
        import carmusr.rostering.Publish
        publisher = carmusr.rostering.Publish.HistoricPublish(split=False)
        publisher.publish()

class TagPublish(BatchPublish):
    def run(self):
        import carmusr.rostering.Publish
        publisher = carmusr.rostering.Publish.TagPublish()
        publisher.publish()

def run_script(schema, function, start_p, area_p = "ALL FD", end_p = '1Jan1986'):
    execution = None

    scriptMap = {
        'UpdateDoubleQualLineCheck':DblQualLineCheckUpdate(start_p, schema),
        'BatchPublish': BatchPublish(start_p, area_p, schema),
        'HistoricPublish':HistoricPublish(start_p, area_p, schema),
        'HistoricPublishNoSplit':HistoricPublishNoSplit(start_p, area_p, schema),
        'TagPublish':TagPublish(start_p, area_p, schema)
        }
    try:
        execution = scriptMap.get(function)
    except KeyError:
        print 'No matching macro execution found'
        sys.exit(-2)
    execution.execute()
