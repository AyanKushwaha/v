"""
Test CrewMealFlightOwnerTest
"""


from carmtest.framework import *
from AbsTime import AbsTime
from utils.airport_tz import Airport



class Airport_001_test(TestFixture):
    "Airport test"

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def setUp(self):
        self.winter_utc = (2007, 11, 3, 12, 0)
        self.winter = {
            'BJS': (2007, 11, 3, 20, 0),
            'CPH': (2007, 11, 3, 13, 0),
            'NRT': (2007, 11, 3, 21, 0),
            'OSL': (2007, 11, 3, 13, 0),
            'PEK': (2007, 11, 3, 20, 0),
            'PVG': (2007, 11, 3, 20, 0),
            'SHA': (2007, 11, 3, 20, 0),
            'STO': (2007, 11, 3, 13, 0),
            'SVG': (2007, 11, 3, 13, 0),
            'TYO': (2007, 11, 3, 21, 0),
        }
        self.summer_utc = (2007, 5, 3, 12, 0)
        self.summer = {
            'BJS': (2007, 5, 3, 20, 0),
            'CPH': (2007, 5, 3, 14, 0),
            'NRT': (2007, 5, 3, 21, 0),
            'OSL': (2007, 5, 3, 14, 0),
            'PEK': (2007, 5, 3, 20, 0),
            'PVG': (2007, 5, 3, 20, 0),
            'SHA': (2007, 5, 3, 20, 0),
            'STO': (2007, 5, 3, 14, 0),
            'SVG': (2007, 5, 3, 14, 0),
            'TYO': (2007, 5, 3, 21, 0),
        }

    def test_001_Winter(self):
        for ap in self.winter:
            airport = Airport(ap)
            self.assertEqual(airport.getUTCTime(AbsTime(*self.winter[ap])).split(), self.winter_utc)
            self.assertEqual(airport.getLocalTime(AbsTime(*self.winter_utc)).split(), self.winter[ap])

    def test_002_Summer(self):
        for ap in self.summer:
            airport = Airport(ap)
            self.assertEqual(airport.getUTCTime(AbsTime(*self.summer[ap])).split(), self.summer_utc)
            self.assertEqual(airport.getLocalTime(AbsTime(*self.summer_utc)).split(), self.summer[ap])


    

