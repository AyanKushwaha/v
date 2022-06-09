

"""
Time/date related utilities.
"""

import time
import warnings

import copy as c


try:
    from AbsTime import AbsTime
    FIRST_OK_ABSTIME = AbsTime(1872, 1, 1, 0, 0)
    LAST_OK_ABSTIME = AbsTime(2099, 12, 31, 23, 59)
    FIRST_USABLE_ABSTIME = AbsTime(1901, 1, 1, 0, 0) # Rave can't handle smaller! see BZ 24600
    LAST_USABLE_ABSTIME = AbsTime(2099, 12, 30, 0, 0) # For practical reasons, AbsDate / AbsTime.
except:
    warnings.warn("AbsTime class not available")


# Exceptions ============================================================={{{1

# Infinity ---------------------------------------------------------------{{{2
class Infinity(ValueError):
    """Used to signal infinitely large value for open intervals."""
    def __str__(self):
        return "Infinitely large value."


# Timer =================================================================={{{1
class Timer(list):
    def __init__(self, header=None, verbose=True):
        list.__init__(self)
        self.t = time.time()
        self.header = header
        if verbose:
            print "Timer created for %s" % header

    def tick(self, txt=None):
        now = time.time()
        if txt:
            self.append("%s: %.2f s" % (txt, now - self.t))
        self.t = now

    def display(self):
        print "**************************************************"
        print "%s:" %self.header
        for item in self:
            print "      %s" %item
        print "**************************************************"


# Period ================================================================={{{1
class Period(object):
    """
    Immutable AbsTime period

    [acosta:09/138@18:34] Please refrain from using this class, Interval
    and IntervalSet are more complete and uses common types (tuple, set)
    """
    def __init__(self, aStart, aEnd, makeCopies=True):
        warnings.warn("time_util.Period is deprecated, use Interval",
                PendingDeprecationWarning)
        if makeCopies:
            self._start = AbsTime(aStart)
            self._end = AbsTime(aEnd)
        else:
            self._start = aStart
            self._end = aEnd
        
    def __repr__(self):
        return '%s-%s' % (str(self._start), str(self._end))
        
    def __cmp__(self, other):
        startcmp = cmp(self._start, other._start)
        if startcmp:
            return startcmp
        return cmp(self._end, other._end)
        
    def __eq__(self, other):
        return self._start == other._start and self._end == other._end
        
    def __hash__(self):
        seed = 17
        prime = 37
        hash_value = seed * prime + hash(self._start)
        hash_value = hash_value * prime + hash(self._end)
        return hash_value  
    
    def __add__(self, other):    
        """
        Returns a new Period which is the sum of this and the other period
        the sum is defined as the period with start set to the minimum
        of this start and other start, end is set to max of this end and
        other end.
        """
        sum_start = min(self._start, other._start)
        sum_end = max(self._end, other._end)
        return Period(sum_start, sum_end)
    
    def start(self):
        return AbsTime(self._start)
    
    def end(self):
        return AbsTime(self._end)

    def getStartUnsafe(self):
        return self._start
    
    def getEndUnsafe(self):
        return self._end

    def setStart(self, start):
        self._start = start

    def setEnd(self, end):
        self._end = end

    def length(self):
        return (self._end - self._start)

    def overlap(self, period):
        """
        Returns the overlap between this period and period.
        
        @rtype:  Period        
        @return: The overlap between this and period or I{C{None}} if 
                 there is no overlap
        """
        if self._start > period._end or self._end < period._start:
            return None
        return Period(max(self._start, period._start), min(self._end, period._end))
        
    def contains(self, period):
        """
        @return: True if this period fully contains period i.e if
                 start of this period is before or equal to start
                 of other period and end of this period is after
                 end of this period
        """
        return self._start <= period._start and self._end >= period._end
        
    def contains_abstime(self, abstime):
        """
        @param abstime: Time to check with
        @type abstime: AbsTime

        @return: True if this period contains abstime (inclusive)
        @rtype: Bool
        """  
        return self._start <= abstime and abstime <= self._end        
        
    def not_covered_by(self, period):
        """
        Returns the part(s) of self that is not covered by period.
        I.e. period\self.
        
        If period contains self then the list will contain the two periods
        that are not covered at the ends. If the periods just overlap the
        returned list will contain one period which is the part of period
        not covered by self and finally if the periods are not
        
        Examples:
        
        self overlaps period
        self:       |-----|
        period:         |------|
        not_covered:      |----|
        
        self contained in period
        self:            |-----|
        period:        |---------|
        not_covered:   |-|     |-|
        
        self covering period
        self:       |-----|
        period:       |--|
        not_covered:  empty list
        
        self not overlapping
        self:       |-----|
        period:              |------|
        not_covered:         |------|
        
        @return: list of none, one or two period objects
        @rtype: list of periods
        """
        periods = []
        
        if self.contains(period):
            pass        
        elif not self.overlap(period):
            periods.append(period)
        else:
            if period._start < self._start:
                periods.append(Period(period._start, self._start))
            if period._end > self._end:
                periods.append(Period(self._end, period._end))
            
        return periods
        
    def difference(self, lstPeriod):
        """
        self\lstPeriod.

        Examples:

        self overlaps period
        self:       |-------------|
        lstPeriod:    |--| |--|
        not_covered:|-|  |-|  |---|
        """
        orig = [c.copy(self)]
        for p in lstPeriod:
            ret = []
            for o in orig:
                ret.extend(p.not_covered_by(o))
            orig = ret
        return orig


