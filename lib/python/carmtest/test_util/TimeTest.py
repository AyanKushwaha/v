"""
Test CrewMealFlightOwnerTest
"""


from carmtest.framework import *

from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime

from utils import time_util


class time_001_IntervalBasic(TestFixture):
    "Time Interval basic "


    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def test_01(self):
        self.assertEqual(time_util.TimeInterval(None, None), 
                (AbsTime(1901, 1, 1, 0, 0), AbsTime(2099, 12, 30, 0, 0)))

    def test_02(self):
        self.assertEqual(time_util.TimeInterval(None, AbsTime(1965, 1, 10, 16, 31)), 
                (AbsTime(1901, 1, 1, 0, 0), AbsTime(1965, 1, 10, 16, 31)))

    def test_03(self):
        self.assertEqual(time_util.TimeInterval(AbsTime(1965, 1, 10, 16, 31), None), 
                (AbsTime(1965, 1, 10, 16, 31), AbsTime(2099, 12, 30, 0, 0)))

    def test_04(self):
        self.assertEqual(time_util.TimeInterval(AbsTime(2005, 8, 26, 15, 12),
            AbsTime(2002, 12, 4, 16, 30)), 
            (AbsTime(2002, 12, 4, 16, 30), AbsTime(2005, 8, 26, 15, 12)))

    def test_05(self):
        self.assertEqual(time_util.TimeInterval("26AUG2005 15:12", "4DEC2002 16:30"),
            (AbsTime(2002, 12, 4, 16, 30), AbsTime(2005, 8, 26, 15, 12)))

    def test_06(self):
        t = time_util.TimeInterval("26AUG2005 15:12", "4DEC2002 16:30")
        self.assertEqual(t.first, AbsTime(2002, 12, 4, 16, 30))
        self.assertEqual(t.last, AbsTime(2005, 8, 26, 15, 12))

    def test_07(self):
        t = time_util.TimeInterval("4DEC2002 15:00", "4DEC2002 16:30")
        self.assertEqual(t.adjoins(time_util.TimeInterval("4DEC2002 14:31", "4DEC2002 14:59")), False)
        self.assertEqual(t.adjoins(time_util.TimeInterval("4DEC2002 14:31", "4DEC2002 15:00")), True)
        self.assertEqual(t.adjoins(time_util.TimeInterval("4DEC2002 14:31", "4DEC2002 17:00")), True)
        self.assertEqual(t.adjoins(time_util.TimeInterval("4DEC2002 15:30", "4DEC2002 16:00")), True)
        self.assertEqual(t.adjoins(time_util.TimeInterval("4DEC2002 16:29", "4DEC2002 17:00")), True)
        self.assertEqual(t.adjoins(time_util.TimeInterval("4DEC2002 16:30", "4DEC2002 17:00")), True)
        self.assertEqual(t.adjoins(time_util.TimeInterval("4DEC2002 16:31", "4DEC2002 17:00")), False)

    def test_08(self):
        t = time_util.TimeInterval("4DEC2002 15:00", "4DEC2002 16:30")
        self.assertEqual(t.overlap(time_util.TimeInterval("4DEC2002 14:31", "4DEC2002 14:59")), 0)
        self.assertEqual(t.overlap(time_util.TimeInterval("4DEC2002 14:31", "4DEC2002 15:00")), 0)
        self.assertEqual(t.overlap(time_util.TimeInterval("4DEC2002 14:31", "4DEC2002 15:01")), 1)
        self.assertEqual(t.overlap(time_util.TimeInterval("4DEC2002 14:31", "4DEC2002 17:00")), 90)
        self.assertEqual(t.overlap(time_util.TimeInterval("4DEC2002 15:30", "4DEC2002 16:00")), 30)
        self.assertEqual(t.overlap(time_util.TimeInterval("4DEC2002 16:29", "4DEC2002 17:00")), 1)
        self.assertEqual(t.overlap(time_util.TimeInterval("4DEC2002 16:30", "4DEC2002 17:00")), 0)
        self.assertEqual(t.overlap(time_util.TimeInterval("4DEC2002 16:31", "4DEC2002 17:00")), 0)


