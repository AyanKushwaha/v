"""
Test CrewTraining
"""

import tm
import utils.wave

from carmtest.framework import *

class crew_001_CrewTraining(TestFixture):

    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        self.crewId = '15418'
        self.tmp_table_prefix = "tmp_ctl_"

        utils.wave.init_wave_values()

    def test_001_initiate_tables(self):
        import carmusr.CrewTraining as CT
        CT.setCrew(True, self.crewId)

        self.assertEquals(self.tmp_table_prefix + "form_info", CT.FormInfoTable._name)
        self.assertEquals(self.tmp_table_prefix + "crew_summary", CT.CrewInfoTable._name)
        self.assertEquals(self.tmp_table_prefix + "log", CT.TrainingLogTable._name)
        self.assertEquals(self.tmp_table_prefix + "sys", CT.SystemTable._name)
        self.assertEquals(self.tmp_table_prefix + "landing", CT.LandingTable._name)
        self.assertEquals(self.tmp_table_prefix + "need", CT.NeedTable._name)
        self.assertEquals(self.tmp_table_prefix + "rows", CT.NeedRowTable._name)
        self.assertEquals(self.tmp_table_prefix + "valid_docno", CT.ValidDocno._name)
        self.assertEquals(self.tmp_table_prefix + "document", CT.DocumentTable._name)
        self.assertEquals(self.tmp_table_prefix + "rehearse", CT.RehearseTable._name)        
        
    def test_002_switch_crew(self):
        cid = '23456'

        import carmusr.CrewTraining as CT
        CT.setCrew(True, cid)
        table = self.table("tmp_ctl_crew_summary")
        for row in table:
            self.assertEquals(row.crew_id, cid)