# intervals =============================================================={{{1

# OpenInterval -----------------------------------------------------------{{{2
class OpenInterval(tuple):
    """An interval that accepts open end points, with value None denoting
    infinity."""
    def __new__(cls, first, last):
        return tuple.__new__(cls, (first, last))

    @property
    def first(self):
        return self[0]

    @property
    def last(self):
        return self[1]

    def magnitude(self):
        """Return the distance from first to last (length, magnitude)."""
        try:
            return self[1] - self[0]
        except:
            raise Infinity()

    def embraces(self, other):
        """True if the other interval is completely embraced within this."""
        return embraces(self.first, self.last, other.first, other.last)
        
    def includes(self, point):
        """True if point is within this interval."""
        return self.first <= point <= self.last

    def adjoins(self, other):
        """Return True if self adjoins or overlaps other."""
        return adjoins(self.first, self.last, other.first, other.last)

    def overlaps(self, other):
        """Return True if self and other overlap each other."""
        try:
            return self.overlap(other) > 0
        except Infinity:
            return True

    def overlap(self, other):
        """Return number of units two intervals overlap eachother."""
        return overlap(self.first, self.last, other.first, other.last)


# Interval ---------------------------------------------------------------{{{2
class Interval(OpenInterval):
    """An interval where first and last are numeric values (times).  Cannot be
    used for open intervals."""
    def __new__(cls, first, last):
        return OpenInterval.__new__(cls, min(first, last), max(first, last))


# TimeInterval -----------------------------------------------------------{{{2
class TimeInterval(Interval):
    """Interval of two times (AbsTime)."""
    def __new__(cls, first, last):
        """Arguments are AbsTimes or values that can be converted to AbsTime"""
        if first is None:
            first = FIRST_USABLE_ABSTIME
        else:
            first = AbsTime(first)
        if last is None:
            last = LAST_USABLE_ABSTIME
        else:
            last = AbsTime(last)
        return Interval.__new__(cls, first, last)

    def __repr__(self):
        return "(%04d-%02d-%02dT%02d:%02d:00, %04d-%02d-%02dT%02d:%02d:00)" % (self.first.split()[:5] +  self.last.split()[:5])

    def includes(self, point):
        """True if point is within this interval."""
        return self.first <= AbsTime(point) <= self.last


# DateInterval -----------------------------------------------------------{{{2
class DateInterval(TimeInterval):
    """Interval of two dates (AbsTime)."""
    def __new__(cls, first, last):
        """Arguments are AbsTimes or values that can be converted to AbsTime
        NOTE: It might be tempting to use AbsDate, but see Bugzilla 26400!"""
        if first is None:
            first = FIRST_USABLE_ABSTIME
        else:
            first = AbsTime(first)
        if last is None:
            last = LAST_USABLE_ABSTIME
        else:
            last = AbsTime(last)
        if first > last:
            # Swap
            first, last = last, first
        # round down first day
        F = AbsTime(*(first.split()[:3] + (0, 0)))
        # and round up last day
        (y, m, d, H, M) = last.split()[:5]
        if (H, M) > (0, 0):
            # Add 24 hours
            r = (24, 0)
        else:
            r = (0, 0)
        L = AbsTime(*((y, m, d) + r))
        return TimeInterval.__new__(cls, F, L)

    def __repr__(self):
        return "(%04d-%02d-%02d, %04d-%02d-%02d)" % (self.first.split()[:3] +  self.last.split()[:3])


