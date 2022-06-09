'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import os
import commands

class data_001_nightly_cleanups(DaveTestFixture):
    """
    Tests Nightly cleanups
    """
    
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("NotMigrated")
    def __init__(self):
        pass
    
    @REQUIRE("DangerousDatabaseOperations")
    def test_001_nightly_cleanups(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/db/nightly_cleanups.sh"

        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')
        
        for line in script_output:
            if "Error" in line or "error" in line:
                self.fail(line)
        pass
