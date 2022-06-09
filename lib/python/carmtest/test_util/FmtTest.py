"""
Test CrewMealFlightOwnerTest
"""


from carmtest.framework import *
from AbsTime import AbsTime
from utils.fmt import CHR, INT, DATE, CellOverFlowError

class Test_fmt(TestFixture):
    "Fmt test"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_01_chr(self):
        """ Testing CHR """
        class AClass:
            def __str__(self):
                return 'ABCDEFG'

        self.assertEqual('AB  ', CHR(4, 'AB'))
        self.assertEqual('ABCD', CHR(4, 'ABCD'))
        self.assertEqual('ABCD', CHR(4, 'ABCDE'))
        self.assertEqual('ABCD', CHR(4, 'ABCDE'))
        self.assertEqual('ABCD', CHR(4, AClass()))
        self.assertEqual('1234', CHR(4, 12345))
        self.assertEqual('    ', CHR(4, None))

    def test_02_int(self):
        """ Testing INT """
        def testfault():
            return '1234' == INT(4, 12345)
        class AClass:
            def __int__(self):
                return 12
        self.assertEqual('0123', INT(4, 123))
        self.assertEqual('0000', INT(4, 'a'))
        self.assertEqual('1234', INT(4, 1234))
        self.failUnlessRaises(CellOverFlowError, testfault)
        self.assertEqual('0012', INT(4, AClass()))




