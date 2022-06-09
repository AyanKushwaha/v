
__version__ = "$Revision: 1.8 $"
"""
TestBaseClass
Module for doing:
Provide basic clss for testcases (pre, run, post actions)
@date:02Apr2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""


import os
import time
import unittest

import Cui
import Variable
import carmensystems.rave.api as R
import carmensystems.studio.MacroRecorder.PlayMacro as PM
import modelserver
import Errlog
import AbsTime
import RelTime

import carmtest.TestBaseClass as TBC
import carmtest.TestUtils as TU

class GuiTest(TBC.MacroTest):
    """
    Base class for GuiTests, will run own macro as test
    """

    def __init__(self, *args):
        """
        Init method, sets tets macroclass and _START_TIME/_END_TIME variables inside plan
        """
        TBC.MacroTest.__init__(self, *args)
        self.crew = None
        self.tmp_macro = None
        self.tmp_macro_class = RowsShowAllAndClearTmpMacro
        try:
            self._START_TIME, = R.eval('default_context','fundamental.pp_start')
            self._START_TIME += RelTime.RelTime('24:00')*5
            self._END_TIME = self._START_TIME + RelTime.RelTime('24:00')*25
        except Exception, err:
            self.log("No rave ruleset loaded, reverting to sourced test env for time period")
            self._START_TIME = AbsTime.AbsTime('01JUL2008 00:00')
            start_day  = os.environ.get('TEST_START_DAY', '01')
            end_day    = os.environ.get('TEST_END_DAY', '31')
            start_mon  = os.environ.get('TEST_START_MONTH', 'JUL')
            end_mon    = os.environ.get('TEST_END_MONTH', 'AUG')
            start_year = os.environ.get('TEST_START_YEAR', '2008')
            end_year   = os.environ.get('TEST_END_YEAR', '2008')
            
            self._START_TIME = AbsTime.AbsTime('%s%s%s'%(start_day,start_mon,start_year))
            self._START_TIME += RelTime.RelTime('24:00')*5
            self._END_TIME =  AbsTime.AbsTime('%s%s%s'%(end_day,end_mon,end_year))
            self._END_TIME -= RelTime.RelTime('24:00')*5
        
    def setUp(self):
        TBC.MacroTest.setUp(self)
        R.param('fundamental.%use_now_debug%').setvalue(True)
        R.param('fundamental.%now_debug%').setvalue(self._START_TIME)
        self.reset_areas()
        
    def tearDown(self):
        TBC.MacroTest.tearDown(self)
        R.param('fundamental.%use_now_debug%').setvalue(False)
        self.log('Reset now debug')
        
    def reset_areas(self):
        """
        Open and show crew in window 1 and trips in window 2
        """
        if Cui.CuiAreaExists({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION},
                             Cui.gpc_info, Cui.CuiArea0) != 0:
            Cui.CuiOpenArea(Cui.gpc_info)
        if Cui.CuiAreaExists({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION},
                             Cui.gpc_info, Cui.CuiArea1) != 0:
            Cui.CuiOpenArea(Cui.gpc_info)
        
        Cui.CuiDisplayObjects(Cui.gpc_info,Cui.CuiArea0,Cui.CrewMode,Cui.CuiShowAll)
        Cui.CuiDisplayFilteredObjects(Cui.gpc_info,Cui.CuiArea1,Cui.CrrMode,"trip_in_planning_area.sel",1)
        Cui.CuiUnmarkAllLegs(Cui.gpc_info,Cui.CuiArea0, 'window')
        Cui.CuiUnmarkAllLegs(Cui.gpc_info,Cui.CuiArea1, 'window')
        
    def show_and_clear(self):
        """
        Run show all area modes in all windows (make sure all ravetbales are loaded)
        Then clear all windows
        """
        tmp_macro = RowsShowAllAndClearTmpMacro()
        self.set_macro(tmp_macro.generate_tmp())
        PM.PlayMacroFile(self.macro) 
        self.reset_areas()
        del tmp_macro

    def find_and_display_1st_match_crew_leg(self, leg_filter=(), area=Cui.CuiArea0):
        """
        Find 1 crew and display crew and zoom to matched leg matching leg_filter tuple 
        """
        import carmensystems.studio.gui.private.Zoom as Zoom
        Cui.CuiDisplayObjects(Cui.gpc_info,area,Cui.CrewMode,Cui.CuiShowAll)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
        default_bag = R.context('default_context').bag()
        for roster_bag in default_bag.iterators.roster_set():
            for leg_bag in roster_bag.iterators.leg_set(where=leg_filter, sort_by='leg.%start_utc%'):
                start = leg_bag.leg.start_utc()
                end = leg_bag.leg.end_utc()
                leg_id = str(leg_bag.leg_identifier())
                crew = str(leg_bag.crew.id())
                self.log('Found crew leg to zoom %s (crew=%s, start=%s, end=%s)'%(leg_id, crew, str(start), str(end)))
                self.display_crews([crew], area)
                #Zoom.zoomArea(area, start, end)
                return (leg_id, crew)
        self.fail('Unable to find any crew legs matching %s'%leg_filter)
        
    def find_and_display_1st_match_trip_leg(self, leg_filter=(), area=Cui.CuiArea1):
        """
        Find 1 trip and display crew and zoom to matched leg matching leg_filter tuple 
        """
        import carmensystems.studio.gui.private.Zoom as Zoom
        Cui.CuiDisplayObjects(Cui.gpc_info,area,Cui.CrrMode,Cui.CuiShowAll)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
        default_bag = R.context('default_context').bag()
        for trip_bag in default_bag.iterators.trip_set(sort_by='trip.%start_utc%'):
            for leg_bag in trip_bag.iterators.leg_set(where=leg_filter):
                start = leg_bag.trip.start_utc()
                end = leg_bag.trip.end_utc()
                leg_id = str(leg_bag.leg_identifier())
                trip = str(leg_bag.crr_identifier())
                self.log('Found trip leg to zoom %s (trip=%s, start=%s, end=%s)'%(leg_id, trip, str(start), str(end)))
                self.display_trips([trip], area)
                #Zoom.zoomArea(area, start, end)
                return (leg_id,trip)
        self.fail('Unable to find any trip legs matching %s'%leg_filter)

    def display_trips(self, trips, area=Cui.CuiArea1):
        """
        Show trips in window
        """
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, area,
                                   Cui.CrrMode, Cui.CrrMode, trips)
        shown_trip = Cui.CuiGetTrips(Cui.gpc_info, area, "window")
        self.failIf(len(shown_trip) < 1,'Could not show trip %s'%trips)
        
        
    def mark_trip(self, trip, area=Cui.CuiArea1):
        """
        Mark trip with crr_identifier trip
        """
        mark_leg_bypass = {
            'FORM': 'form_mark_crr_filter',
            'FL_TIME_BASE': 'RDOP',
            'FILTER_MARK': 'Trip',
            'CRC_VARIABLE_0': 'crr_identifier',
            'CRC_VALUE_0': trip,
            'OK': ''
            }
        
        Cui.CuiMarkCrrsWithFilter(mark_leg_bypass,
                                   Cui.gpc_info, area, 0)
            
        marked_trip = Cui.CuiGetTrips(Cui.gpc_info, area, "marked")
        self.log('Marked trip %s'%marked_trip)
        self.failIf(len(marked_trip) < 1,'Could not mark trip %s'%trip)


    def select_trip(self, trip, area=Cui.CuiArea1):
        """
        Set trip with crr_identifier trip as selection object
        """
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrrMode, trip)
        v = Variable.Variable("")
        selected_object = Cui.CuiGetSelectionObject(Cui.gpc_info, area, 0, v)
        self.log("Selected trip %s"%v.value)
        self.failIf(v.value == "",'Could not select trip %s'%trip)
        
    def select_crew(self, crew, area=Cui.CuiArea0):
        """
        Set crew with crew_id crew as selection object
        """
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, crew)
        v = Variable.Variable("")
        selected_object = Cui.CuiGetSelectionObject(Cui.gpc_info, area, 0, v)
        self.log("Selected crew %s"%v.value)
        self.failIf(v.value == "",'Could not select crew %s'%crew)
        
    def display_crews(self, crews, area=Cui.CuiArea0):
        """
        Display crew in list crews
        """
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, area,
                                   Cui.CrewMode, Cui.CrewMode, crews)
        shown_crew = Cui.CuiGetCrew(Cui.gpc_info, area, "window")
        self.failIf(len(shown_crew) < 1,'Could not show crew %s'%crews)
        
        
    def mark_crew(self, crew, area=Cui.CuiArea0):
        """
        Mark crew with crew_id crew
        """
        mark_leg_bypass = {
            'FORM': 'form_mark_crew_member_filter',
            'FL_TIME_BASE': 'RDOP',
            'FILTER_MARK': 'CREW',
            'CRC_VARIABLE_0': 'crew.%id%',
            'CRC_VALUE_0': crew,
            'OK': ''}
        Cui.CuiMarkCrewsWithFilter(mark_leg_bypass,
                                   Cui.gpc_info, area, 0)
            
        marked_crew = Cui.CuiGetCrew(Cui.gpc_info, area, "MarkedLeft")
        self.log('Marked crew %s'%marked_crew)
        self.failIf(len(marked_crew) < 1,'Could not mark crew %s'%crew)

    def select_leg(self, leg, area=Cui.CuiArea0):
        """
        Set leg with leg_identifer=leg as selection object
        """
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, leg)
        v = Variable.Variable("")
        selected_object = Cui.CuiGetSelectionObject(Cui.gpc_info, area, 0, v)
        self.log("Selected leg  %s"%v.value)
        self.failIf(v.value == "",'Could not select  leg %s'%leg)
        
    def mark_leg(self, leg, area=Cui.CuiArea1):
        """
        Mark leg  with leg_identifier leg
        """
        mark_leg_bypass = {
            'FORM': 'form_mark_leg_filter',
            'FL_TIME_BASE': 'RDOP',
            'FILTER_MARK': 'LEG',
            'CRC_VARIABLE_0': 'leg_identifier',
            'CRC_VALUE_0':leg,
            'OK': ''
            }
        
        Cui.CuiMarkLegsWithFilter(mark_leg_bypass,
                                   Cui.gpc_info, area, 0)
            
        marked_leg = Cui.CuiGetLegs(Cui.gpc_info, area, "marked")
        self.log('Marked leg  %s'%marked_leg)
        self.failIf(len(marked_leg) < 1,'Could not mark leg %s'%leg)   
        
    def display_random_crew(self, area=Cui.CuiArea0):
        """
        Display a random crew in window
        """
        crew =  self.get_random_crew()
        self.display_crews([crew], area)
        return crew

    
    def get_random_crew(self):
        """
        Get a random crew from model
        """
        import random
        crew = [crew.id for crew in modelserver.TableManager.instance().table('crew')]
        ix = int(len(crew)*random.random())
        return crew[ix]



class FullGuiTest(GuiTest):
    """
    Macros defined in end of this file
    """

        
    def setUp(self):
        GuiTest.setUp(self)
        tmp_macro = ResetSelectFormTmpMacro()
        PM.PlayMacroFile(tmp_macro.generate_tmp())
        self.crew = self.get_random_crew()

    # disable main test
    def testRun(self):
        pass
    #Test not working   
    #def testN2225SelectCrewCommandLine(self):
    #    self.assertTrue(self.crew is not None, 'No selected crew')
    #    self.assertTrue(self.is_tracking(),'Testcase only avalilable in tracking')
    #    tmp_macro = SelectCrewCommandLineTmpMacro()
    #    self.set_macro(tmp_macro.generate_tmp({'CREW':self.crew, 'START_TIME':str(self._START_TIME)}))
    #    self.performance_test(self.run_impl)


    def testN2219ShowRosters(self):
        tmp_macro = ShowRosterTmpMacro()
        self.set_macro(tmp_macro.generate_tmp())
        self.performance_test(self.run_impl)
    
    def testN2221Scroll50Row(self):
        tmp_macro = Scroll50RostersTmpMacro()
        self.set_macro(tmp_macro.generate_tmp({'START_TIME':str(self._START_TIME)}))
        self.performance_test(self.run_impl)
    
 
    def testN2222ShowTrips(self):
        tmp_macro = ShowTripsTmpMacro()
        self.set_macro(tmp_macro.generate_tmp())
        self.performance_test(self.run_impl)    

    def testN2223ShowRotations(self):
        tmp_macro = ShowRotationsTmpMacro()
        self.set_macro(tmp_macro.generate_tmp())
        self.performance_test(self.run_impl)
        
    def testN2224MarkAll(self):
        tmp_macro = MarkLegsTmpMacro()
        self.set_macro(tmp_macro.generate_tmp({'VAR0':'leg.code',
                                               'VAL0':'*'}))
        self.performance_test(self.run_impl)
        
    def testN2226SelectCrewFromForm(self):
        self.assertTrue(self.crew is not None, 'No selected crew')
        tmp_macro = SelectCrewFromFormTmpMacro()
        self.set_macro(tmp_macro.generate_tmp({'CRR_CREW_ID':self.crew}))
        self.performance_test(self.run_impl)
        
    #Test not working
    #def testN2227SelectStandbysCommandLine(self):
    #    self.assertTrue(self.is_tracking(),'Testcase only avalilable in tracking')
    #    tmp_macro = SelectStandbysCommandLineTmpMacro()
    #    self.set_macro(tmp_macro.generate_tmp({'TIME':str(self._START_TIME)[0:5]}))
    #    self.performance_test(self.run_impl)
        
    def testN2228SelectStandbysMiniSelection(self):
        tmp_macro = SelectTaskCodeMiniSelection()
        self.set_macro(tmp_macro.generate_tmp({'DATE1':str(self._START_TIME)[0:9],
                                               'DATE2':str(self._END_TIME)[0:9],
                                               'TASKCODE':'STANDBY'}))
        self.performance_test(self.run_impl)
        
    def testN2229ShowIllegalCrew(self):
        tmp_macro = ShowIllegalRosterTmpMacro()
        self.set_macro(tmp_macro.generate_tmp())
        self.performance_test(self.run_impl)
        
    def testN2230MarkTouchAirportLegsCPH(self):
        tmp_macro = MarkLegsTmpMacro()
        self.set_macro(tmp_macro.generate_tmp({'VAR0':'departure_airport_name',
                                               'VAL0':'CPH'}))
        self.performance_test(self.run_impl)
        
    def testN2231SelectTaskCodeVA(self):
        tmp_macro = MarkLegsTmpMacro()
        self.set_macro(tmp_macro.generate_tmp({'VAR0':'task.code',
                                               'VAL0':'VA'}))
        self.performance_test(self.run_impl)

    def tearDown(self):
        GuiTest.tearDown(self)
        del self
        
class  RaveTest(GuiTest):
    
    def setUp(self):
        GuiTest.setUp(self)
        self.show_and_clear()
        
    def testRaveKPIColors(self):
        tmp_macro = RavKPITmpMacro()
        self.set_macro(tmp_macro.generate_tmp({'OPT1':'No',
                                               'OPT2':'No',
                                               'OPT3':'No',
                                               'OPT4':'No',
                                               'OPT5':'Yes',
                                               'FILE_NAME':'RaveKPIColors.txt'}))
        self.performance_test(self.run_impl)

    def testRaveKPILevels(self):
        tmp_macro = RavKPITmpMacro()
        self.set_macro(tmp_macro.generate_tmp({'OPT1':'Yes',
                                               'OPT2':'No',
                                               'OPT3':'No',
                                               'OPT4':'No',
                                               'OPT5':'No',
                                               'FILE_NAME':'RaveKPILevels.txt'}))
        self.performance_test(self.run_impl)

    def testRaveKPIRudobs(self):
        tmp_macro = RavKPITmpMacro()
        self.set_macro(tmp_macro.generate_tmp({'OPT1':'No',
                                               'OPT2':'No',
                                               'OPT3':'No',
                                               'OPT4':'Yes',
                                               'OPT5':'No',
                                               'FILE_NAME':'RaveKPIRudobstxt'}))
        self.performance_test(self.run_impl)

    def testRaveKPIRuleFailures(self):
        tmp_macro = RavKPITmpMacro()
        self.set_macro(tmp_macro.generate_tmp({'OPT1':'No',
                                               'OPT2':'Yes',
                                               'OPT3':'No',
                                               'OPT4':'No',
                                               'OPT5':'No',
                                               'FILE_NAME':'RaveKPIRuleFailures.txt'}))
        self.performance_test(self.run_impl)
        
    def testRaveKPIRules(self):  
        tmp_macro = RavKPITmpMacro()
        self.set_macro(tmp_macro.generate_tmp({'OPT1':'No',
                                               'OPT2':'No',
                                               'OPT3':'Yes',
                                               'OPT4':'No',
                                               'OPT5':'No',
                                               'FILE_NAME':'RaveKPIRules.txt'}))
        self.performance_test(self.run_impl)

    # disable main test
    def testRun(self):
        pass

###############  GUI MACROS (HERE BE DRAGONS) ##############################
class SelectCrewCommandLineTmpMacro(TU.TmpMacro):

    XML="""<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Commandline/SelectCrew"
         script="PythonEvalExpr(&quot;carmusr.tracking.CommandlineCommands.show_crew((Cui.CuiArea0, &apos;&apos;), (&apos;CREW&apos;, &apos;&apos;, &apos;r&apos;))&quot;)"
         level="0">
