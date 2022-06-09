#

#
__version__ = "$Revision: 1.5 $"
"""
<module name>
Module for doing:
<xyz>
@date:16Mar2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import os
import sys
import traceback
import Cui

import AbsTime
import RelTime

import carmensystems.rave.api as R
import Errlog
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
from carmtest.GuiTests import GuiTest 
# Change here if macro-time changes!

import carmusr.rostering.Publish as Publish
import carmusr.training_attribute_handler as Training   

class TestPublish(Publish.RosterPublish):
    """
    Class that performs a full roster publish, except that it will always pass the roster check.
    If there is any ambiguity in tagging instructors, the instructor will not be tagged and
    his crew id will be logged. One should always inspect the log afterwards
    """
    def __init__(self):
        Publish.RosterPublish.__init__(self)

    def checkRosters(self):
        ok_to_publish, crew_structs, crew_messages = Publish.rosters_ok_for_publish(self.currentArea,
                                                                                    self.start,
                                                                                    self.end)
        self.crew_structs = crew_structs
        self.crewList = [crew.crewid  for crew in crew_structs]
        return True, ''

    def displayFinishedOKMessage(self):
        pass

    def handleContinueMessage(self, message=''):
        return True

    def splitPACTsAtPeriodEnd(self):
        Publish.RosterPublish.splitPACTsAtPeriodEnd(self)
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        Publish.merge_pacts_in_period(self.currentArea)
        self._log("Merging PACT:s in period")
        Publish.timer("Merging PACTS")

    def tagInstructors(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        Training.set_instructor_tag(mode='PUBLISH',area=self.currentArea, flags = Training.SILENT_FORM)
        Publish.timer("Tag instructors")
        self._log("Tagged instructors")

#class RosterPublishTest(GuiTest):
#
#
#    def setUp(self):
#        GuiTest.setUp(self)
#        self._publisher = TestPublish()
#      
#            
#    def run_impl(self):
#        self._publisher.publish()
