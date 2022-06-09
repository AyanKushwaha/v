'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import os
import commands


class data_001_Crewlog(DaveTestFixture):
    """
    Tests Crewlog
    """
    
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("NotMigrated")
    def __init__(self):
        pass
    
    def test_001_Crewlog(self):
        scriptfile = os.getenv("CARMSYS")+"/bin/carmrunner "+os.getenv("CARMUSR")+"/lib/python/utils/crewlog.py"
        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')

        for line in script_output:
            if "error" in line.lower():
                self.fail(line)
        pass