<CommandAttributes label="Commandline/SelectCrew"
                   script="PythonEvalExpr(&quot;carmusr.tracking.CommandlineCommands.show_crew((Cui.CuiArea0, &apos;&apos;), (&apos;CREW&apos;, &apos;&apos;, &apos;r&apos;))&quot;)"
                   level="0" returnVal="0" />
</Command>
</All>
"""
        
class SelectCrewFromFormTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Select/by Selection Mask..." script="CuiFilterObjects(gpc_info,CuiArea0,&quot;CrewFilter&quot;,0,0)" level="0">
<FormData name="form_crew_filter">
<FormInput  name="FCREW_ID" value="CRR_CREW_ID" />
<FormInput  name="OK" value="" type="Done" />
</FormData>
<CommandAttributes label="Select/by Selection Mask..."
                   script="CuiFilterObjects(gpc_info,CuiArea0,&quot;CrewFilter&quot;,0,0)" level="0" returnVal="0" />
</Command>
</All>
"""

class SelectStandbysCommandLineTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>    
<Command label="Commandline/SelectCrew"
         script="PythonEvalExpr(&quot;carmusr.tracking.CommandlineCommands.show_standby((Cui.CuiArea0, &apos;&apos;), (&apos;TIME&apos;, &apos;r&apos;))&quot;)" level="0">
