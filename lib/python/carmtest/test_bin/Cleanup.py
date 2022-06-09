'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import os
import commands

class data_001_cleanup(DaveTestFixture):
    """
    Tests Cleanup
    """
    
    @REQUIRE("DangerousDatabaseOperations")
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("NotMigrated")
    def __init__(self):
        pass
    
    def test_001_cleanup(self):
        scriptfile = os.getenv("CARMSYS")+"/bin/carmrunner utils/cleanup.py"

        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')

        search_str = "Error"
        
        for line in script_output:
            if search_str in line:
                self.fail(line)

        pass