# IntervalSlicer --------------------------------------------------------{{{2
class IntervalSlicer:
    """Used by IntervalSet.split to slice an interval into several smaller parts.
    See 'slice' and '__iter__'."""
    def __init__(self, interval):
        """Save original types and keep list of slice points."""
        self.interval = interval
        self.cuts = []

    def slice(self, other):
        """Put a slice mark if the other interval overlaps this.
        self:      |----X--|       adds mark at X
        other:          |-----| 
        """
        i = self.interval
        if i.first < other.first < i.last:
            self.cuts.append(other.first)
        if i.first < other.last < i.last:
            self.cuts.append(other.last)

    def __iter__(self):
        """Return iteration of intervals."""
        if not self.cuts:
            yield self.interval
        else:
            c = [self.interval.first] + self.cuts + [self.interval.last]
            for i in xrange(1, len(c)):
                yield type(self.interval)(c[i - 1], c[i])


# IntervalSet ============================================================{{{1

def split_copy(func):
    """Adjust the 'IntervalSet' arguments by:
    (1) creating copies, 
    (2) split the copies into comparable chunks.
    (3) pass on copies to the called function."""
    def wrapper(a, b):
        i = a.copy()
        j = b.copy()
        i.split(j)
        return func(i, j)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__ = func.__dict__
    return wrapper


def merge_result(func):
    """Merge and return 'IntervalSet'"""
    def wrapper(*a):
        x = func(*a)
        x.merge()
        return x
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__ = func.__dict__
    return wrapper


class IntervalSet(set):
    """Set of intervals with some extra methods.
    An IntervalSet should contain (non-overlapping) activities, to merge
    overlaps, use the 'merge()' modifier.

    Note: Most (if not all) of the important methods from set() have been
    extended to handle intervals.

    The common idea is to: (1) first divide the intervals into comparable
    chunks, (2) use the basic methods from 'set()' to get a result and (3)
    when applicable, merge the result to avoid overlaps.

    Here are some of the things you can do with IntervalSet:

    - Get difference between two intervals
        |------------|      |------------------|         |------------| (interval 1)
              |---------------------|  |---|                            (interval 2)
        xxxxxx                       xx     xxxx         xxxxxxxxxxxxxx (difference)

       diff = interval_1 - interval_2   # calculate difference

    - Get union of two intervals:
        |------------|      |------------------|         |------------| (interval 1)
              |---------------------|  |---|                            (interval 2)
        xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx         xxxxxxxxxxxxxx (union)

       union = interval_1 | interval_2

    - Symmetric difference:
        |------------|      |------------------|         |------------| (interval 1)
              |---------------------|  |---|                            (interval 2)
        xxxxxx        xxxxxx         xx     xxxx         xxxxxxxxxxxxxx (symmetric difference)
       (intervals that are only in one, but not the other)

       symdiff = interval_1 ^ interval_2

    - Intersection:
        |------------|      |------------------|         |------------| (interval 1)
              |---------------------|  |---|                            (interval 2)
              xxxxxxxx      xxxxxxxxx  xxxxx                            (intersection)

       intersection = interval_1 & interval_2

    The split() method is central, since it allows the intervals to be compared.
    """

    def merge(self):
        """Modifier. Merge adjacent/overlapping intervals."""
        cand = None
        for item in sorted(self):
            if cand is None:
                cand = item
            elif cand.adjoins(item):
                self.remove(item)
                self.remove(cand)
                # Create new candidate of same type and add it
                cand = type(cand)(min(item.first, cand.first), max(item.last, cand.last))
                self.add(cand)
            else:
                cand = item

    def split(self, other):
        """'Double' modifier. Split self and other into chunks making it
        possible to perform common set() operations."""
        self.merge()
        other.merge()
        S = [IntervalSlicer(x) for x in sorted(self)]
        O = [IntervalSlicer(x) for x in sorted(other)]
        s = o = 0
        while s < len(S) and o < len(O):
            ss = S[s].interval
            oo = O[o].interval
            if ss.overlaps(oo):
                S[s].slice(oo)
                O[o].slice(ss)
            if ss == oo:
                o += 1
                s += 1
            elif oo.last <= ss.last:
                o += 1
            elif ss.last <= oo.last:
                s += 1
        self.clear()
        for i in S:
            for j in i:
                self.add(j)
        other.clear()
        for i in O:
            for j in i:
                other.add(j)

    def complement(self, interval=None):
        """Modifier. Clear and populate with time periods NOT covered by self."""
        #           |=interval=============|
        #       |------|x|--|x|-|xx|---------| |--|
        #         |---------------------------|
        #           xx|----|xxxxxxxxxxxxxxxx
        #    |---|  xxxxxxxxxxxxxxxxxxxxxxxx  |---|
        if interval is None:
            min_ = min(self)
            interval = type(min_)(min_.first, max([x.last for x in self]))
        x = self.__class__([interval]) - self
        self.clear()
        self.update(x)
        self.merge()

    # The following methods are described in the Python documentation and
    # have been modified to handle Intervals.

    def isdisjoint(self, other):
        return not (self & other)

    @split_copy
    def issubset(self, other):
        return set.issubset(self, other)

    @split_copy
    def __le__(self, other):
        return set.__le__(self, other)

    @split_copy
    def __lt__(self, other):
        return set.__lt__(self, other)

    @split_copy
    def issuperset(self, other):
        return set.issuperset(self, other)

    @split_copy
    def __ge__(self, other):
        return set.__ge__(self, other)

    @split_copy
    def __gt__(self, other):
        return set.__gt__(self, other)

    # Improvement?: is it really necessary to override both 'union()' and '__or__()'?
    # Is set()'s '__or__()' calling its own 'union()'?
    # There is a slight difference in that __or__ only accepts sets, whereas
    # union takes any iterable.

    @merge_result
    @split_copy
    def union(self, other):
        return set.union(self, other)

    @merge_result
    @split_copy
    def __or__(self, other):
        return set.__or__(self, other)

    @merge_result
    @split_copy
    def intersection(self, other):
        return set.intersection(self, other)

    @merge_result
    @split_copy
    def __and__(self, other):
        return set.__and__(self, other)

    @merge_result
    @split_copy
    def difference(self, other):
        return set.difference(self, other)

    @merge_result
    @split_copy
    def __sub__(self, other):
        return set.__sub__(self, other)

    @merge_result
    @split_copy
    def symmetric_difference(self, other):
        return set.symmetric_difference(self, other)

    @merge_result
    @split_copy
    def __xor__(self, other):
        return set.__xor__(self, other)

    def update(self, other):
        set.update(self, other)
        self.merge()
        return self

    __ior__ = update

    def intersection_update(self, other):
        j = other.copy()
        self.split(j)
        set.intersection_update(self, j)
        self.merge()
        return self

    __iand__ = intersection_update

    def difference_update(self, other):
        j = other.copy()
        self.split(j)
        set.difference_update(self, j)
        self.merge()
        return self

    __isub__ = difference_update

    def symmetric_difference_update(self, other):
        j = other.copy()
        self.split(j)
        set.symmetric_difference_update(self, j)
        self.merge()
        return self

    __ixor__ = symmetric_difference_update


