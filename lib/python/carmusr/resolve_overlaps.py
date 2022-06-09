

"""
Remove overlaps from rosters.

Problem: Remove or adjust overlapping activities in order to be able to run
    Matador, a.k.a. "Matador Overlap v. 3", see Bugzilla 25556 for details.

Method:
    1. Iterate each roster containing overlaps.
    2. Divide roster into overlap groups.
    3. Evaluate each group, create actions.
    4. Evaluate actions.
    5. Perform actions.

Each activity in each group will be given a dignity, needed to select winner.

Example:
    Activities are ordered by rank, (1) is "most valuable", (4) is "least
    valuable". An activity is "adjustable" if it's start and end times can be
    changed, or if it can be splitted.
        |== 1 ==|
           |== 2 ==|
                                    |== 3 ==|
     |== 4 ====================================| (adjustable)

    Act. 2 will be discarded, since it is not adjustable. Act. 3 is not
    overlapping Act. 1, so it will be kept.  Act. 4 is adjustable - this will
    be the final result:
     |4=|== 1 ==|4==================|== 3 ==|4=|


UPDATE:
    Now performing operation in two steps.
    (1) Remove Overlaps on trip level, this should take care of 90% of the
        cases.
    (2) Remove Overlaps on remaining trips.


Note: Comparisons in UTC, assignments in HB time.
"""

# imports ================================================================{{{1
import Cui

import Select
import utils.time_util as time_util
import carmstd.cfhExtensions

from utils.rave import RaveIterator
from Variable import Variable


# exports, globals ======================================================={{{1
__all__ = ['main', 'run']


# help classes ==========================================================={{{1

# LegOrTripIterator ------------------------------------------------------{{{2
class LegOrTripIterator(RaveIterator):
    """Rave variables that are evaluated on each leg or trip."""
    def __init__(self, module='trip'):
        # [acosta:08/120@16:13] ok this class got ugly, but this way leg
        # and trip objects can be treated the same.
        assert module in ('trip', 'leg'), "I only know about Rave modules 'trip' and 'leg'."
        fields = {
            'category': '%s.%%category_code%%' % module,
            'code': '%s.%%code%%' % module,
            'crewid': 'crew.%id%',
            'dignity': 'studio_overlap.%%%s_dignity%%' % module,
            'empno': 'crew.%employee_number%',
            'end_hb': '%s.%%end_hb%%' % module,
            'end_station': '%s.%%end_station%%' % module,
            'end_utc': '%s.%%end_utc%%' % module,
            'flight_id': ('leg.%flight_id%', 'void_string')[module == 'trip'],
            'id': 'studio_overlap.%%%s_id%%' % module,
            'is_adjustable': 'studio_overlap.%%%s_is_adjustable%%' % module,
            'is_flight': '%s.%%is_flight_duty%%' % module,
            'is_pact_or_off': 'studio_overlap.%%%s_is_pact_or_off%%' % module,
            'logname': 'crew.%login_name%',
            'rave_module': '"%s"' % module, # NOTE: Used to separate legs and trips.
            'start_hb': '%s.%%start_hb%%' % module,
            'start_station': '%s.%%start_station%%' % module,
            'start_utc': '%s.%%start_utc%%' % module,
        }
        iterator = RaveIterator.iter('iterators.%s_set' % module,
                where='studio_overlap.%%%s_overlap%%' % module)
        RaveIterator.__init__(self, iterator, fields)


