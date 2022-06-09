'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import os
import commands

class data_001_compdays_reset(DaveTestFixture):
    """
    Tests Compdays
    """
    
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("NotMigrated")
    def __init__(self):
        pass
    
    def test_001_compdays_reset(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/salary_batch.sh RESET"

        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')
        
        for line in script_output:
            if "Error" in line or "error" in line:
                self.fail(line)
        pass

    def test_002_compdays_f31(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/salary_batch.sh F31"

        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')
        
        for line in script_output:
            if "Error" in line or "error" in line:
                self.fail(line)
        pass

    def test_003_compdays_f3s(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/salary_batch.sh F3S"

        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')
        
        for line in script_output:
            if "Error" in line or "error" in line:
                self.fail(line)
        pass

    def test_004_compdays_f7gain(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/salary_batch.sh F7GAIN"

        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')
        
        for line in script_output:
            if "Error" in line or "error" in line:
                self.fail(line)
        pass

    def test_005_compdays_f33gain(self):
        scriptfile = os.getenv("CARMUSR")+"/bin/salary_batch.sh F33GAIN -a "+commands.getoutput("date +%d%b%Y --date \"1 month\"")+" -l "+commands.getoutput("date +%d%b%Y --date \"4 month\"")

        script_output = commands.getoutput(scriptfile)
        script_output = script_output.split('\n')

        for line in script_output:
            print line
            if "Error" in line or "error" in line:
                self.fail(line)
        pass