# functions =============================================================={{{1

# copy -------------------------------------------------------------------{{{2
def copy(x):
    #NOTE: copy() is completely unnecessary, AbsTime(time) will return a 
    #new object with the same time.
    warnings.warn("time_util.copy() will be removed in future versions.",
            PendingDeprecationWarning)
    return AbsTime(x)


# month_intervals --------------------------------------------------------{{{2
def month_intervals(interval):
    """Return list of month intervals, e.g.: lo = 090103, hi = 090406 
    -> [(090101, 090201), (090201, 090301), (090301, 090401), (090401, 090501)]
    """
    l = []
    lo, hi = interval
    i1, i2 = lo.month_floor(), lo.addmonths(1)
    while i1 < hi:
        l.append(type(interval)(type(interval.first)(i1), type(interval.last)(i2)))
        i1, i2 = i2, i2.addmonths(1)
    return l


# adjoins ----------------------------------------------------------------{{{2
def adjoins(s1, e1, s2, e2):
    """Return True if interval (s1, e1) touches interval (s2, e2)."""
    try:
        return __infinity_check(max, s1, s2) <= __infinity_check(min, e1, e2)
    except Infinity:
        return True


# embraces ---------------------------------------------------------------{{{2
def embraces(s1, e1, s2, e2):
    """Return True if interval (s1, e1) completely embraces interval (s2, e2)."""
    try:
        return (s1 is None or s1 <= s2) and (e1 is None or e2 <= e1)
    except:
        return False


# overlap ----------------------------------------------------------------{{{1
def overlap(s1, e1, s2, e2):
    """Return overlapping time (in minutes) for two time intervals."""
    o = __infinity_check(min, e1, e2) - __infinity_check(max, s1, s2)
    if o > 0:
        return o
    return 0


# __infinity_check -------------------------------------------------------{{{2
def __infinity_check(func, x, y):
    """Wrapper for max() and min(), will fail with 'Infinity()' in 
    case one interval is open."""
    if x is None and y is None:
        raise Infinity()
    if x is None:
        return y
    if y is None:
        return x
    return func(int(x), int(y))


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    # Run test suite
    import os
    execfile(os.path.join(os.environ['CARMUSR'], "lib/python/tests/utils/test_time_util.py"))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
