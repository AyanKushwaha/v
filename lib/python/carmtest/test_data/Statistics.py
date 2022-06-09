'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *


class data_003_Statistics(DaveTestFixture):
    """
    Runs database statistics and verifies the result.
    """
    
    def __init__(self):
        pass
    
    @REQUIRE("ExtensiveTestsEnabled")
    def test_001_TableStatistics(self):
        self.shellcommand("db tablestats")
    
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("DangerousDatabaseOperations")
    def test_002_SchemaStatistics(self):
        self.shellcommand("db schemastats")