class time_002_DateIntervalBasic(TestFixture):
    " Date interval basic"

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def test_01(self):
        self.assertEqual(time_util.DateInterval(None, None), 
                (AbsTime(1901, 1, 1, 0, 0), AbsTime(2099, 12, 30, 0, 0)))

    def test_02(self):
        self.assertEqual(time_util.DateInterval(None, AbsTime(1965, 1, 10, 16, 31)), 
                (AbsTime(1901, 1, 1, 0, 0), AbsTime(1965, 1, 11, 0, 0)))

    def test_03(self):
        self.assertEqual(time_util.DateInterval(AbsTime(1965, 1, 10, 16, 31), None), 
                (AbsTime(1965, 1, 10, 0, 0), AbsTime(2099, 12, 30, 0, 0)))

    def test_04(self):
        self.assertEqual(time_util.DateInterval(AbsTime(2005, 8, 26, 15, 12),
            AbsTime(2002, 12, 4, 16, 30)), 
            (AbsTime(2002, 12, 4, 0, 0), AbsTime(2005, 8, 27, 0, 0)))

    def test_05(self):
        self.assertEqual(time_util.DateInterval("26AUG2005 15:12", "4DEC2002 16:30"),
            (AbsTime(2002, 12, 4, 0, 0), AbsTime(2005, 8, 27, 0, 0)))

    def test_06(self):
        t = time_util.DateInterval("26AUG2005 15:12", "4DEC2002 16:30")
        self.assertEqual(t.first, AbsTime(2002, 12, 4, 0, 0))
        self.assertEqual(t.last, AbsTime(2005, 8, 27, 0, 0))

    def test_07(self):
        t = time_util.DateInterval("3DEC2002 15:00", "4DEC2002 16:30")
        self.assertEqual(t.adjoins(time_util.DateInterval("1DEC2002 14:31", "1DEC2002 14:59")), False)
        self.assertEqual(t.adjoins(time_util.DateInterval("1DEC2002 14:31", "2DEC2002 14:59")), True)
        self.assertEqual(t.adjoins(time_util.DateInterval("1DEC2002 14:31", "3DEC2002 15:00")), True)
        self.assertEqual(t.adjoins(time_util.DateInterval("1DEC2002 14:31", "5DEC2002 17:00")), True)
        self.assertEqual(t.adjoins(time_util.DateInterval("3DEC2002 15:30", "4DEC2002 16:00")), True)
        self.assertEqual(t.adjoins(time_util.DateInterval("4DEC2002 16:29", "4DEC2002 17:00")), True)
        self.assertEqual(t.adjoins(time_util.DateInterval("4DEC2002 16:30", "4DEC2002 17:00")), True)
        self.assertEqual(t.adjoins(time_util.DateInterval("5DEC2002 0:01", "6DEC2002 17:00")), True)
        self.assertEqual(t.adjoins(time_util.DateInterval("6DEC2002 0:01", "6DEC2002 17:00")), False)

    def test_08(self):
        t = time_util.DateInterval("3DEC2002 15:00", "4DEC2002 16:30")
        self.assertEqual(t.overlap(time_util.DateInterval("1DEC2002 14:31", "1DEC2002 14:59")), 0)
        self.assertEqual(t.overlap(time_util.DateInterval("1DEC2002 14:31", "2DEC2002 14:59")), 0)
        self.assertEqual(t.overlap(time_util.DateInterval("1DEC2002 14:31", "3DEC2002 15:00")), 1440)
        self.assertEqual(t.overlap(time_util.DateInterval("1DEC2002 14:31", "5DEC2002 17:00")), 2880)
        self.assertEqual(t.overlap(time_util.DateInterval("3DEC2002 15:30", "4DEC2002 16:00")), 2880)
        self.assertEqual(t.overlap(time_util.DateInterval("4DEC2002 16:29", "4DEC2002 17:00")), 1440)
        self.assertEqual(t.overlap(time_util.DateInterval("4DEC2002 16:30", "4DEC2002 17:00")), 1440)
        self.assertEqual(t.overlap(time_util.DateInterval("5DEC2002 0:00", "6DEC2002 17:00")), 0)
        self.assertEqual(t.overlap(time_util.DateInterval("5DEC2002 0:01", "6DEC2002 17:00")), 0)

class time_003_Overlap(TestFixture):
    "Overlap"
#          t1       t2 t3      t4
#     (A)  |--------|                       2007-01-10T10:10 - 2007-03-01T12:10
#                     |--------|            2007-03-05T13:59 - 2007-04-01T23:00
#
#     (B)  |----------|                     2007-01-10T10:10 - 2007-03-05T13:59
#                   |----------|            2007-03-01T12:10 - 2007-04-01T23:00
#
#     (C)  |-------------------|            2007-01-10T10:10 - 2007-04-01T23:00
#                   |-|                     2007-03-01T12:10 - 2007-03-05T13:59
#
#     (D)  |--------|                       2007-02-20T00:00 - 2007-02-21T00:00
#                   |---------|             2007-02-21T00:00 - 2007-02-22T00:00



    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def setUp(self):
        self.t1 = AbsTime(2007, 1, 10, 10, 10)
        self.t2 = AbsTime(2007, 3, 1, 12, 10)
        self.t3 = AbsTime(2007, 3, 5, 13, 59)
        self.t4 = AbsTime(2007, 4, 1, 23, 0)
        self.t5 = AbsTime(2007, 2, 20, 0, 0)
        self.t6 = AbsTime(2007, 2, 21, 0, 0)
        self.t7 = AbsTime(2007, 2, 22, 0, 0)

    def test_01(self): self.assertEqual(time_util.overlap(self.t1, self.t2, self.t3, self.t4), 0)
    def test_02(self): self.assertEqual(time_util.overlap(self.t1, self.t3, self.t2, self.t4), 5869)
    def test_03(self): self.assertEqual(time_util.overlap(self.t1, self.t4, self.t2, self.t3), 5869)
    def test_04(self): self.assertEqual(time_util.overlap(self.t3, self.t4, self.t1, self.t2), 0)
    def test_05(self): self.assertEqual(time_util.overlap(self.t2, self.t4, self.t1, self.t3), 5869)
    def test_06(self): self.assertEqual(time_util.overlap(self.t2, self.t3, self.t1, self.t4), 5869)
    def test_07(self): self.assertEqual(time_util.overlap(self.t5, self.t6, self.t6, self.t7), 0)



