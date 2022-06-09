'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *


class data_004_TruncateHistory(DaveTestFixture):
    """
    Runs database db truncate
    """
    
    def __init__(self):
        pass
    
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("DangerousDatabaseOperations")
    def test_001_Truncate(self):
        self.shellcommand("db truncate")
