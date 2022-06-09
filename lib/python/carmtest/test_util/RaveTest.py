"""
Test CrewMealFlightOwnerTest
"""


from carmtest.framework import *
from AbsTime import AbsTime
from utils.rave import RaveIterator
import utils.TimeServerUtils as TSU

udor = TSU.now_AbsTime().day_floor()
adep = "ARN"

class rave_001_Iterator(TestFixture):

    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)        

    def setUp(self):
        class MyDocs(RaveIterator):
            def __init__(self):
                fields = {
                    'typ': 'report_crewlists.%doc_typ%',
                    'subtype': 'report_crewlists.%doc_subtype%',
                }
                iterator = RaveIterator.times('report_crewlists.%document_count%')
                RaveIterator.__init__(self, iterator, fields)

        class MyCrew(RaveIterator):
            def __init__(self):
                fields = {
                    'id': 'report_crewlists.%crew_id%',
                    'gn': 'report_crewlists.%crew_gn%',
                    'sn': 'report_crewlists.%crew_sn%',
                }
                nextlevels = {'doc': MyDocs()}
                iterator = RaveIterator.iter('iterators.leg_set', where='fundamental.%is_roster%')
                RaveIterator.__init__(self, iterator, fields, nextlevels)

        class MyLegs(RaveIterator):
            def __init__(self):
                fields = {
                    'flight': 'report_crewlists.%leg_flight_name%',
                    'std': 'report_crewlists.%leg_std_utc%',
                }
                nextlevels = {'crew': MyCrew()}
                iterator = RaveIterator.iter('iterators.unique_leg_set',
                    where='leg.%%is_flight_duty%% and leg.%%udor%% = %s and leg.%%start_station%% = "%s"' % 
                        (udor, adep), 
                    sort_by='leg.%flight_name%')
                RaveIterator.__init__(self, iterator, fields, nextlevels)

        self.legs = MyLegs().eval('sp_crew')


    def test_001_length(self):
        print udor
        
        self.assertTrue(len(self.legs)>10, "Check that a number of legs exists")

    def test_002_iterate_1(self):
        for leg in self.legs:
            for crew in leg.chain('crew'):
                for doc in crew.chain('doc'):
                    self.assertTrue(len(doc.typ)>0, "Check document type, %s" % (doc.typ))
                    self.assertTrue(len(doc.subtype)>0, "Check document sub type, %s" % (doc.subtype))


    def test_003_index_access(self):        
        self.assertTrue(len(self.legs[4].flight)>1, "Check index access")
        

    