class time_004_DateInterval(TestFixture):
    "Date Interval"

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def setUp(self):
        self.t1 = AbsTime(2007, 1, 10, 10, 10)
        self.t2 = AbsTime(2007, 3, 1, 12, 10)
        self.t3 = AbsTime(2007, 3, 5, 13, 59)
        self.t4 = AbsTime(2007, 4, 1, 23, 00)

    def test_01(self):
        x = time_util.DateInterval(AbsTime(2007, 1, 10, 9, 5), AbsTime(2007, 1, 10, 23, 59))
        self.assertEqual(x.first, AbsTime(2007, 1, 10, 0, 0))
        self.assertEqual(x.last, AbsTime(2007, 1, 11, 0, 0))

    def test_02(self):
        x = time_util.DateInterval(AbsTime(2007, 1, 10, 9, 5), AbsTime(2007, 1, 10, 24, 0))
        self.assertEqual(x.last, AbsTime(2007, 1, 11, 0, 0))

    def test_03(self):
        x = time_util.DateInterval(AbsTime(2007, 1, 10, 9, 5), AbsTime(2007, 1, 11, 0, 2))
        self.assertEqual(x.last, AbsTime(2007, 1, 12, 0, 0))

    def test_04(self):
        self.assertEqual(time_util.DateInterval(self.t1, self.t3).overlap(time_util.DateInterval(self.t2, self.t4)), 7200)

    def test_05(self):
        self.assert_(time_util.DateInterval(self.t1, self.t3).adjoins(time_util.DateInterval(self.t2, self.t4)))

class time_005_IntervalSet(TestFixture):
    "Interval Set"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        


    def setUp(self):
        self.t1 = AbsTime(2007, 1, 10, 0, 0)
        self.t2 = AbsTime(2007, 1, 11, 0, 0)
        self.t3 = AbsTime(2007, 1, 12, 0, 0)
        self.t4 = AbsTime(2007, 1, 15, 0, 0)
        self.t5 = AbsTime(2007, 2, 20, 0, 0)
        self.t6 = AbsTime(2007, 2, 21, 0, 0)
        self.t7 = AbsTime(2007, 2, 22, 0, 0)
        self.t8 = AbsTime(2007, 2, 23, 0, 0)
        self.t9 = AbsTime(2007, 2, 24, 0, 0)
        self.t1t4 = time_util.DateInterval(self.t1, self.t4)
        self.t2t3 = time_util.DateInterval(self.t2, self.t3)
        self.t5t6 = time_util.DateInterval(self.t5, self.t6)
        self.t6t7 = time_util.DateInterval(self.t6, self.t7)
        self.t7t8 = time_util.DateInterval(self.t7, self.t8)
        self.t8t9 = time_util.DateInterval(self.t8, self.t9)

    def test_01(self):
        l = time_util.IntervalSet(self.t1t4)
        self.assertEqual(sorted(l), [self.t1, self.t4])

    def test_02(self):
        l = time_util.IntervalSet((self.t1t4, self.t2t3, self.t5t6, self.t6t7, self.t8t9))
        l.merge()
        self.assertEqual(sorted(l), [(self.t1, self.t4), (self.t5, self.t7), (self.t8, self.t9)])
        l.add(self.t7t8)
        l.merge()
        self.assertEqual(sorted(l), [(self.t1, self.t4), (self.t5, self.t9)])

