'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import os
import commands

class data_001_update_crewuserfilter(DaveTestFixture):
    """
    Tests Update crewuserfilter
    """
    
    @REQUIRE("DangerousDatabaseOperations")
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("NotMigrated")
    def __init__(self):
        pass
    
    def test_001_update_crewuserfilter(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/updateCrewUserFilter.sh"

        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')

        search_str = "Error"
        
        for line in script_output:
            if search_str in line:
                self.fail(line)

        pass
