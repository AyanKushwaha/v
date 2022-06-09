from carmtest.framework import *
import os
import Cui

class tracking_001_MenuCommandsExt(TestFixture):
    "Menu Command ZoomOut"
    
    @REQUIRE("PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)

    def test_001_ZoomOut(self):
        from MenuCommandsExt import Zoom
        
        st, et = self.rave().eval('pp_start_time', 'pp_end_time')
        
        zoomStr = Zoom.ZoomOut()
        if zoomStr is not None:
            self.fail(zoomStr)
        
        logfile = open(os.getenv("LOG_FILE"))
        
        if 'MenuCommandsExt.Zoom.ZoomOut: (Overrides sys.) Zoom to pp = [%s .. %s]' % (st,et) not in logfile.read():
                self.fail("'MenuCommandsExt.Zoom.ZoomOut: (Overrides sys.) Zoom to pp = [%s .. %s]' not found in logfile" % (st,et))
     
        logfile = None

class tracking_002_LegAuditTrail(TestFixture):
    "LegAuditTrail"
    
    @REQUIRE("PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        
    def test_001_LegAuditTrail(self):
        import carmusr.LegAuditTrail
        from carmusr.LegAuditTrail import Get
        import Cui

        for crewId in self.getCrew(max_crew=100):
            self.select(crew=crewId)
            for _,leg in self.getLegs('leg.%is_flight_duty%', eval=("leg_identifier",))[0]:
                Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.LegMode, str(leg))
                st = Get(Cui.CuiScriptBuffer)
                assert "Created by" in st, "Expected 'Created by' in the report"
                lines = st.split('\n')
                assert "Assigned to: %s" % crewId in lines[0], "Expected 'Assigned to: %s' in the beginning of the report" % crewId
                return
        self.dataError("No suitable legs found")

class tracking_003_TripTools(TestFixture):
    "TripTools"
    
    @REQUIRE("PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        
    def test_001_tripClean(self):
        from carmusr.tracking import TripTools
        import Cui
        
        for crewId in self.getCrew(max_crew=100):
            self.select(crew=crewId)

            for _,leg in self.getLegs('leg.%is_flight_duty%', eval=("leg_identifier",))[0]:
                Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.LegMode, str(leg))
                self.markLegs([leg], area=Cui.CuiScriptBuffer)

                marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiScriptBuffer)
                response = TripTools.tripClean(Cui.CuiScriptBuffer, marked_legs)
                assert response is None, "%s" % response
                return
        self.dataError("No suitable legs found")
   
class tracking_004_DeassignAssign(TestFixture):
    "Deassign and Assign"

    @REQUIRE("PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        self.crewId = 0
        self.deassigned_legId = 0
        self.deassigned_crrId = 0
        self.leg_start_utc = 0
        
    def test_001_deassign(self):
        from carmusr.tracking import Deassign

        for crewId in self.getCrew(max_crew=100):
            self.select(crew=crewId)
            for _,leg,leg_start_utc in self.getLegs('leg.%is_flight_duty%', eval=("leg_identifier", "leg.%start_utc%",))[0]:
                Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.LegMode, str(leg))
                self.markLegs([leg], area=Cui.CuiScriptBuffer)

                response = Deassign.deassign(Cui.CuiScriptBuffer)
                assert response is None, "%s" % response
                _,self.deassigned_legId, self.deassigned_crrId = self.getLegs('leg.%is_flight_duty%', eval=('leg_identifier', 'crr_identifier',))[0][0]
                
                self.select(crew=crewId)
                assert leg not in self.getLegs('leg.%is_flight_duty%', eval=('leg_identifier', 'leg.%start_utc%',))[0], "The selected leg was not deassigned"
                assert self.deassigned_legId in [id for id in Cui.CuiGetLegs(Cui.gpc_info,Cui.CuiArea1, "window")], "The selected leg was not found in the trip window"
                self.crewId = crewId
                self.leg_start_utc = leg_start_utc
                return
        self.dataError("No suitable legs found")
        
    def test_002_Assign(self):
        import carmusr.tracking.DragDrop as DnD

        if Cui.CuiGetAreaMode(Cui.gpc_info, Cui.CuiArea1) != Cui.CrrMode:
            Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea1, Cui.CrrMode, Cui.CuiShowAll)
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, Cui.CuiArea1, 'WINDOW')
            
        Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiArea1, Cui.CrrMode, str(self.deassigned_crrId))
        self.markLegs([self.deassigned_legId], area=Cui.CuiArea1)
        
        if self.isTracking():
            DnD.AssignMarkedTrips(Cui.CuiArea1, Cui.CuiArea0, str(self.deassigned_crrId), str(self.crewId), int(self.leg_start_utc), ctrlPressed=0, pos=None)
        else:
            Cui.CuiAssignCrrById(Cui.gpc_info, self.crewId, self.deassigned_crrId, 0)
        
        _,assigned_legId = self.getLegs('leg.%is_flight_duty%', eval=('leg_identifier',))[0][0]
        assert assigned_legId not in [id for id in Cui.CuiGetLegs(Cui.gpc_info,Cui.CuiArea1, "window")], "The selected leg was not assigned back to crew %s" % self.crewId