class time_007_IntervalSetMethods(TestFixture):
    "Interval Set Methods"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        


    def setUp(self):
        self.s = time_util.IntervalSet
        self.i = time_util.Interval

    def t2i(self, t):
        return self.s([self.i(x, y) for x, y in t])

    def i2i(self, a, b):
        return self.s([self.i(a, b)])

    def test_isdisjoint_01(self):
        # isdisjoint
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        self.assertFalse(x.isdisjoint(i2i(1, 4)))
        self.assertTrue(x.isdisjoint(i2i(10, 12)))
        self.assertEqual(xorg, x)

    def test_issubset_01(self):
        # issubset
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        self.assertTrue(i2i(2, 3).issubset(x))
        self.assertTrue(i2i(6, 8).issubset(x))
        self.assertFalse(i2i(9, 10).issubset(x))
        self.assertTrue(x.issubset(x))
        self.assertEqual(xorg, x)

    def test_issubset_02(self):
        # <= 
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        self.assertTrue(i2i(2, 3) <= x)
        self.assertTrue(i2i(6, 8) <= x)
        self.assertFalse(i2i(9, 10) <= x)
        self.assertTrue(x <= x)
        self.assertEqual(xorg, x)

    def test_issubset_03(self):
        # < 
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        self.assertTrue(i2i(2, 3) < x)
        self.assertTrue(i2i(6, 8) < x)
        self.assertFalse(i2i(9, 10) < x)
        self.assertFalse(x < x)
        self.assertEqual(xorg, x)

    def test_issuperset_01(self):
        # issuperset
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        self.assertTrue(x.issuperset(i2i(2, 3)))
        self.assertTrue(x.issuperset(i2i(6, 8)))
        self.assertFalse(x.issuperset(i2i(9, 10)))
        self.assertTrue(x.issuperset(x))
        self.assertEqual(xorg, x)

    def test_issuperset_02(self):
        # >=
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        self.assertTrue(x >= i2i(2, 3))
        self.assertTrue(x >= i2i(6, 8))
        self.assertFalse(x >= i2i(9, 10))
        self.assertTrue(x >= x)
        self.assertEqual(xorg, x)

    def test_issuperset_03(self):
        # >
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        self.assertTrue(x > i2i(2, 3))
        self.assertTrue(x > i2i(6, 8))
        self.assertFalse(x > i2i(9, 10))
        self.assertFalse(x > x)
        self.assertEqual(xorg, x)

    def test_union_01(self):
        # union
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        self.assertEqual(x.union(i2i(1, 4)), self.t2i([(1, 4), (5, 9)]))
        self.assertEqual(x.union(i2i(9, 24)), self.t2i([(1, 3), (5, 24)]))
        self.assertEqual(xorg, x)

    def test_union_02(self):
        # |
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        self.assertEqual(x | i2i(1, 4), self.t2i([(1, 4), (5, 9)]))
        self.assertEqual(x | i2i(9, 24), self.t2i([(1, 3), (5, 24)]))
        self.assertEqual(xorg, x)

    def test_difference_01(self):
        # difference
        # 0        1         2         3         4         5         
        # 12345678901234567890123456789012345678901234567890123456879
        # xxxxxxxxx     xxxxxxxxxxxxxxx          xxxxxxxxxx
        #     yyyyyyyyyyyyy  yyyyy     yyyyy
        # rrrr             rr     rrrrr          rrrrrrrrrr
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(1, 5), (18, 20), (25, 30), (40, 50)])
        self.assertEqual(x.difference(y), r)
        self.assertEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_difference_02(self):
        # -
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(1, 5), (18, 20), (25, 30), (40, 50)])
        self.assertEqual(x - y, r)
        self.assertEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_symmetric_difference_01(self):
        # symmetric_difference
        # 0        1         2         3         4         5         
        # 12345678901234567890123456789012345678901234567890123456879
        # xxxxxxxxx     xxxxxxxxxxxxxxx          xxxxxxxxxx
        #     yyyyyyyyyyyyy  yyyyy     yyyyy
        # rrrr     rrrrr   rr     rrrrrrrrrr     rrrrrrrrrr
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(1, 5), (10, 15), (18, 20), (25, 35), (40, 50)])
        self.assertEqual(x.symmetric_difference(y), r)
        self.assertEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_symmetric_difference_02(self):
        # ^
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(1, 5), (10, 15), (18, 20), (25, 35), (40, 50)])
        self.assertEqual(x ^ y, r)
        self.assertEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_intersection_01(self):
        # intersection
        # 0        1         2         3         4         5         
        # 12345678901234567890123456789012345678901234567890123456879
        # xxxxxxxxx     xxxxxxxxxxxxxxx          xxxxxxxxxx
        #     yyyyyyyyyyyyy  yyyyy     yyyyy
        #     rrrrr     rrr  rrrrr                         
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(5, 10), (15, 18), (20, 25)])
        self.assertEqual(x.intersection(y), r)
        self.assertEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_intersection_02(self):
        # &
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(5, 10), (15, 18), (20, 25)])
        self.assertEqual(x & y, r)
        self.assertEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_update_01(self):
        # update
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        x.update(i2i(1, 4))
        self.assertEqual(x, self.t2i([(1, 4), (5, 9)]))
        x.update(i2i(9, 24))
        self.assertEqual(x, self.t2i([(1, 4), (5, 24)]))
        self.assertNotEqual(xorg, x)

    def test_update_02(self):
        # |=
        i2i = self.i2i
        x = self.t2i([(1, 3), (5, 9)])
        xorg = x.copy()
        x |= i2i(1, 4)
        self.assertEqual(x, self.t2i([(1, 4), (5, 9)]))
        x |= i2i(9, 24)
        self.assertEqual(x, self.t2i([(1, 4), (5, 24)]))
        self.assertNotEqual(xorg, x)

    def test_difference_update_01(self):
        # difference_update
        # 0        1         2         3         4         5         
        # 12345678901234567890123456789012345678901234567890123456879
        # xxxxxxxxx     xxxxxxxxxxxxxxx          xxxxxxxxxx
        #     yyyyyyyyyyyyy  yyyyy     yyyyy
        # rrrr             rr     rrrrr          rrrrrrrrrr
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(1, 5), (18, 20), (25, 30), (40, 50)])
        x.difference_update(y)
        self.assertEqual(x, r)
        self.assertNotEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_difference_update_02(self):
        # -=
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(1, 5), (18, 20), (25, 30), (40, 50)])
        x -= y
        self.assertEqual(x, r)
        self.assertNotEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_symmetric_difference_update_01(self):
        # symmetric_difference_update
        # 0        1         2         3         4         5         
        # 12345678901234567890123456789012345678901234567890123456879
        # xxxxxxxxx     xxxxxxxxxxxxxxx          xxxxxxxxxx
        #     yyyyyyyyyyyyy  yyyyy     yyyyy
        # rrrr     rrrrr   rr     rrrrrrrrrr     rrrrrrrrrr
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(1, 5), (10, 15), (18, 20), (25, 35), (40, 50)])
        x.symmetric_difference_update(y)
        self.assertEqual(x, r)
        self.assertNotEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_symmetric_difference_update_02(self):
        # ^=
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(1, 5), (10, 15), (18, 20), (25, 35), (40, 50)])
        x ^= y
        self.assertEqual(x, r)
        self.assertNotEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_intersection_update_01(self):
        # intersection_update
        # 0        1         2         3         4         5         
        # 12345678901234567890123456789012345678901234567890123456879
        # xxxxxxxxx     xxxxxxxxxxxxxxx          xxxxxxxxxx
        #     yyyyyyyyyyyyy  yyyyy     yyyyy
        #     rrrrr     rrr  rrrrr                         
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(5, 10), (15, 18), (20, 25)])
        x.intersection_update(y)
        self.assertEqual(x, r)
        self.assertNotEqual(xorg, x)
        self.assertEqual(yorg, y)

    def test_intersection_update_02(self):
        # &=
        x = self.t2i([(1, 10), (15, 30), (40, 50)])
        xorg = x.copy()
        y = self.t2i([(5, 18), (20, 25), (30, 35)])
        yorg = y.copy()
        r = self.t2i([(5, 10), (15, 18), (20, 25)])
        x &= y
        self.assertEqual(x, r)
        self.assertNotEqual(xorg, x)
        self.assertEqual(yorg, y)


