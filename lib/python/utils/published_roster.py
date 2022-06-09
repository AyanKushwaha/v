
# [acosta:08/039@14:54] Created.

"""
Functions for obtaining differences between rosters in different published
states.
"""

from AbsTime import AbsTime
from utils.rave import RaveIterator, Entry
from utils.time_util import DateInterval, IntervalSet

__all__ = ['RosterChanges']


# LegTuple ==============================================================={{{1
class LegTuple(tuple):
    """Some key attributes for a leg are stored in this tuple for easier
    comparison and membership tests.
    Note that the two first entries must be integers, start and end times."""
    def __new__(cls, obj):
        return tuple.__new__(cls, obj.keys())

    def __init__(self, obj):
        self.__dict__ = obj.__dict__

    def interval(self):
        return DateInterval(AbsTime(self[0]), AbsTime(self[1]))


# RosterChangePeriod ====================================================={{{1
class RosterChangePeriod(tuple):
    """Stores original roster and changed roster for a specific time interval,
    all legs that fall within the interval are stored.  For access the
    attributes 'interval', 'original_roster' and 'revised_roster can be
    used."""
    def __new__(cls, interval, original, revised):
        return tuple.__new__(cls, (interval, original, revised))

    @property
    def interval(self):
        """The date interval (start, end)."""
        return self[0]

    @property
    def original_roster(self):
        """List of activities (original)."""
        return self[1]

    @property
    def revised_roster(self):
        """List of activities (revised)."""
        return self[2]


# RosterChanges =========================================================={{{1
class RosterChanges(list):
    """
    List of RosterChangePeriod (tuple) objects.

    The parameter 'split' will, if True, split multi-day activities into several
        one-day activities.  Note that the splitting mechanism will only work
        if the activity objects (legs) follow the following conventions:
        (1): The object is simple (only attributes).
        (2): Its 'keys()' method will return key fields as tuple, where the
             two first entries in the tuple are start and end times,
             expressed as integers.

    If this is not the case, subclass and make the appropriate modifications.

    The attribute 'changed_set' is a set of changed entries.

    The attribute 'interval_set' is a set of date intervals - (start, end)

    The attribute 'min_time' is the first start time of any activity in the the
        original roster and the revised roster.  The value is None if neither
        original roster nor revised roster was found.

    The attribute 'max_time' is the last end time of any activity in the the
        original roster and the revised roster.  The value is None if neither
        original roster nor revised roster was found.

    'min_time' and 'max_time' will only work if prerequisite (2) for 'split'
        (see above) are fulfilled.
    """

    class LegEntryProxy:
        """This Proxy class will be a "copy" of the original activity object,
        but with modified start and end times."""
        def __init__(self, le, new_start, new_end):
            self.__dict__ = le.__dict__
            self.__interval = (new_start, new_end)
            self.__master = le

        def keys(self):
            return self.__interval + self.__master.keys()[2:]

    def __init__(self, rri, from_state, to_state, split=True):
        """Fill self (which is a list) with RosterChangePeriod objects."""
        self.from_state = from_state
        self.to_state = to_state
        self.split = split
        original_roster = self.activity_list(rri, from_state)
        revised_roster = self.activity_list(rri, to_state)
        self.changed_set = set(original_roster) ^ set(revised_roster)
        self.interval_set = IntervalSet(lt.interval() for lt in self.changed_set)
        self.interval_set.merge()
        try:
            (self.min_time, self.max_time) = self.get_min_max(original_roster, revised_roster)
        except:
            (self.min_time, self.max_time) = (None, None)
        for interval in sorted(self.interval_set):
            self.append(RosterChangePeriod(interval, 
                [x for x in original_roster if interval.first <= x.interval().first and x.interval().first < interval.last],
                [x for x in revised_roster if interval.first <= x.interval().first and x.interval().first < interval.last]
            ))

    def __str__(self):
        """Debug printouts."""
        return '\n--\n'.join([str(x) for x in self])

    def activity_list(self, rri, state):
        """Return a list of activities for 'state'."""
        def ceil_(num):
            d, _ = divmod(num, base)
            return (d + 1) * base

        def floor_(num):
            d, _ = divmod(num, base)
            return d * base

        base = 1440
        R = []
        for leg in rri.eval(state):
            if self.split:
                first, last = leg.keys()[:2]
                days, _ = divmod(last - first, base)
                if days > 1:
                    first_ceil = ceil_(first)
                    last_floor = floor_(last)
                    if first != first_ceil:
                        R.append(LegTuple(self.LegEntryProxy(leg, first, first_ceil)))
                    for days in xrange(days - 1):
                        sd = first_ceil + (days * base)
                        R.append(LegTuple(self.LegEntryProxy(leg, sd, sd + base)))
                    if last != last_floor:
                        R.append(LegTuple(self.LegEntryProxy(leg, last_floor, last)))
                else:
                    R.append(LegTuple(leg))
            else:
                R.append(LegTuple(leg))
        return R

    def get_min_max(self, o, r):
        """Return (<min of first time found>, <max of last time found>)."""
        if len(o) > 0:
            if len(r) > 0:
                return min(o[0][0], r[0][0]), max(o[-1][1], r[-1][1])
            else:
                # No revised roster
                return o[0][0], o[-1][1]
        else:
            # No original roster
            if len(r) > 0:
                return r[0][0], r[-1][1]
            else:
                return None, None


