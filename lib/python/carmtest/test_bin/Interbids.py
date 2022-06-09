'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import os
import commands


class data_001_Interbids(DaveTestFixture):
    """
    Tests Interbids
    """
    
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("NotMigrated")
    def __init__(self):
        pass
    
    def test_001_Interbids(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/bids/cmd_install_bids.sh -f /opt/Carmen/CARMTMP/ftp/in"
        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')

        for line in script_output:
            if "error" in line.lower():
                self.fail(line)

        pass
