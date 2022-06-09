"""
Test CrewBlockHoursTest
"""

import tm
import utils.wave
import utils.TimeServerUtils as TSU

from carmtest.framework import *

class crew_001_CrewBlockHoursTest(TestFixture):

    @REQUIRE("Tracking", "PlanLoaded")
    @REQUIRE("NotMigrated")
    def __init__(self):
        TestFixture.__init__(self)
        self.crewId = '28052'
        self.now = TSU.now_AbsTime()
        self.tmp_table_prefix = "tmp_cbh_"

        utils.wave.init_wave_values()

    def test_001_initiate_tables(self):
        import carmusr.CrewBlockHours as CBH
        CBH.cbh.initiate_tables()

        self.assertEquals(self.tmp_table_prefix + "crew_details", CBH.cbh.th_details.table._name)
        self.assertEquals(self.tmp_table_prefix + "acc_table", CBH.cbh.th_acc.table._name)
        self.assertEquals(self.tmp_table_prefix + "form_info", CBH.cbh.th_forminfo.table._name)
        self.assertEquals(self.tmp_table_prefix + "stat", CBH.cbh.th_stat.table._name)

    def test_002_populate_tables(self):
        import carmusr.CrewBlockHours as CBH
        CBH.cbh.initiate_tables()
        cid = '23456'
        res = '23456 (23456)'

        CBH.cbh.get_new_crew(cid)
        #print "***", dir(CBH.cbh.th_details.table)
        self.assertEquals(CBH.cbh.th_details.table[(0,)].empno, res)

        