class time_008_IntervalSetSplit(TestFixture):
    "Interval Set Split"


    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        


    def test_01(self):
        f = time_util.IntervalSet
        x = time_util.Interval
        a = f([x(1, 3), x(5, 20), x(30, 40)])
        b = f([x(2, 3), x(4, 6), x(15, 55)])
        a.split(b)
        self.assertEqual(a, f([x(1, 2), x(2, 3), x(5, 6), x(6, 15), x(15, 20), x(30, 40)]))
        self.assertEqual(b, f([x(2, 3), x(4, 5), x(5, 6), x(15, 20), x(20, 30), x(30, 40), x(40, 55)]))

    def test_02(self):
        f = time_util.IntervalSet
        x = time_util.Interval
        a = f([x(1, 20)])
        b = f([x(30, 90)])
        a.split(b)
        self.assertEqual(a, f([x(1, 20)]))
        self.assertEqual(b, f([x(30, 90)]))


class time_009_IntervalSetComplementI(TestFixture):
    "Interval Set Comp I"
    #           |=interval=============|
    #2 |--| |-|
    #3                                     |--| |-|
    #4      |------|x|--|x|-|xx|---------| |--|
    #5        |---------------------------|
    #6          xx|----|xxxxxxxxxxxxxxxx
    #7   |---|  xxxxxxxxxxxxxxxxxxxxxxxx  |---|
    
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    
    def setUp(self): 
        self.ref = 1, 900
        self.t1 = 10, 25
        self.t2 = 35, 40
        self.t3 = 50, 110
        self.t4 = 120, 170
        self.t5 = 180, 190
        self.t6 = 201, 300
        self.t7 = 350, 400
        self.t8 = 450, 600
        self.i_type = time_util.Interval
    
    def test_01(self):
        i = time_util.IntervalSet([
            self.i_type(*self.t1),
            self.i_type(*self.t2),
            self.i_type(*self.t4),
            self.i_type(*self.t5),
            self.i_type(*self.t6),
            self.i_type(*self.t7),
            self.i_type(*self.t8),
        ])
        i.complement()
        self.assertEqual(i, time_util.IntervalSet([
            self.i_type(self.t1[1], self.t2[0]),
            self.i_type(self.t2[1], self.t4[0]),
            self.i_type(self.t4[1], self.t5[0]),
            self.i_type(self.t5[1], self.t6[0]),
            self.i_type(self.t6[1], self.t7[0]),
            self.i_type(self.t7[1], self.t8[0]),
        ]))

