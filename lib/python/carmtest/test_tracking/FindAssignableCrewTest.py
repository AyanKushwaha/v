'''
Created on Aug 16, 2012

@author: sven.olsson
'''
from carmtest.framework import *
import Cui
import carmusr.tracking.FindAssignableCrew as FAC
import carmusr.HelperFunctions as HF

class tracking_001_FindAssignableCrew(TestFixture):
    "Find assignable crew"
    
    @REQUIRE("PlanLoaded")
    @REQUIRE("ExtensiveTestsEnabled")
    def __init__(self):
        TestFixture.__init__(self)
        
    def test_001_FindAssignableCrew(self):
        pp_start, = self.rave().eval('pp_start_time')
        self.setNowTime(str(pp_start))
        counter = 0
        limit = 200
        for crewId in self.getCrew(max_crew=100):
            if counter == limit: break
            self.select(crew=crewId)
            for _,leg, start_utc, flight_nr in self.getLegs('leg.%is_flight_duty% and not leg.%is_deadhead% and leg.%start_utc% > fundamental.%now%', area=Cui.CuiScriptBuffer, eval=("leg_identifier","leg.%start_utc%", "leg.%flight_nr%"))[0]:
                Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.LegMode, str(leg))
                self.markLegs([leg], area=Cui.CuiScriptBuffer)
                FAC.findAssignableCrew(test_mode=True)
                counter += 1
                HF.unmarkAllLegs(area=Cui.CuiScriptBuffer)
                
                if counter == limit: break

        assert counter == limit, "Find Assignable Crew did only run %s times out of %s" % (counter, limit)