# Activity ---------------------------------------------------------------{{{2
class Activity(tuple):
    """Wrap iteration object. Subclass of tuple to be able to sort with several
    keys. The lower the value, the more "valuable" is the activity (likely to
    stay)."""
    def __new__(cls, obj):
        """Set value based on properties of trip."""
        a = obj.dignity

        if obj.is_pact_or_off:
            b = 1
        else:
            b = 0

        # NOTE: negative number!
        # Long activities are favored compared to short ones.
        c = obj.start_utc - obj.end_utc
        return tuple.__new__(cls, (a, b, c))

    def __init__(self, obj):
        self.obj = obj
        self.interval = obj.interval
        self.interval_hb = obj.interval_hb
        self._discarded = False
        self.cut_off_set = time_util.IntervalSet()

    def __str__(self):
        """For debug printouts."""
        return "%s (%s) %s %s-%s %s" % (self.obj.code, self.obj.id,
                self.obj.start_station, self.obj.start_hb, self.obj.end_hb,
                self.obj.end_station)

    __repr__ = __str__

    def is_adjustable(self):
        """Return True if obj can be adjusted in time."""
        return self.obj.is_adjustable

    def adjust(self, other):
        """Make a "hole" in 'self' in order to be able to contain 'other'
        activity."""
        self.cut_off_set.add(other)

    def is_discarded(self):
        """Marked for removal?"""
        return self._discarded

    def discard(self):
        """Mark for removal."""
        self._discarded = True

    def finalize(self, ops):
        """Commit changes. If trip/leg should be discarded, then scrap it, if it's
        going to be adjusted, remove the original and recreate from the
        remainders, if there are any.
        If it's a trip, then resolve the trip (since trips could be containing
        overlapping legs)."""
        # Remove ?
        if self.is_discarded():
            ops.remove(self.obj)
            return

        # Adjust ?
        if self.cut_off_set:
            # Using 'complement' (see utils.time_util) to get remainders.
            self.cut_off_set.complement(self.interval_hb)
            # First remove leg/trip
            ops.remove(self.obj)
            for portion in self.cut_off_set:
                # Create the parts that should remain.
                ops.create(self.obj, portion)

        # Keep ?
        else:
            # If we are looking at a trip, also resolve overlaps *within* trip.
            if self.obj.rave_module == 'trip':
                # NOTE: Calling resolve_overlaps again!
                resolve_overlaps(self.obj, ops)


# Operations -------------------------------------------------------------{{{2
class Operations:
    """Keeps track of changes to the plan."""
    def __init__(self):
        self.additions = []
        self.removals = []
        self.warnings = []

    def __str__(self):
        """For debugging."""
        return "Additions: %s\nRemovals: %s\nWarnings: %s" % (self.additions,
                self.removals, self.warnings)

    def remove(self, obj):
        """Complete removal of object."""
        self.removals.append(obj)

    def create(self, obj, interval):
        """Creation of PACT."""
        self.additions.append((obj, interval))

    def commit(self):
        """Use the lists to create/remove objects. All removals have to be done
        first, or new overlaps could arise!"""

        # Step (1) remove objects.
        for obj in self.removals:
            try:
                if obj.rave_module == 'trip':
                    deassign_trip(obj.crewid, obj.id)
                else:
                    remove_leg(obj.crewid, obj.id)
            except Exception, e:
                print "Failed remove/deassign %s: crewid=%s, id=%s - %s" % (obj.rave_module,
                        obj.crewid, obj.id, e)
                self.warnings.append(obj)

        # Step (2) create objects.
        for obj, interval in self.additions:
            try:
                create_pact(obj.crewid, obj.code, obj.start_station,
                        interval.first, interval.last)
            except Exception, e:
                print "Failed create PACT: crewid=%s, code=%s, station=%s, st=%s, et=%s - %s" % (
                        obj.crewid, obj.code, obj.start_station,
                        interval.first, interval.last, e)
                self.warnings.append(obj)


# OverlapGroup -----------------------------------------------------------{{{2
class OverlapGroup(list):
    """Group of activities that mutually overlap each other."""
    def __init__(self, interval):
        list.__init__(self)
        self.interval = interval


# Main class ============================================================={{{1
class Main:
    def __init__(self):
        """Reserved for future use."""
        pass

    def __call__(self, commit=True):
        """Start point. Iterate each crew member with overlaps and act."""
        self.commit = commit
        self.area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        self.ops = Operations()
        for crew in self.get_overlaps():
            resolve_overlaps(crew, self.ops)
        if commit:
            self.ops.commit()
            if self.ops.warnings:
                carmstd.cfhExtensions.show(("Some overlaps are remaining.\n"
                    "You will have to remove them manually"), 
                    title="Warning")
        return self.ops

    def main(self, *a):
        """If called from "command line"."""
        return self(*a)

    def get_overlaps(self):
        """Get overlaps from current area."""
        Cui.CuiSetCurrentArea(Cui.gpc_info, self.area)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, self.area, 'WINDOW')
        ri = RaveIterator(
                RaveIterator.iter('iterators.roster_set', 
                    where='studio_overlap.%roster_overlap%',
                    sort_by='crew.%employee_number%'))
        ti = LegOrTripIterator('trip')
        li = LegOrTripIterator('leg')
        ti.link(li)
        ri.link(ti)
        return ri.eval('default_context')