class time_010_IntervalSetComplementT(TestFixture):
    "Interval Set Comp T"
    #           |=interval=============|
    #2 |--| |-|
    #3                                     |--| |-|
    #4      |------|x|--|x|-|xx|---------| |--|
    #5        |---------------------------|
    #6          xx|----|xxxxxxxxxxxxxxxx
    #7   |---|  xxxxxxxxxxxxxxxxxxxxxxxx  |---|
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    
    def setUp(self):
        self.ref = AbsTime(2007, 1, 1, 1, 1), AbsTime(2007, 1, 30, 15, 15)

        self.t1 = AbsTime(2006, 12, 24, 15, 0), AbsTime(2006, 12, 24, 16, 15)
        self.t2 = AbsTime(2006, 12, 25, 10, 10), AbsTime(2006, 12, 26, 14, 15)
        self.t3 = AbsTime(2006, 12, 25, 13, 13), AbsTime(2007, 1, 1, 15, 0)
        self.t4 = AbsTime(2007, 1, 12, 10, 10), AbsTime(2007, 1, 13, 14, 15)
        self.t5 = AbsTime(2007, 1, 16, 0, 0), AbsTime(2007, 1, 16, 16, 16)
        self.t6 = AbsTime(2007, 1, 20, 22, 0), AbsTime(2007, 2, 4, 4, 24)
        self.t7 = AbsTime(2007, 2, 5, 12, 45), AbsTime(2007, 2, 6, 6, 24)
        self.t8 = AbsTime(2007, 3, 12, 10, 0), AbsTime(2007, 3, 16, 12, 24)
        self.i_type = time_util.TimeInterval
    
    def test_01(self):
        i = time_util.IntervalSet([
            self.i_type(*self.t1),
            self.i_type(*self.t2),
            self.i_type(*self.t4),
            self.i_type(*self.t5),
            self.i_type(*self.t6),
            self.i_type(*self.t7),
            self.i_type(*self.t8),
        ])
        i.complement()
        self.assertEqual(i, time_util.IntervalSet([
            self.i_type(self.t1[1], self.t2[0]),
            self.i_type(self.t2[1], self.t4[0]),
            self.i_type(self.t4[1], self.t5[0]),
            self.i_type(self.t5[1], self.t6[0]),
            self.i_type(self.t6[1], self.t7[0]),
            self.i_type(self.t7[1], self.t8[0]),
        ]))

    def test_02(self):
        #           |=interval=============|
        #2 |--| |-|
        i = time_util.IntervalSet([
            self.i_type(*self.t1),
            self.i_type(*self.t2),
        ])
        i.complement(self.i_type(*self.ref))
        self.assertEqual(i, time_util.IntervalSet([self.i_type(*self.ref)]))

    def test_03(self):
        #           |=interval=============|
        #3                                     |--| |-|
        i = time_util.IntervalSet([
            self.i_type(*self.t7),
            self.i_type(*self.t8),
        ])
        i.complement(self.i_type(*self.ref))
        self.assertEqual(i, time_util.IntervalSet([self.i_type(*self.ref)]))

    def test_04(self):
        #           |=interval=============|
        #4      |------|x|--|x|-|xx|---------| |--|
        i = time_util.IntervalSet([
            self.i_type(*self.t3),
            self.i_type(*self.t4),
            self.i_type(*self.t5),
            self.i_type(*self.t6),
        ])
        i.complement(self.i_type(*self.ref))
        self.assertEqual(i, time_util.IntervalSet([
            self.i_type(self.t3[1], self.t4[0]),
            self.i_type(self.t4[1], self.t5[0]),
            self.i_type(self.t5[1], self.t6[0]),
        ]))

    def test_05(self):
        #           |=interval=============|
        #5        |---------------------------|
        i = time_util.IntervalSet([
            self.i_type(self.t2[0], self.t6[1])
        ])
        i.complement(self.i_type(*self.ref))
        self.assertEqual(i, time_util.IntervalSet([]))
        i = time_util.IntervalSet([
            self.i_type(*self.t1),
            self.i_type(self.t2[0], self.t6[1]),
            self.i_type(*self.t7),
        ])
        i.complement(self.i_type(*self.ref))
        self.assertEqual(i, time_util.IntervalSet([]))

    def test_06(self):
        #           |=interval=============|
        #6          xx|----|xxxxxxxxxxxxxxxx
        i = time_util.IntervalSet([
            self.i_type(*self.t4)
        ])
        i.complement(self.i_type(*self.ref))
        self.assertEqual(i, time_util.IntervalSet([
            self.i_type(self.ref[0], self.t4[0]),
            self.i_type(self.t4[1], self.ref[1]),
        ]))

    def test_07(self):
        #           |=interval=============|
        #7   |---|  xxxxxxxxxxxxxxxxxxxxxxxx  |---|
        i = time_util.IntervalSet([
            self.i_type(*self.t1),
            self.i_type(*self.t8),
        ])
        i.complement(self.i_type(*self.ref))
        self.assertEqual(i, time_util.IntervalSet([
            self.i_type(*self.ref),
        ]))

