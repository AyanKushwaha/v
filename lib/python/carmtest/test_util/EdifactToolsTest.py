"""
Test Edifact tools
"""


from carmtest.framework import *
from AbsTime import AbsTime
import utils.edifact.tools as tools

class TestISO3166_1(TestFixture):
    "Test ISO3166_1"
    
    @REQUIRE("Tracking")
    @REQUIRE("NotMigrated")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001_alpha2to3(self):
        self.assertEqual(tools.ISO3166_1.alpha2to3('SE'), 'SWE')

    def test_002_alpha3to2(self):
        self.assertEqual(tools.ISO3166_1.alpha3to2('DNK'), 'DK')

    def test_003_failure(self):
        def failtest():
            x = tools.ISO3166_1.alpha3to2('BJS')
        self.assertRaises(Exception, failtest)


class TestDates(TestFixture):
    "Test dates"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def setUp(self):
        self.ts = AbsTime("20070809 13:12")

    def test_001_date(self):
        self.assertEqual(tools.edi_date(self.ts), '070809')

    def test_002_time(self):
        self.assertEqual(tools.edi_time(self.ts), '1312')

    def test_003_datetime(self):
        self.assertEqual(tools.edi_datetime(self.ts), '0708091312')


