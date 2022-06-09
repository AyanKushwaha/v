'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *


class data_001_Connectivity(DaveTestFixture):
    """
    Tests schema connectivity.
    """
    
    def __init__(self):
        pass
    
    def test_001_Connection(self):
        assert self.sqlRow("SELECT 1 FROM DUAL")[0] == 1, "'SELECT 1 FROM DUAL' did not return 1"
    
    def test_002_Schema(self):
        ct =  self.sqlRow("SELECT COUNT(*) FROM dave_revision")[0]
        print "dave_revision has %d rows" % ct
        assert ct > 100, "Invalid dave_revision count"
