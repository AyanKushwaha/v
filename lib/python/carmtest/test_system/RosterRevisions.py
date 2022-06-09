'''
Created on May 7, 2010

@author: rickard
'''


from carmtest.framework import *


class system_001_LoadPublished(TestFixture):
    "Load published rosters"
    
    @REQUIRE("PlanLoaded","Tracking")
    def __init__(self):
        TestFixture.__init__(self)
        
    def setUp(self):
        self.type = 'PUBLISHED'

    def test_001_Load1(self):
        crew = list(self.getCrew(max_crew=1).keys())
        assert len(crew) == 1, "Incorrect number of crew"
        self._load(crew)

    def test_002_Load100(self):
        crew = list(self.getCrew(max_crew=100).keys())
        assert len(crew) == 100, "Incorrect number of crew"
        self._load(crew)

    @REQUIRE("ExtensiveTestsEnabled")
    def test_003_LoadAll(self):
        crew = list(self.getCrew().keys())
        self.log("Number of crew: %d" % len(crew))
        self._load(crew)
        
    def _load(self, crewlist):
        import Cui
        Cui.CuiLoadPublishedRosters(Cui.gpc_info, crewlist, self.type)
        
class system_002_LoadScheduled(system_001_LoadPublished):
    "Load scheduled rosters"
    
    def setUp(self):
        self.type = 'SCHEDULED'
        
class system_003_LoadInformed(system_001_LoadPublished):
    "Load informed rosters"
    
    def setUp(self):
        self.type = 'INFORMED'
        
        
class system_004_LoadDelivered(system_001_LoadPublished):
    "Load delivered rosters"
    
    def setUp(self):
        self.type = 'DELIVERED'