<CommandAttributes label="Commandline/SelectCrew" script="PythonEvalExpr(&quot;carmusr.tracking.CommandlineCommands.show_standby((Cui.CuiArea0, &apos;&apos;), (&apos;TIME&apos;, &apos;r&apos;))&quot;)" level="0" returnVal="0" />
</Command>
</All>
"""
         
class SelectTaskCodeMiniSelection(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Select Rosters/Mini Select..." script="PythonEvalExpr(&quot;MiniSelect.startMiniSelectForm()&quot;)" level="0">
<AreaId id=""/>
<FormData name="Mini Select Form">
<FormInput  name="END_DATE" value="DATE2" />
<FormInput  name="START_DATE" value="DATE1" />
<FormInput  name="ACTIVITY_CODE" value="TASKCODE"  />
<FormInput  name="B_OK" value="" type="Done" />
</FormData>
<CommandAttributes label="Select Rosters/Mini Select..." script="PythonEvalExpr(&quot;MiniSelect.startMiniSelectForm()&quot;)" level="0" returnVal="0" />
</Command>

</All>

"""

class MarkLegsTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Select Rosters/by Selection Mask..." script="CuiFilterObjects(gpc_info,CuiArea0,&quot;CrewFilter&quot;,0,0)" level="0">
<FormData name="form_crew_filter">
<FormInput  name="FILTER_MARK" value="LEG"/>
<FormInput  name="CRC_VARIABLE_0" value="VAR0" />
<FormInput  name="CRC_VALUE_0" value="VAL0" />
<FormInput  name="OK" value="" type="Done" />
</FormData>
<CommandAttributes label="Select Rosters/by Selection Mask..."
                   script="CuiFilterObjects(gpc_info,CuiArea0,&quot;CrewFilter&quot;,0,0)"
                   level="0" returnVal="0" />
