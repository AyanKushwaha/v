"""
Test CrewInfoTest
"""

import tm
import utils.wave
import utils.TimeServerUtils as TSU

try:
    from AbsTime import AbsTime
    from RelTime import RelTime
except:
    def AbsTime(*args, **kwargs):
        raise "AbsTime is not supported"
    def RelTime(*args, **kwargs):
        raise "RelTime is not supported"

from carmtest.framework import *

class crew_001_CrewInfoTest(TestFixture):

    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        self.crewId = '85715'
        self.now = TSU.now_AbsTime()
        self.tmp_table_prefix = 'tmp_cbi_'

        utils.wave.init_wave_values()

        import carmusr.crewinfo.CrewInfo as CI
        CI.initiateTables(self.tmp_table_prefix, tablesToLoad="ALL", crewIdNonGlobal=self.crewId)

    def test_001_initiateTables(self):
        cxt = self.createContext()

        self.assertEquals(self.tmp_table_prefix + "crew_summary", cxt.tables.CrewSummary.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_address", cxt.tables.CrewAddress.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_contact", cxt.tables.CrewContact.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_contract", cxt.tables.CrewContract.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_document", cxt.tables.CrewDocument.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_employment", cxt.tables.CrewEmployment.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_not_fly_with", cxt.tables.ProhibitedCrew.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_qualification", cxt.tables.CrewQualification.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_restriction", cxt.tables.CrewRestriction.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_seniority", cxt.tables.CrewSeniority.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_profile", cxt.tables.CrewProfile.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_qual_acqual", cxt.tables.CrewQualAcqual.tableName)
        self.assertEquals(self.tmp_table_prefix + "crew_restr_acqual", cxt.tables.CrewRestAcQual.tableName)
        self.assertEquals(self.tmp_table_prefix + "special_schedules", cxt.tables.CrewSpecSched.tableName)
    
    def test_002_CountAcQualsAt(self):
        cxt = self.createContext()
        q1 = self.create_crew_qual(cxt, 'ACQUAL', 'AH', '19980101', '19980228')
        q2 = self.create_crew_qual(cxt, 'ACQUAL', '37', '19980131', '19980220')
        q3 = self.create_crew_qual(cxt, 'ACQUAL', '38', '19980210', '19980220')
        q4 = self.create_crew_qual(cxt, 'ACQUAL', 'A3', '19980220', '19980227')
        q5 = self.create_crew_qual(cxt, 'ACQUAL', 'A4', '19980225', '19980226')
         
        t = cxt.tables.CrewQualification
        self.assertEquals(0, t.countAcQualsAt(AbsTime('19971231')))
        self.assertEquals(1, t.countAcQualsAt(AbsTime('19980101')))
        self.assertEquals(1, t.countAcQualsAt(AbsTime('19980130')))
        self.assertEquals(2, t.countAcQualsAt(AbsTime('19980131')))
        self.assertEquals(2, t.countAcQualsAt(AbsTime('19980210')), '37 and 38 treated as same qual.')
        self.assertEquals(3, t.countAcQualsAt(AbsTime('19980220')))
        self.assertEquals(2, t.countAcQualsAt(AbsTime('19980221')))
        self.assertEquals(2, t.countAcQualsAt(AbsTime('19980225')), 'A3 and A4 treated as same qual.')
        self.assertEquals(2, t.countAcQualsAt(AbsTime('19980226')))
        self.assertEquals(2, t.countAcQualsAt(AbsTime('19980227')))
        self.assertEquals(1, t.countAcQualsAt(AbsTime('19980228')))

    def test_003_CrewMainCategory(self):
        cxt = self.createContext()
        mainCat = cxt.crewMainCategory(self.now)
        self.assertEquals('C', mainCat)

    def test_004_ChangeCrew(self):
        old_crew = self.crewId
        self.crewId = '15418'
        cxt = self.createContext()
        mainCat = cxt.crewMainCategory(self.now)
        self.crewId = old_crew
        self.assertEquals('F', mainCat)

    def test_005_ValidContract(self):
        cxt = self.createContext()
        contract = cxt.tables.CrewContract.validate(self.now)
        self.assertEquals('', contract)

    def test_006_EmploymentContractMatch(self):
        cxt = self.createContext()
        
        import carmusr.crewinfo.CrewInfo as CI
        res = CI.validateMismatch(cxt.tables.CrewEmployment, cxt.tables.CrewContract)
        self.assertEquals("", res)
        
    def createContext(self):
        import carmusr.crewinfo.CrewInfoTables as CIT
        cxt = CIT.CrewInfoContext.create(self.now, self.crewId, self.tmp_table_prefix)
        
        return cxt

    def create_crew_qual(self, cxt, qualtype, qualsubtype, validfrom, validto, acstring=None):
        row = cxt.tables.CrewQualification.createRow(self.now)
        row.qual = tm.TM.crew_qualification_set.getOrCreateRef((qualtype, qualsubtype))
        row.validfrom = AbsTime(validfrom)
        row.validto = AbsTime(validto)
        row.acstring = acstring
        return row