# functions =============================================================={{{1

# resolve_overlaps -------------------------------------------------------{{{2
def resolve_overlaps(iterable, ops):
    """Resolve overlaps for one iterable."""
    # Create set of intervals
    iset = time_util.IntervalSet()
    for obj in iterable:
        # For comparisons (overlap or not)
        obj.interval = time_util.TimeInterval(obj.start_utc, obj.end_utc)
        # For assignments (create PACT always in HB time)
        obj.interval_hb = time_util.TimeInterval(obj.start_hb, obj.end_hb)
        iset.add(obj.interval)
    # Merge adjacent intervals
    iset.merge()

    # Populate list of overlap group objects.
    ogs = []
    for interval in iset:
        ogs.append(OverlapGroup(interval))

    # Put trip/leg into overlap group that the trip/leg belongs to.
    for obj in iterable:
        for og in ogs:
            if obj.interval.overlap(og.interval):
                og.append(Activity(obj))

    # Resolve each overlap group individually.
    for og in ogs:
        resolve_group(og)
        # Modify list of operations to be performed.
        for obj in og:
            obj.finalize(ops)


# resolve_group ----------------------------------------------------------{{{2
def resolve_group(og):
    """Resolve overlaps within an overlap group containing overlapping
    trips/legs."""
    # sort group ordered by dignity
    og.sort()

    # Compare items within group
    for i in xrange(len(og)):
        if og[i].is_discarded():
            continue
        for j in xrange(i + 1, len(og)):
            if og[j].is_discarded():
                continue
            if og[i].interval.overlap(og[j].interval):
                if og[j].is_adjustable():
                    s = og[i].obj.start_hb.day_floor()
                    e = og[i].obj.end_hb.day_ceil()
                    og[j].adjust(time_util.TimeInterval(s, e))
                else:
                    # Discard object
                    og[j].discard()


# create_pact ------------------------------------------------------------{{{2
def create_pact(crewid, code, station, st, et, groupCode='',
        flags=(Cui.CUI_CREATE_PACT_DONT_CONFIRM | Cui.CUI_CREATE_PACT_SILENT |
            Cui.CUI_CREATE_PACT_NO_LEGALITY)):
    """Create PACT.""" 
    print "create_pact(%s, %s, %s, %s, %s)" % (crewid, code, station, st, et) # XXX
    def create(cut):
        overlap_flag = bool(cut) * Cui.CUI_CREATE_PACT_REMOVE_OVERLAPPING_LEGS
        Cui.CuiCreatePact(Cui.gpc_info, crewid, code, groupCode, st, et,
                station, flags | overlap_flag)
    try:
        create(False)
    except:
        create(True)


# deassign_trip ----------------------------------------------------------{{{2
def deassign_trip(crewid, id):
    """Deassign trip."""
    print "deassign_trip(%s, %s)" % (crewid, id) # XXX
    r = Variable(-1)
    rc = Cui.CuiDeassignCrrById(Cui.gpc_info, crewid, id, r,
            Cui.CUI_DEASSIGN_SILENT)


# remove_leg -------------------------------------------------------------{{{2
def remove_leg(crewid, id):
    """Remove leg from trip."""
    print "remove_leg(%s, %s)" % (crewid, id) # XXX
    Select.select({
        'FILTER_METHOD': 'REPLACE',
        'studio_overlap.%leg_id%': "%s" % id,
    }, Cui.CuiScriptBuffer, Cui.CrewMode)
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')
    Select.select({
        'FILTER_MARK': 'LEG',
        'FILTER_METHOD': 'REPLACE',
        'studio_overlap.%leg_id%': "%s" % id,
    }, Cui.CuiScriptBuffer, Cui.CrewMode)
    Cui.CuiRemoveAssignments(Cui.gpc_info, Cui.CuiScriptBuffer, crewid,
            Cui.CUI_MOVE_ASMT_SILENT)


# run ===================================================================={{{1
run = Main()


# main ==================================================================={{{1
main = run.main


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    main()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