</Command>
</All>
"""

class ResetSelectFormTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Select Rosters/by Selection Mask..." script="CuiFilterObjects(gpc_info,CuiArea0,&quot;CrewFilter&quot;,0,0)" level="0">
<FormData name="form_crew_filter">
<FormInput  name="DEFAULT" value="" type="Done" />
<FormInput  name="OK" value="" type="Done" />
</FormData>
<CommandAttributes label="Select Rosters/by Selection Mask..."
                   script="CuiFilterObjects(gpc_info,CuiArea0,&quot;CrewFilter&quot;,0,0)"
                   level="0" returnVal="0" />
</Command>
</All>
"""
                   
class ShowIllegalRosterTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Window 1/Show Legal/Illegal/Show Illegal Rosters"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrewMode,CuiShowIllegal)" level="0">
<CommandAttributes label="Window 1/Show Legal/Illegal/Show Illegal Rosters"
                   script="CuiDisplayObjects(gpc_info,CuiArea0,CrewMode,CuiShowIllegal)" level="0" returnVal="0" />
</Command>
</All>
"""

class ShowRosterTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Window 1/Show Rosters"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrewMode,CuiShowAll)" level="0">
<CommandAttributes label="Window 1/Show Rosters"
                   script="CuiDisplayObjects(gpc_info,CuiArea0,CrewMode,CuiShowAll)" level="0" returnVal="0" />
</Command>
</All>
"""

