'''
Created on Feb 11, 2010

@author: rickard
'''

from carmtest.framework import *
import os
import csv
try:
    from salary import run
except:
    pass

class salary_001_RunOVERTIME(TestFixture):
    "Run: OVERTIME"
    
    @REQUIRE("PlanLoaded","Tracking")
    def __init__(self):
        TestFixture.__init__(self)
        self.startDate = self.raveExpr('fundamental.%pp_start%')
        self.endDate = self.startDate.addmonths(1)
        
    def setUp(self):
        self.runType = "OVERTIME"
        
    def test_001_OVERTIME_DK_run(self):
        "OVERTIME DK"
        assert self.runType
        self.extSys = "DK"
        self.run = run.run(run.RunData(fromStudio=True, extsys=self.extSys, admcode="N", runtype=self.runType,firstdate=self.startDate, lastdate=self.endDate))
        self.log("Run ID is %s" % self.run)
    
    def test_002_OVERTIME_DK_export(self):
        filename = run.export(run.RunData(runid=self.run, extsys=self.extSys, runtype=self.runType, exportformat="CSV"))
        assert "%s" % self.run in filename, "Expected salary run id '%s' in filename" % self.run
        assert "Extperkey,Type,Amount" in file(filename).read(), "Expected CSV header in file" 
        os.unlink(filename)
        
    def test_003_OVERTIME_NO_run(self):
        "OVERTIME NO"
        assert self.runType
        self.extSys = "NO"
        self.run = run.run(run.RunData(fromStudio=True, extsys=self.extSys, admcode="N", runtype=self.runType,firstdate=self.startDate, lastdate=self.endDate))
        self.log("Run ID is %s" % self.run)
    
    def test_004_OVERTIME_NO_export(self):
        filename = run.export(run.RunData(runid=self.run, extsys=self.extSys, runtype=self.runType, exportformat="CSV"))
        assert "%s" % self.run in filename, "Expected salary run id '%s' in filename" % self.run
        assert "Extperkey,Type,Amount" in file(filename).read(), "Expected CSV header in file" 
        os.unlink(filename)
        