# Samples ================================================================{{{1
# These sample classes are here to show the interface between your implementation
# and the classes above.

class SampleRosterIterator:
    """Iterate legs in one crew member's roster."""
    def __init__(self, crewid):
        from utils.selctx import SingleCrewFilter
        self.scf = SingleCrewFilter(crewid)
        self.ri = RaveIterator(RaveIterator.iter('iterators.roster_set',
            where=self.scf.asTuple()))
        self.ri.link(SampleLegIterator())

    def eval(self, type=None):
        try:
            return self.ri.eval(self.scf.context(type))[0]
        except:
            return []


class SampleLegIterator(RaveIterator):
    """This class is just a sample."""
    class LegEntry(Entry):
        def keys(self):
            """Return tuple with key fields for comparison."""
            if self.is_flight:
                activity = self.flight_id
            else:
                activity = self.task_code
            return (
                int(self.std_hb), 
                int(self.sta_hb),
                activity,
                self.adep,
                self.ades,
                self.meal_stop,
                self.dutycd,
                self.actype
            )

    def __init__(self):
        # This day or later
        iterator = RaveIterator.iter('iterators.leg_set',
                where='round_down(leg.%start_utc%, 24:00) >= round_down(fundamental.%now%, 24:00)')
        fields = {
            'actcode': 'packed_roster.%current_activity_code%(true, 0)',
            'actype': 'report_crewlists.%leg_ac_type%',
            'adep': 'report_crewlists.%leg_adep%',
            'ades': 'report_crewlists.%leg_ades%',
            'ci': 'report_crewlists.%checkin_time%',
            'dutycd': 'report_crewlists.%duty_code%',
            'first_in_trip': 'report_crewlists.%leg_is_first_in_trip%',
            'flight_id': 'report_crewlists.%leg_flight_id%',
            'flight_name': 'report_crewlists.%leg_flight_name%',
            'is_flight': 'report_crewlists.%leg_is_flight%',
            'meal_stop': 'report_crewlists.%leg_is_meal_stop%',
            'sta_hb': 'leg.%end_hb%',
            'sta_lt': 'report_crewlists.%leg_sta_lt%',
            'sta_utc': 'report_crewlists.%leg_sta_utc%',
            'std_hb': 'leg.%start_hb%',
            'std_lt': 'report_crewlists.%leg_std_lt%',
            'std_utc': 'report_crewlists.%leg_std_utc%',
            'stop': 'report_crewlists.%stop_duration%',
            'task_code': 'report_crewlists.%task_code%',
            'udor': 'report_crewlists.%leg_udor%',
        }
        RaveIterator.__init__(self, iterator, fields)

    def create_entry(self):
        """Important extension to RaveIterator."""
        return self.LegEntry()


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    import carmensystems.rave.api as rave
    crewid, = rave.eval(rave.selected(rave.Level.chain()), 'crew.%id%')
    print "crew", crewid
    rc = RosterChanges(SampleRosterIterator(crewid), None, "INFORMED")
    print rc


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