class Scroll50RostersTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0">
<AreaId id=""/>
<Object position="" identity=""/>
<InteractionData type="SelectInteractor" id="">
<InteractionItem key="Area" value="0" />
<InteractionItem key="Elevation" value="60" />
<InteractionItem key="Operation" value="2" />
<InteractionItem key="Row" value="150" />
<InteractionItem key="Subwindow" value="2" />
<InteractionItem key="Time" value="START_TIME" />
</InteractionData>
<CommandAttributes label="Select"
                   script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0" returnVal="0" />
</Command>
</All>
"""

class ShowTripsTmpMacro(TU.TmpMacro):
    XML ="""<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Window 1/Show Trips"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrrMode,CuiShowAll)" level="0">
<CommandAttributes label="Window 1/Show Trips"
                   script="CuiDisplayObjects(gpc_info,CuiArea0,CrrMode,CuiShowAll)" level="0" returnVal="0" />
</Command>
</All>
"""

class ShowRotationsTmpMacro(TU.TmpMacro):
    XML ="""<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Window 1/Show Rotations" script="CuiDisplayObjects(gpc_info,CuiArea0,AcRotMode,CuiShowAll)" level="0">
<CommandAttributes label="Window 1/Show Rotations" script="CuiDisplayObjects(gpc_info,CuiArea0,AcRotMode,CuiShowAll)" level="0" returnVal="0" />
</Command>
</All>
"""

class RavKPITmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>

<Command label="Admin Tools/Rave KPI" script="CuiRaveKPI(gpc_info,6)" level="0">
<AreaId id=""/>
<FormData name="RAVE_KPI">
<FormInput  name="RUNS" value="3" height="1" length="5" style="1" type="String" width="5" />
<FormInput  name="RAVE_KPI_DOMAIN_ROSTERS" value="Yes" />
<FormInput  name="RAVE_KPI_LEVELS" value="OPT1" />
<FormInput  name="RAVE_KPI_EMPTY_ROSTERS" value="No" />
<FormInput  name="RAVE_KPI_RULE_FAILURES" value="OPT2"  />
<FormInput  name="RAVE_KPI_RULES" value="OPT3" />
<FormInput  name="RAVE_KPI_DOMAIN_TRIPS" value="No" />
<FormInput  name="RAVE_KPI_RUDOBS" value="OPT4"  />
<FormInput  name="RAVE_KPI_DOMAIN_ROTATIONS" value="No" />
<FormInput  name="RAVE_KPI_MAP_COLORS" value="OPT5" />
<FormInput  name="OK" value="" type="Done" />
</FormData>
<CommandAttributes label="Admin Tools/Rave KPI" script="CuiRaveKPI(gpc_info,6)" level="0" returnVal="0" />
</Command>

<Command label="Rave KPI/Save As..." script="GuiProcessInteraction(&quot;Text&quot;, &quot;Rave KPI&quot;)" level="0">
<FormData name="CRG_FILE_DIALOG">
<FormInput  name="CRG_SAVE_DIR" value="$CARMTMP/logfiles/" height="1" length="1199" style="1" type="String" width="60" />
<FormInput  name="CRG_SAVE_FILE" value="FILE_NAME" height="1" length="1199" style="1" type="String" width="60" />
<FormInput  name="OK" value="" type="Done" />
</FormData>
<InteractionData type="Text" id="Rave KPI">
<InteractionItem key="button" value="SAVE_AS" />
</InteractionData>
<CommandAttributes label="Rave KPI/Save As..." script="GuiProcessInteraction(&quot;Text&quot;, &quot;Rave KPI&quot;)" level="0" returnVal="0" />
</Command>
<Command label="Rave KPI/Close" script="GuiProcessInteraction(&quot;Text&quot;, &quot;Rave KPI&quot;)" level="0">
<AreaId id=""/>
<Object position="" identity=""/>
<InteractionData type="Text" id="Rave KPI">
<InteractionItem key="button" value="CLOSE" />
</InteractionData>
<CommandAttributes label="Rave KPI/Close" script="GuiProcessInteraction(&quot;Text&quot;, &quot;Rave KPI&quot;)" level="0" returnVal="0" />
</Command>
</All>
"""


class RowsShowAllAndClearTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Window 2/Remove" script="CuiRemoveArea(gpc_info,CuiArea1)" level="0">
<CommandAttributes label="Window 2/Remove" script="CuiRemoveArea(gpc_info,CuiArea1)" level="0" returnVal="0" />
</Command>
<Command label="Window 1/Properties..." script="CuiAreaProperties(gpc_info,CuiArea0)" level="0">
<FormData name="AreaSetup">
<FormInput  name="NUMBER_OF_ROWS" value="25" />
<FormInput  name="ROW_MENU" value="Number of" />
<FormInput  name="ROW_HEIGHT" value="25" />
<FormInput  name="OK" value="" type="Done" />
</FormData>
<CommandAttributes label="Window 1/Properties..."
                   script="CuiAreaProperties(gpc_info,CuiArea0)" level="0" returnVal="0" />
</Command>

<Command label="Window 1/Show Rosters"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrewMode,CuiShowAll)" level="0">
<CommandAttributes label="Window 1/Show Rosters"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrewMode,CuiShowAll)" level="0" returnVal="0" />
</Command>

<Command label="Window 1/Show Trips"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrrMode,CuiShowAll)" level="0">
<CommandAttributes label="Window 1/Show Trips"
                   script="CuiDisplayObjects(gpc_info,CuiArea0,CrrMode,CuiShowAll)" level="0" returnVal="0" />
