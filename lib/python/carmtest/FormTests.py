#

#
__version__ = "$Revision: 1.4 $"
"""
WaveFormTests
Module for doing:
Testing wave forms
@date:17Nov2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import os
import sys
import traceback
import Cui
import Variable

import AbsTime
import RelTime

import carmensystems.rave.api as R
import Errlog

from carmtest.GuiTests import GuiTest
import tm
import carmtest.TestUtils as TU

import time

class CrewFormTest(GuiTest):

   
    def setUp(self):
        GuiTest.setUp(self)
        self.crew = self.get_random_crew()
        self.display_crews([self.crew])
        self.mark_crew(self.crew)
        self.select_crew(self.crew)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "object")
    
    def testRun(self):
        return #disable main test
    
    def tearDown(self):
        GuiTest.tearDown(self)
        Cui.CuiClearArea(Cui.gpc_info,Cui.CuiArea0)
        Cui.CuiClearArea(Cui.gpc_info,Cui.CuiArea1)

        
class CrewWaveFormTest(CrewFormTest):

    def testCrewNotification(self):
        import carmusr.tracking.CrewNotificationFunctions as CrewNotificationFunctions
        self.performance_test(CrewNotificationFunctions.startCrewNotification,args=['crew_object'])

   
   
     
"""
    def testAccountView(self):
        import carmusr.AccountView as AccountView
        self.performance_test(AccountView.start)
        
     def testRuleException(self):
        leg, crew = self.find_and_display_1st_match_crew_leg(leg_filter=('illegal_segment>0'))
        self.mark_crew(crew)
        self.select_crew(crew)
        import carmensystems.studio.rave.RuleException as RE 
        self.performance_test(RE.CheckIllegalities)

    def testAnnotations(self):
        import carmusr.tracking.Annotations as Annotations
        self.performance_test(Annotations.startAnnotations)
        
"""
"""           

"""       
"""
       def testViewNotification(self):
           import carmusr.tracking.CrewNotificationFunctions as CrewNotificationFunctions
           self.performance_test(CrewNotificationFunctions.startViewNotification,
                                 args=['crew_object'])
"""           
"""        
       def testCrewInfo(self):
           import carmusr.crewinfo.CrewInfo as CrewInfo
           self.performance_test(CrewInfo.startCrewInfoForm)
"""




"""
       def testCrewTraining(self):
           import carmusr.CrewTraining as CrewTraining
           self.performance_test(CrewTraining.start)
"""
"""        
       def testCrewBlockHours(self):
           import carmusr.CrewBlockHours as CrewBlockHours
           self.performance_test(CrewBlockHours.start)    

       def testStartTableEditor(self):
           import StartTableEditor
           self.performance_test(StartTableEditor.StartTableEditor,
                                 args=[[]]) #empty list for some reason
"""
       
        
class CrewCFHFormTest(CrewFormTest):

    def __init__(self, *args):
        CrewFormTest.__init__(self, *args)
        self.tmp_macro_class = SetAnnotationMacroTmp
    
    def setUp(self):
        CrewFormTest.setUp(self)
        print str(self._START_TIME)
        self.set_macro(self.get_macro_file({'DATE':str(self._START_TIME)[:9]}))
        
    def testBatchAnnotations(self):
        import carmusr.tracking.Annotations as Annotations
        self.performance_test(self.run_impl)



class LegFormTest(GuiTest):

    def __init__(self, *args):
        GuiTest.__init__(self, *args)
        self.leg_filter=()
        
    def setUp(self):
        GuiTest.setUp(self)
        self.leg_filter=('trip.%%start_utc%%>=%s'%str(self._START_TIME),
                         'task.%%code%% = "%s"'%'F')
        self.find_and_display_1st_match_crew_leg(self.leg_filter)
        self.leg_filter=('trip.%%start_utc%%>=%s'%str(self._START_TIME),
                         'trip.%has_active_flight% = true')
        self.find_and_display_1st_match_trip_leg(self.leg_filter)

    
class FindAssignableCrewTest(GuiTest):

    def __init__(self,*args):
        GuiTest.__init__(self, *args)
        
        self.tmp_macro_class =  FindAssignableCrewTMpMacro
        self.leg_filter = ('trip.%%start_hb%% >= %s'%self._START_TIME,
                           'trip.%%end_hb%% <= %s'%self._END_TIME,
                           'trip.%start_station% = "ARN"',
                           'trip.%qual% <> ""',
                           'trip.%region% <> ""',
                           'trip.%has_only_flight_duty%')
        self.trip = None
        
    def setUp(self):
        self.assertTrue(self.is_tracking(),'Testcase only avalilable in tracking')
        GuiTest.setUp(self)
        leg, self.trip = self.find_and_display_1st_match_trip_leg(self.leg_filter)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea1, "object")
        self.mark_trip(self.trip)
        self.select_trip(self.trip)
        
    def testRun(self):
        import carmusr.tracking.FindAssignableCrew as FindAssignableCrew
        self.performance_test(self.run_impl)
        
############################  GUI MACROS ################################
        
class SetAnnotationMacroTmp(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>

<Command label="Annotations/Set Annotation on Marked Crew..." script="PythonEvalExpr(&quot;Annotations.startBatchAnnotations()&quot;)" level="0">
<AreaId id=""/>
<FormData name="batch_annot_form">
<FormInput  name="ANN_CODE" value="JN - Yes to nightstop" height="1" length="36" menu="Codes;-- - Miscellaneous;FQ - Request for time-off;FX - Willing to sell freedays;IE - Wants to start earlier this day;J4 - Temporary special schedule;JN - Yes to nightstop;NS - No free days sale;OL - Wants to start later this day;RC - Resource Crew;SW - Willing to swap days with self" menuOnly="True" style="1" type="String" width="20" />
<FormInput  name="ANN_TEXT" value="TEST" height="1" length="200" style="1" type="String" width="50" />
<FormInput  name="ANN_START" value="DATE" height="1" length="11" style="1" type="Date" width="11" />
<FormInput  name="ANN_END" value="DATE" height="1" length="11" style="1" type="Date" width="11" />
<FormInput  name="B_OK" value="" type="Done" />
</FormData>
<CommandAttributes label="Annotations/Set Annotation on Marked Crew..." script="PythonEvalExpr(&quot;Annotations.startBatchAnnotations()&quot;)" level="0" returnVal="0" />
</Command>

</All>
"""

class FindAssignableCrewTMpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Find Assignable Crew..." script="PythonEvalExpr(&quot;FindAssignableCrew.findAssignableCrew()&quot;)" level="0">
<AreaId id=""/>
<FormData name="Find Assignable Crew">
<FormInput  name="C8_VALUE" value="True" height="1" length="-1" menu=";True;False" menuOnly="True" style="2" type="Toggle" width="7" />
<FormInput  name="C8_LABEL" value="Day off" height="1" length="0" style="10" type="String" width="4" />
<FormInput  name="B_OK" value="" type="Done" />
</FormData>
<FormData name="MESSAGE_BOX">
<FormInput  name="OK" value="" type="Done" />
</FormData>
<CommandAttributes label="Find Assignable Crew..." script="PythonEvalExpr(&quot;FindAssignableCrew.findAssignableCrew()&quot;)" level="0" returnVal="0" />
</Command>
</All>
"""
##############################################