class time_011_IntervalSetComplementD(time_010_IntervalSetComplementT):
    "Interval Set Comp D"

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def setUp(self):
        time_010_IntervalSetComplementT.setUp(self)
        self.i_type = time_util.DateInterval

    def test_01(self):
        i = time_util.IntervalSet([
            self.i_type(*self.t1),
            self.i_type(*self.t2),
            self.i_type(*self.t4),
            self.i_type(*self.t5),
            self.i_type(*self.t6),
            self.i_type(*self.t7),
            self.i_type(*self.t8),
        ])
        i.complement()
        self.assertEqual(i, time_util.IntervalSet([
            self.i_type(AbsTime(2006, 12, 27, 0, 0), AbsTime(2007, 1, 12, 0, 0)),
            self.i_type(AbsTime(2007, 1, 14, 0, 0), AbsTime(2007, 1, 16, 0, 0)),
            self.i_type(AbsTime(2007, 1, 17, 0, 0), AbsTime(2007, 1, 20, 0, 0)),
            self.i_type(AbsTime(2007, 2, 7, 0, 0), AbsTime(2007, 3, 12, 0, 0)),
        ]))

    def test_04(self):
        #           |=interval=============|
        #4      |------|x|--|x|-|xx|---------| |--|
        i = time_util.IntervalSet([
            self.i_type(*self.t3),
            self.i_type(*self.t4),
            self.i_type(*self.t5),
            self.i_type(*self.t6),
        ])
        i.complement(self.i_type(*self.ref))
        self.assertEqual(i, time_util.IntervalSet([
            self.i_type(AbsTime(2007, 1, 2, 0, 0), AbsTime(2007, 1, 12, 0, 0)),
            self.i_type(AbsTime(2007, 1, 14, 0, 0), AbsTime(2007, 1, 16, 0, 0)),
            self.i_type(AbsTime(2007, 1, 17, 0, 0), AbsTime(2007, 1, 20, 0, 0)),
        ]))

    def test_06(self):
        #           |=interval=============|
        #6          xx|----|xxxxxxxxxxxxxxxx
        i = time_util.IntervalSet([
            self.i_type(*self.t4)
        ])
        i.complement(self.i_type(*self.ref))
        self.assertEqual(i, time_util.IntervalSet([
            self.i_type(AbsTime(2007, 1, 1, 0, 0),  AbsTime(2007, 1, 12, 0, 0)),
            self.i_type(AbsTime(2007, 1, 14, 0, 0), AbsTime(2007, 1, 31, 0, 0))
        ]))

    def test_07(self):
        #           |=interval=============|
        #6          xx|----|xxxxxxxxxxxxxxxx
        i = time_util.IntervalSet([
            self.i_type(*self.t4)
        ])
        j = time_util.IntervalSet([self.i_type(*self.ref)])
        i.split(j)
        x = j - i
        x.merge()
        self.assertEqual(x, time_util.IntervalSet([
            self.i_type(AbsTime(2007, 1, 1, 0, 0),  AbsTime(2007, 1, 12, 0, 0)),
            self.i_type(AbsTime(2007, 1, 14, 0, 0), AbsTime(2007, 1, 31, 0, 0))
        ]))

class time_012_IntervalSetDifferenceI(TestFixture):
    "Interval Set Diff T"

    #  |------------|      |------------------|         |------------|
    #        |---------------------|  |---|
    #  xxxxxx                       xx     xxx          xxxxxxxxxxxxxx

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    
    def setUp(self):
        self.s = [(1, 10), (15, 30), (40, 50)]
        self.o = [(5, 18), (20, 25), (30, 35)]
        self.i_type = time_util.Interval

    def test_01(self):
        i = time_util.IntervalSet([self.i_type(x, y) for x, y in self.s])
        j = time_util.IntervalSet([self.i_type(x, y) for x, y in self.o])
        z = time_util.IntervalSet(i)
        self.assertEqual(i.difference(j), 
            time_util.IntervalSet([self.i_type(1, 5), self.i_type(18, 20),
                self.i_type(25, 30), self.i_type(40, 50)]))
        self.assertEqual(i, z)

    def test_02(self):
        i = time_util.IntervalSet([self.i_type(x, y) for x, y in self.s])
        j = time_util.IntervalSet([self.i_type(x, y) for x, y in self.o])
        i.split(j)
        x = i - j
        x.merge()
        self.assertEqual(x,
            time_util.IntervalSet([self.i_type(1, 5), self.i_type(18, 20),
                self.i_type(25, 30), self.i_type(40, 50)]))


