'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import os
import commands


class data_001_CMP_Revision(DaveTestFixture):
    """
    Tests CMP Revision for Manpower
    """
    
    @REQUIRE("DangerousDatabaseOperations")
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("NotMigrated")
    def __init__(self):
        pass
    
    def test_001_CMP_Revision(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/cmp_revision.sh"
        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')

        for line in script_output:
            if "error" in line.lower():
                self.fail(line)

        pass
