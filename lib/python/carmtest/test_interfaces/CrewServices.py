'''
Created on Mar 22, 2010

@author: rickard
'''

from carmtest.framework import *
import sys

class interfaces_001_CrewBasic(TestFixture):
    "CrewBasic report"
    
    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        
    def setUp(self):
        self.queryTime = self.raveExpr("fundamental.%pp_start%")
        
    def test_001_report(self):
        self.empNo = self.getCrew(crewemployment=True,date=self.queryTime,max_crew=1).values()[0].extperkey
        assert self.empNo, "Did not find a crew"
        import report_sources.report_server.rs_crewbasic as r
        ret = r.generate("CrewBasic", self.empNo, str(self.queryTime), "Y", "Y")
        assert len(ret) == 2, "Expected tuple of length 2"
        reportDict = ret[0][0]
        assert "content" in reportDict, "Expected dictionary with 'content' element"
        content = reportDict["content"]
        assert "<requestName>CrewBasic</requestName>" in content, "Expected CrewBasic report"
        assert "<empno>%s</empno>" % self.empNo in content, "Expected employee nr %s in report" % self.empNo
        
    def test_002_badrequest(self):
        import report_sources.report_server.rs_crewbasic as r
        ret = r.generate("CrewBasic", "666", str(self.queryTime), "Y", "Y")
        assert len(ret) == 2, "Expected tuple of length 2"
        reportDict = ret[0][0]
        assert "content" in reportDict, "Expected dictionary with 'content' element"
        content = reportDict["content"]
        assert "<statusText><![CDATA[Crew not found.]]></statusText>" in content, "Expected 'crew not found' in message"
        
            

class interfaces_002_CrewRoster(TestFixture):
    "CrewRoster report"
    
    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        
    def setUp(self):
        self.startDate = self.raveExpr("fundamental.%pp_start%")
        self.endDate = self.raveExpr("fundamental.%pp_end%")
        
    def test_001_report(self):
        self.empNo = self.getCrew(crewemployment=True,date=self.startDate,max_crew=1).values()[0].extperkey
        assert self.empNo, "Did not find a crew"
        import report_sources.report_server.rs_crewroster as r
        ret = r.generate("CrewRoster", self.empNo, "N", "N", "N", "N", "N", str(self.startDate), str(self.endDate))
        assert len(ret) == 2, "Expected tuple of length 2"
        reportDict = ret[0][0]
        assert "content" in reportDict, "Expected dictionary with 'content' element"
        content = reportDict["content"]
        assert "<requestName>CrewRoster</requestName>" in content, "Expected CrewRoster report"
        assert "<empno>%s</empno>" % self.empNo in content, "Expected employee nr %s in report" % self.empNo
        
    def test_002_badrequest(self):
        import report_sources.report_server.rs_crewroster as r
        ret = r.generate("CrewRoster", "666", "N", "N", "N", "N", "N", str(self.startDate), str(self.endDate))
        assert len(ret) == 2, "Expected tuple of length 2"
        reportDict = ret[0][0]
        assert "content" in reportDict, "Expected dictionary with 'content' element"
        content = reportDict["content"]
        assert "<statusText><![CDATA[Crew not found.]]></statusText>" in content, "Expected 'crew not found' in message"
        

class interfaces_003_CrewLanding(TestFixture):
    "CrewLanding report"
    
    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        import MenuCommandsExt
        MenuCommandsExt.showCrewCrrs(planning_area_filter=True, remove_other_windows=True)
        
    def setUp(self):
        self.startDate = self.raveExpr("fundamental.%pp_start%")
        self.endDate = self.raveExpr("fundamental.%pp_end%")

    def test_001_report(self):
        self.empNo = self.getCrew(cat="FC", crewemployment=True, date=self.startDate, max_crew=100).keys()
        assert self.empNo, "Did not find a crew"
        import report_sources.report_server.rs_crewlanding as r
  
        for empNo in self.empNo:
            list = self.getLegs(('leg.%is_flight_duty%', 'leg.%is_active_flight%', 'leg.%start_date% > fundamental.%pp_start%', 'leg.%is_last_in_duty%', 'crr_crew_id = "%s"' % empNo),area=0, eval=("leg.%flight_id%", "leg.%start_date%", "leg.%start_station%", "leg.%end_station%",))[0]
            if len(list) > 0:
                _, self.flightId, self.originDate, self.depStation, self.arrStation = list[0]
                ret = r.generate(requestName="CrewLanding", flightId=self.flightId, originDate=AbsDate(self.originDate),
                                 depStation=self.depStation, arrStation=self.arrStation, empno=empNo)
                break
        assert len(list) > 0, "Did not find a suitable crew"
        assert len(ret) == 2, "Expected tuple of length 2"
        reportDict = ret[0][0]
        assert "content" in reportDict, "Expected dictionary with 'content' element"
        content = reportDict["content"]
        assert "<requestName>CrewLanding</requestName>" in content, "Expected CrewRoster report"
        assert " <uplinkMessage><![CDATA[Ok]]></uplinkMessage>" in content, "Expected uplinkMessage OK"
                        
    def test_002_cabincrew(self):
        import MenuCommandsExt
        MenuCommandsExt.showCrewCrrs(planning_area_filter=True, remove_other_windows=True)
        self.empNo = self.getCrew(cat="CC", crewemployment=True, date=self.startDate, max_crew=100).keys()
        assert self.empNo, "Did not find a crew"
        import report_sources.report_server.rs_crewlanding as r
  
        for empNo in self.empNo:
            list = self.getLegs(('leg.%is_flight_duty%', 'leg.%is_active_flight%', 'leg.%start_date% > fundamental.%pp_start%', 'leg.%is_last_in_duty%', 'crr_crew_id = "%s"' % empNo),area=0, eval=("leg.%flight_id%", "leg.%start_date%", "leg.%start_station%", "leg.%end_station%",))[0]
            if len(list) > 0:
                _, self.flightId, self.originDate, self.depStation, self.arrStation = list[0]
                ret = r.generate(requestName="CrewLanding", flightId=self.flightId, originDate=AbsDate(self.originDate),
                                 depStation=self.depStation, arrStation=self.arrStation, empno=empNo)
                break
        assert len(list) > 0, "Did not find a suitable crew"
        assert len(ret) == 2, "Expected tuple of length 2"
        reportDict = ret[0][0]
        assert "content" in reportDict, "Expected dictionary with 'content' element"
        content = reportDict["content"]
        assert  "<uplinkMessage><![CDATA[Crew %s not qualified to land this flight" % empNo in content, "Expected 'crew not qualified to land'"
        
