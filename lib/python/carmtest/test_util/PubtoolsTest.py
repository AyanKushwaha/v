"""
Test CrewMealFlightOwnerTest
"""


from carmtest.framework import *
from AbsTime import AbsTime
from utils.airport_tz import Airport



from AbsTime import AbsTime
from tm import TM
from utils import time_util
from utils import pubtools


class TestCopyTags(TestFixture):
    "Copy tags test"

    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)        
    
    # type, pubstart, pubend, pubcid
    orig_data = (
        ("DELIVERED", AbsTime(2008, 10, 30, 23, 0), AbsTime(2008, 11, 30, 23, 0), 66473),
        ("DELIVERED", AbsTime(2008, 11, 30, 23, 0), AbsTime(2008, 12, 31, 23, 0), 66477),
        ("DELIVERED", AbsTime(2008, 12, 31, 23, 0), AbsTime(2009, 1, 31, 23, 0), 1444819),
        ("INFORMED", AbsTime(2008, 10, 30, 23, 0), AbsTime(2008, 11, 30, 23, 0), 66473),
        ("INFORMED", AbsTime(2008, 11, 30, 23, 0), AbsTime(2008, 12, 31, 23, 0), 66477),
        ("INFORMED", AbsTime(2008, 12, 31, 23, 0), AbsTime(2009, 1, 31, 23, 0), 1444819),
        ("PUBLISHED", AbsTime(2008, 10, 30, 23, 0), AbsTime(2008, 11, 30, 23, 0), 66473),
        ("PUBLISHED", AbsTime(2008, 11, 30, 23, 0), AbsTime(2008, 12, 16, 23, 0), 1488702),
        ("PUBLISHED", AbsTime(2008, 12, 16, 23, 0), AbsTime(2008, 12, 17, 23, 0), 1491399),
        ("PUBLISHED", AbsTime(2008, 12, 17, 23, 0), AbsTime(2009, 1, 31, 23, 0), 1589996),
        ("PUBLISHED", AbsTime(2009, 3, 15, 23, 0), AbsTime(2009, 3, 25, 22, 59), 438479),
        ("PUBLISHED", AbsTime(2009, 3, 25, 23, 0), AbsTime(2009, 3, 29, 21, 59), 438479),
        ("SCHEDULED", AbsTime(2008, 10, 30, 23, 0), AbsTime(2008, 11, 30, 23, 0), 66473),
        ("SCHEDULED", AbsTime(2008, 11, 30, 23, 0), AbsTime(2008, 12, 31, 23, 0), 66477),
        ("SCHEDULED", AbsTime(2008, 12, 31, 23, 0), AbsTime(2009, 1, 31, 23, 0), 1444819),
    )

    crewid = "test_pubtools"

    def setUp(self):
        self.cref = TM.crew.create((self.crewid,))
        for rec in self.cref.referers('published_roster', 'crew'):
            rec.remove()
        for pubtype, pubstart, pubend, pubcid in self.orig_data:
            pubref = TM.publication_type_set[(pubtype,)]
            rec = TM.published_roster.create((pubstart, self.cref, pubref))
            rec.pubend = pubend
            rec.pubcid = pubcid
            rec.si = 'test_pubtools.py'

    def tearDown(self):
        for rec in self.cref.referers('published_roster', 'crew'):
            rec.remove()
        self.cref.remove()

    def get_data(self, pubtype):
        L = []
        for rec in self.cref.referers('published_roster', 'crew'):
            if rec.pubtype.id == pubtype:
                L.append((rec.pubstart, rec.pubend, rec.pubcid))
        L.sort()
        return self.make_printable(L)

    def make_printable(self, l):
        l.sort()
        return [(str(a), str(b), str(c)) for (a, b, c) in l]

    def test_001(self):
        pubtools.copy_tags(self.crewid, AbsTime(2008, 12, 16, 23, 0), AbsTime(2008, 12, 17, 23, 0),
                "PUBLISHED", ("INFORMED", "DELIVERED"))
        expected_result = self.make_printable([
            (AbsTime(2008, 10, 30, 23, 0), AbsTime(2008, 11, 30, 23, 0), 66473),
            (AbsTime(2008, 11, 30, 23, 0), AbsTime(2008, 12, 16, 23, 0), 66477),
            (AbsTime(2008, 12, 16, 23, 0), AbsTime(2008, 12, 17, 23, 0), 1491399),
            (AbsTime(2008, 12, 17, 23, 0), AbsTime(2008, 12, 31, 23, 0), 66477),
            (AbsTime(2008, 12, 31, 23, 0), AbsTime(2009, 1, 31, 23, 0), 1444819),
        ])
        self.assertEqual(self.get_data("INFORMED"), expected_result)
        self.assertEqual(self.get_data("DELIVERED"), expected_result)
        self.assertEqual(self.get_data("SCHEDULED"), self.make_printable([
            (AbsTime(2008, 10, 30, 23, 0), AbsTime(2008, 11, 30, 23, 0), 66473),
            (AbsTime(2008, 11, 30, 23, 0), AbsTime(2008, 12, 31, 23, 0), 66477),
            (AbsTime(2008, 12, 31, 23, 0), AbsTime(2009, 1, 31, 23, 0), 1444819),
        ]))

    def test_002(self):
        pubtools.copy_tags(self.crewid, AbsTime(2008, 12, 16, 0, 0), AbsTime(2008, 12, 17, 23, 0),
                "PUBLISHED", ("INFORMED", "DELIVERED"))
        expected_result = self.make_printable([
            (AbsTime(2008, 10, 30, 23, 0), AbsTime(2008, 11, 30, 23, 0), 66473),
            (AbsTime(2008, 11, 30, 23, 0), AbsTime(2008, 12, 16, 23, 0), 1488702),
            (AbsTime(2008, 12, 16, 23, 0), AbsTime(2008, 12, 17, 23, 0), 1491399),
            (AbsTime(2008, 12, 17, 23, 0), AbsTime(2008, 12, 31, 23, 0), 66477),
            (AbsTime(2008, 12, 31, 23, 0), AbsTime(2009, 1, 31, 23, 0), 1444819),
        ])
        self.assertEqual(self.get_data("INFORMED"), expected_result)
        self.assertEqual(self.get_data("DELIVERED"), expected_result)

    def test_003(self):
        pubtools.copy_tags(self.crewid, AbsTime(2009, 3, 1, 0, 0), AbsTime(2009, 5, 1, 0, 0),
                "PUBLISHED", ("INFORMED", "DELIVERED"))
        expected_result = self.make_printable([
            (AbsTime(2008, 10, 30, 23, 0), AbsTime(2008, 11, 30, 23, 0), 66473),
            (AbsTime(2008, 11, 30, 23, 0), AbsTime(2008, 12, 31, 23, 0), 66477),
            (AbsTime(2008, 12, 31, 23, 0), AbsTime(2009, 1, 31, 23, 0), 1444819),
            (AbsTime(2009, 3, 15, 23, 0), AbsTime(2009, 3, 25, 22, 59), 438479),
            (AbsTime(2009, 3, 25, 23, 0), AbsTime(2009, 3, 29, 21, 59), 438479),
        ])
        self.assertEqual(self.get_data("INFORMED"), expected_result)
        self.assertEqual(self.get_data("DELIVERED"), expected_result)

