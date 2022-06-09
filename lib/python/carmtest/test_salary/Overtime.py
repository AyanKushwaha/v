'''
Created on Feb 11, 2010

@author: rickard
'''

from carmtest.framework import *

import csv
import os
import Cui
from tm import TM
        
class salary_001_OvertimeSalaryFile(TestFixture):
    "Overtime salary files"
    
    @REQUIRE("PlanLoaded","Tracking")
    def __init__(self):
        TestFixture.__init__(self)
        self._salaryFile = None
        self._newSalaryFile = None
        self._crewlist = []
        
    def setUp(self):
        pass

        
    def tearDown(self):
        pass
        
    def test_001_CreateOvertimeFile(self):
        "Create Overtime test file (CSV)"
        self._salaryFile = self.createSalaryFile()

        if not os.path.exists(self._salaryFile):
            self.fail("The expected salary file was not generated")
        
        for line in csv.DictReader(open(self._salaryFile, 'r')):
            crew = int(line['Extperkey'])
            assert crew > 10000 and crew < 100000, "Invalid crew empno"
            self._crewlist.append(str(crew))
        pass
    
    def test_010_ExcludeCrew(self):
        "CR388: Exclude crew from salary files"
        empno = self._crewlist[0]

        self.excludeCrew(empno, AbsTime("1Jan2001"), AbsTime("1Jan2020"))

        self._newSalaryFile = self.createSalaryFile()
        
        if not os.path.exists(self._newSalaryFile):
            self.fail("The expected salary file was not generated")
        
        newCrewlist = []
        for line in csv.DictReader(open(self._newSalaryFile, 'r')):
            newCrewlist.append(line['Extperkey'])
        
        assert empno not in newCrewlist, "Crew was not excluded"
        assert len([x for x in self._crewlist if x != empno]) == len(newCrewlist), "Too many crew excluded"
    
    def createSalaryFile(self, extsys="DK", salaryMonth=None):
        import salary.run
        if not salaryMonth:
            salaryMonth = self.raveExpr("salary.%salary_month_start%")
        return salary.run.job(salary.run.RunData(extsys=extsys,startdate=salaryMonth,exportformat="CSV"), export_run=True)
    
    def excludeCrew(self, empno, validfrom, validto):
        crewid = self.raveExpr('crew.%%extperkey_to_id%%("%s")' % empno)

        try:
            TM('rave_paramset_set', 'rave_string_paramset')
            r_ravevar = TM.rave_paramset_set[('salary_exclude_crew',)]
            r_basicdata = TM.rave_string_paramset.create((r_ravevar, crewid, validfrom))
            r_basicdata.validto = validto
            r_basicdata.si = "Overtime salary test run"

            Cui.CuiReloadTable('rave_string_paramset')
            Cui.CuiSyncModels(Cui.gpc_info)
        except:
            self.log("Failed to insert crew to exclude from salary file")


class Planningtest(TestFixture):
    "Planning test"
    
    @REQUIRE("Planning")
    def __init__(self):
        TestFixture.__init__(self)
        
    def setUp(self):
        self.log("Setting myself up!")
        
    def tearDown(self):
        self.log("Tearing myself down!")
        
    def testMyself1(self):
        self.log("I will succeed")

    def testMyself2(self):
        assert 1==2, "I fail to compute"
        
#class salary_004_Sometest(TestFixture):
#    @REQUIRE("WeirdThing")
#    def __init__(self):
#        TestFixture.__init__(self)
