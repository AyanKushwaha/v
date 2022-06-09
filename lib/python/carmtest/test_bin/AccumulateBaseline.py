'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import os
import commands

class data_001_accumulate_baseline(DaveTestFixture):
    """
    Tests Accumulate baseline (daily)
    """
    
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("NotMigrated")
    def __init__(self):
        pass
    
    def test_001_accumulate_daily(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/accumulators/accumulateBaseline.sh 1JAN1986 RECALC DAILY"

        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')
        
        for line in script_output:
            if "Error" in line or "error" in line:
                self.fail(line)
        pass
