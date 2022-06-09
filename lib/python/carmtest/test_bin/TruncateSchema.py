'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import os
import commands

class data_001_truncate_schema(DaveTestFixture):
    """
    Tests Truncate schema
    """
    
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("DangerousDatabaseOperations")
    @REQUIRE("NotMigrated")
    def __init__(self):
        pass
    
    def test_001_truncate_schema(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/db/truncate_schema.sh"

        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')
        
        for line in script_output:
            if "Error" in line or "error" in line:
                self.fail(line)
        pass