</Command>

<Command label="Window 1/Show Rotations"
         script="CuiDisplayObjects(gpc_info,CuiArea0,AcRotMode,CuiShowAll)" level="0">
<CommandAttributes label="Window 1/Show Rotations"
                   script="CuiDisplayObjects(gpc_info,CuiArea0,AcRotMode,CuiShowAll)" level="0" returnVal="0" />
</Command>

<Command label="Window 1/Show Legal/Illegal/Show Legal Rosters"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrewMode,CuiShowLegal)" level="0">
<CommandAttributes label="Window 1/Show Legal/Illegal/Show Legal Rosters"
                   script="CuiDisplayObjects(gpc_info,CuiArea0,CrewMode,CuiShowLegal)"
                   level="0" returnVal="0" />
</Command>
<Command label="Window 1/Show Legal/Illegal/Show Legal Trips"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrrMode,CuiShowLegal)" level="0">
<CommandAttributes label="Window 1/Show Legal/Illegal/Show Legal Trips"
                   script="CuiDisplayObjects(gpc_info,CuiArea0,CrrMode,CuiShowLegal)" level="0" returnVal="0" />
</Command>
<Command label="Window 1/Show Legal/Illegal/Show Legal Rotations"
         script="CuiDisplayObjects(gpc_info,CuiArea0,AcRotMode,CuiShowLegal)" level="0">