class time_013_OpenInterval(TestFixture):
    "Open interval"

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def setUp(self):
        self.f = time_util.OpenInterval
        self.hilo = self.f(10, 15)
        self.hi = self.f(None, 15)
        self.lo = self.f(10, None)
        self.open = self.f(None, None)

    def test_first(self):
        self.assertEqual(self.hilo.first, 10)
        self.assertEqual(self.hi.first, None)
        self.assertEqual(self.lo.first, 10)
        self.assertEqual(self.open.first, None)

    def test_last(self):
        self.assertEqual(self.hilo.last, 15)
        self.assertEqual(self.hi.last, 15)
        self.assertEqual(self.lo.last, None)
        self.assertEqual(self.open.last, None)

    def test_magnitude(self):
        def failing(a):
            return a.magnitude()
        self.assertEqual(self.hilo.magnitude(), 5)
        self.assertRaises(time_util.Infinity, failing, self.hi)
        self.assertRaises(time_util.Infinity, failing, self.lo)
        self.assertRaises(time_util.Infinity, failing, self.open)

    def test_includes(self):
        self.assertFalse(self.hilo.includes(9))
        self.assertTrue(self.hilo.includes(10))
        self.assertTrue(self.hilo.includes(12))
        self.assertTrue(self.hilo.includes(15))
        self.assertFalse(self.hilo.includes(16))

    def test_embraces(self):
        x = self.f
        self.assertTrue(self.hi.embraces(self.hilo))
        self.assertFalse(self.hilo.embraces(self.hi))
        self.assertTrue(self.hilo.embraces(self.hilo))
        self.assertTrue(self.open.embraces(self.hilo))
        self.assertTrue(self.open.embraces(self.hi))
        self.assertTrue(self.open.embraces(self.lo))
        self.assertTrue(x(1, 10).embraces(x(2, 8)))
        self.assertFalse(x(3, 8).embraces(x(2, 8)))

    def test_adjoins(self):
        x = self.f
        self.assertTrue(x(1, 3).adjoins(x(2, 3)))
        self.assertTrue(x(1, 3).adjoins(x(0, 1)))
        self.assertFalse(x(1, 3).adjoins(x(4, 5)))
        self.assertTrue(x(1, 3).adjoins(x(0, 6)))

    def test_overlaps(self):
        x = self.f
        self.assertTrue(x(1, 3).overlaps(x(2, 3)))
        self.assertFalse(x(1, 3).overlaps(x(0, 1)))
        self.assertFalse(x(1, 3).overlaps(x(4, 5)))
        self.assertTrue(x(1, 3).overlaps(x(0, 6)))

    def test_overlap(self):
        self.assertEqual(self.hilo.overlap(self.lo), 5)

    def test_hilo(self):
        x = self.f
        self.assertEqual(x(8, 17).overlap(self.hilo), 5)
        self.assertEqual(x(9, 17).overlap(self.hilo), 5)
        self.assertEqual(x(10, 17).overlap(self.hilo), 5)
        self.assertEqual(x(11, 17).overlap(self.hilo), 4)
        self.assertEqual(x(8, 15).overlap(self.hilo), 5)
        self.assertEqual(x(8, 14).overlap(self.hilo), 4)
        self.assertEqual(x(8, 13).overlap(self.hilo), 3)
        self.assertEqual(x(10, 13).overlap(self.hilo), 3)
        self.assertEqual(x(11, 13).overlap(self.hilo), 2)

    def test_hi(self):
        x = self.f
        self.assertEqual(x(8, 17).overlap(self.hi), 7)
        self.assertEqual(x(9, 17).overlap(self.hi), 6)
        self.assertEqual(x(10, 17).overlap(self.hi), 5)
        self.assertEqual(x(11, 17).overlap(self.hi), 4)
        self.assertEqual(x(8, 15).overlap(self.hi), 7)
        self.assertEqual(x(8, 14).overlap(self.hi), 6)
        self.assertEqual(x(8, 13).overlap(self.hi), 5)
        self.assertEqual(x(10, 13).overlap(self.hi), 3)
        self.assertEqual(x(11, 13).overlap(self.hi), 2)

    def test_lo(self):
        x = self.f
        self.assertEqual(x(8, 17).overlap(self.lo), 7)
        self.assertEqual(x(9, 17).overlap(self.lo), 7)
        self.assertEqual(x(10, 17).overlap(self.lo), 7)
        self.assertEqual(x(11, 17).overlap(self.lo), 6)
        self.assertEqual(x(8, 15).overlap(self.lo), 5)
        self.assertEqual(x(8, 14).overlap(self.lo), 4)
        self.assertEqual(x(8, 13).overlap(self.lo), 3)
        self.assertEqual(x(10, 13).overlap(self.lo), 3)
        self.assertEqual(x(11, 13).overlap(self.lo), 2)

    def test_no(self):
        x = self.f
        self.assertEqual(x(8, 17).overlap(self.open), 9)
        self.assertEqual(x(9, 17).overlap(self.open), 8)
        self.assertEqual(x(10, 17).overlap(self.open), 7)
        self.assertEqual(x(11, 17).overlap(self.open), 6)
        self.assertEqual(x(8, 15).overlap(self.open), 7)
        self.assertEqual(x(8, 14).overlap(self.open), 6)
        self.assertEqual(x(8, 13).overlap(self.open), 5)
        self.assertEqual(x(10, 13).overlap(self.open), 3)
        self.assertEqual(x(11, 13).overlap(self.open), 2)

    def test_failing(self):
        def failing(a, b):
            return a.overlap(b)
        x = self.f
        self.assertRaises(time_util.Infinity, failing, x(None, 10), self.open)
        self.assertRaises(time_util.Infinity, failing, x(None, None), self.open)
        self.assertRaises(time_util.Infinity, failing, x(10, None), self.open)
        self.assertRaises(time_util.Infinity, failing, x(None, 10), self.hi)