<CommandAttributes label="Window 1/Show Legal/Illegal/Show Legal Rotations"
                   script="CuiDisplayObjects(gpc_info,CuiArea0,AcRotMode,CuiShowLegal)" level="0" returnVal="0" />
</Command>
<Command label="Window 1/Show Legal/Illegal/Show Illegal Rosters"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrewMode,CuiShowIllegal)" level="0">
<CommandAttributes label="Window 1/Show Legal/Illegal/Show Illegal Rosters"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrewMode,CuiShowIllegal)" level="0" returnVal="0" />
</Command>

<Command label="Window 1/Show Legal/Illegal/Show Illegal Trips"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrrMode,CuiShowIllegal)" level="0">
<CommandAttributes label="Window 1/Show Legal/Illegal/Show Illegal Trips"
         script="CuiDisplayObjects(gpc_info,CuiArea0,CrrMode,CuiShowIllegal)" level="0" returnVal="0" />
</Command>

<Command label="Window 1/Show Legal/Illegal/Show Illegal Rotations"
         script="CuiDisplayObjects(gpc_info,CuiArea0,AcRotMode,CuiShowIllegal)" level="0">

<CommandAttributes label="Window 1/Show Legal/Illegal/Show Illegal Rotations"
                   script="CuiDisplayObjects(gpc_info,CuiArea0,AcRotMode,CuiShowIllegal)" level="0" returnVal="0" />
</Command>

<Command label="Window 1/Clear" script="CuiClearArea(gpc_info,CuiArea0)" level="0">
<CommandAttributes label="Window 1/Clear" script="CuiClearArea(gpc_info,CuiArea0)" level="0" returnVal="0" />
</Command>

</All>
"""



#####################################################################
