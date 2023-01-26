
# [acosta:07/141@12:37] 

"""
Summary of block hours, landings, etc with values stored in accumulator tables.

The table 'crew_log_acc' is not loaded in the model, which forces us to use
EntityConnection.

Furthermore, after RFI 51 was accepted, we are forced to calculate statistics
for rolling 90 days.
"""

# For description of cases se 'Use cases' at the end.

#==============================================================================
# Open issues / candidates for improvement.
#------------------------------------------------------------------------------
# The  current implementation is far from perfect, but it should do it's job in
# most cases.  Here are a number of things that might be considered in the
# event of future re-design of this module:
#
# Time-in-period
# Right now missing "time-in-period" function, any times are not split between
# months, must be fixed soon.
#
# Calculation of Block Hours
# Right now block hours are calculated using UTC days. To use homebase days
# would be preferrable, but is much more costly to calculate, especially if a
# crew member changes base during the period.
#
# Accumulated periods
# When asking for several accumulated values (e.g. blockhours and landings), we
# have to make an assumption that both counters were calculated using the same
# high-date (end of accumulated period). If not, the calculations would be more
# complex.
#
# Valid from/valid to
# Right now we allow more than one entry in crew_log_acc for each month, which
# could lead to confusion. The only sure way to update a period is to remove
# all old entries in crew_log_acc for the same period, before adding new data.
# There is no sure way to tell the period that was used for the last
# accumulation, the end date is of course of interest. We have to make an
# assumption that the last accumulation was made on a whole month, not only
# parts of a month.
#
# [acosta:09/110@19:06]
#==============================================================================


# imports ================================================================{{{1
import logging
import re
import sys
import warnings

from optparse import OptionParser

from carmensystems.dave import dmf 
from utils.ServiceConfig import ServiceConfig

from AbsTime import AbsTime
from utils.dave import EC, L1, L1Record, RW
from utils.time_util import Interval, overlap
from utils.TimeServerUtils import now
from datetime import datetime

# exports ================================================================{{{1
__all__ = ['ACCU_TYPES', 'AccuError', 'all_totals', 'totals', 'refresh', 'run',
    'main', 'interval_statistics', 'stat_intervals', 'stat_1_90_6_12_life',
    'stat_90_days']


# module variables ======================================================={{{1
# These are also in crew_log_acc_set, but this group of accumulators is the
# only ones that we know how to handle.
ACCU_TYPES = ('blockhrs', 'logblkhrs', 'simblkhrs', 'landings','oagblkhrs')

activity_regexp = re.compile(r'([A-Z])([A-Z]?)([0-9])([0-9]?)')

# Mapping between SIM codes and A/C families
sim_acfamily_map = {
    "0": "MD90",
    "2": "A320",
    "3": "B737",
    "4": "A340",
    "5": "A350",
    "6": "A330",
    "7": "CRJ",
    "8": "MD80",
    "9": "B737",
    "10":"EMJ",
}


# error handling ========================================================={{{1

# AccuError --------------------------------------------------------------{{{2
class AccuError(Exception):
    """ Used to signal internal error in this module. """
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


# basic data storage ====================================================={{{1

# Record -----------------------------------------------------------------{{{2
class Record(tuple):
    """
    This class is used to wrap objects.  The objects can come from three
    different sources:

        (1) "plain" object, values are given at object creation.
            E.g.  rec = Record("logblkhrs", "34550", "737", AbsTime(2009, 1, 1, 0, 0), 10)
                  rec.accvalue = 123

        (2) Created from a 'crew_log_acc' record, use 'from_record()'.
            E.g.  rec = Record.from_record(crew_log_acc_tablerow)

        (3) Created from a 'crew_log_acc_mod' record, use 'from_record()'.
            E.g.  rec = Record.from_record(crew_log_acc_mod_tablerow)

    The objects are sortable and their 'int'-representation is equal to their
    attribute 'accvalue'.
    """
    def __new__(cls, typ, crew, acfamily, tim, *a, **k):
        """Transform into tuple (to be used for sorting etc.). Note that the AbsTime
        is stored internally as an int."""
        return tuple.__new__(cls, (typ, crew, acfamily, int(tim)))

    def __init__(self, typ, crew, acfamily, tim, accvalue=0):
        """Set attributes, the attributes that are part of the tuple are
        read-only (see properties below)."""
        self.accvalue = accvalue

    @classmethod
    def from_record(cls, rec):
        """Create a new object, 'rec' is an instance of this class."""
        obj = cls(rec.typ, rec.crew, rec.acfamily, rec.tim, rec.accvalue)
        return obj

    @property
    def typ(self):
        return self[0]

    @property
    def crew(self):
        return self[1]

    @property
    def acfamily(self):
        return self[2]

    @property
    def tim(self):
        """Return time *as integer*, we try to avoid too many conversions
        AbsTime/int."""
        return int(self[3])

    def __int__(self):
        """ Return the field 'accvalue'. """
        return int(self.accvalue)

    def as_dict(self):
        """Return dictionary that can be used by DIG, RW etc."""
        return dict(typ=self.typ, crew=self.crew, acfamily=self.acfamily,
                tim=self.tim, accvalue=self.accvalue)


# query classes =========================================================={{{1

# Query ------------------------------------------------------------------{{{2
class Query:
    """ Base class. """
    def __init__(self, ec, typ=None, crew=None, acfamily=None, hi=None, lo=None):
        self.ec = ec
        if not typ is None and not typ in ACCU_TYPES:
            raise AccuError("Accumulator of type '%s' is not valid, available types are %s." % (typ, ACCU_TYPES))
        self.typ = typ
        self.crew = crew
        self.acfamily = acfamily
        self.hi = hi
        self.lo = lo

    def __iter__(self):
        """ Must be implemented by subclasses. """
        raise NotImplementedException()

    def query(self, table):
        """Return information from the database using EC object."""
        Q = []
        Q.extend(EqFilter('typ', self.typ))
        Q.extend(EqFilter('acfamily', self.acfamily))
        Q.extend(EqFilter('crew', self.crew))
        Q.extend(HiLoFilter('tim', self.hi, self.lo))
        if len(Q) > 0:
            l = list([x for x in getattr(self.ec, table).search(' AND '.join(Q))])
        else:
            l = list([x for x in getattr(self.ec, table)])
        return iter(l)


# ManuQuery --------------------------------------------------------------{{{2
class ManuQuery(Query):
    """
    Iterable object with manual entries (from crew_log_acc_mod).
    To convert to list use: [x for x in ManuQuery(...)]

    Each entry is a "raw" database entity.
    """
    def __iter__(self):
        """ Return result set. """
        print (Record.from_record(x) for x in self.query('crew_log_acc_mod'))
        return (Record.from_record(x) for x in self.query('crew_log_acc_mod'))


# AccuQuery --------------------------------------------------------------{{{2
class AccuQuery(Query):
    """
    Iterable object with accumulated entries (from crew_log_acc).  To convert to
    list use: [x for x in AccuQuery(...)]

    Each entry is a "raw" database entity.
    """
    def __iter__(self):
        """ Return result set. """
        return (Record.from_record(x) for x in self.query('crew_log_acc'))


# Level1Query ------------------------------------------------------------{{{2
class Level1Query(Query):
    """Level 1 DAVE queries."""

    select = "SELECT * FROM dual" # Override in subclass

    def __str__(self):
        return self.select_stmt()

    def __iter__(self):
        raise NotImplementedException('__iter__() not implemented')

    def as_records(self):
        return (L1Record.fromRow(x, self.translation) for x in self)

    def select_stmt(self):
        return self.select % {
            'schema': self.ec.getSchema(),
            'where': self.sql_where(),
        }

    def select_where(self):
        raise NotImplementedException('select_where() not implemented.')

    def sql_query(self):
        for x in L1(dmf.BorrowConnection(self.ec)).search(self.select_stmt()):
            yield x


# L1CrewLandingQuery -----------------------------------------------------{{{2
class L1CrewLandingQuery(Level1Query):
    """Run Level 1 database query on crew_landing to get information about
    landings."""

    translation = (
        ('crew', 'String'),
        ('landings', 'Int'),
        ('acfamily', 'String'),
        ('aibt', 'Int'),
        ('eibt', 'Int'),
        ('sibt', 'Int'),
    )

    select = (
        "SELECT"
        " cl.crew, cl.nr_landings, act.maintype, fl.aibt, fl.eibt, fl.sibt "
        "FROM"
        " %(schema)s.crew_landing cl, %(schema)s.flight_leg fl, %(schema)s.aircraft_type act "
        "WHERE %(where)s"
    )

    def __iter__(self):
        """Return iteration of Record objects."""
        for entry in self.sql_query():
            l = L1Record.fromRow(entry, self.translation)
            if self.acfamily is None or self.acfamily == l.acfamily:
                t = l.aibt
                if t is None:
                    t = l.eibt
                    if t is None:
                        t = l.sibt
                rec = Record('landings', l.crew, l.acfamily, t)
                rec.accvalue = l.landings
                rec.l1rec = l #XXX used by PRT report, could be removed.
                yield rec

    def sql_where(self):
        """Return where statement"""
        L = [
            "cl.activ = 'Y'",
            "cl.deleted = 'N'",
            "cl.next_revid = 0",
            "fl.deleted = 'N'",
            "fl.next_revid = 0",
            "act.deleted = 'N'",
            "act.next_revid = 0",
            "cl.leg_udor = fl.udor",
            "cl.leg_fd = fl.fd",
            "cl.leg_adep = fl.adep",
            "act.id = fl.actype",
        ]
        L.extend(HiLoFilterFlightLeg('fl', self.hi, self.lo))
        L.extend(EqFilter("act.maintype", self.acfamily))
        L.extend(EqFilter("cl.crew", self.crew))
        return " AND ".join(L)


class OagEmptyIterator:
    def __init__(self,*kwargs):
        pass
    def __iter__(self):
        return list().__iter__()
# L1BlockHoursQuery ------------------------------------------------------{{{2
class L1BlockHoursQuery(Level1Query):
    """Run Level 1 database query on crew_flight_duty to get information about
    block hours."""

    translation = (
        ('crew', 'String'),
        ('pos', 'String'),
        ('acfamily', 'String'),
        ('udor', 'Date'),
        ('fd', 'String'),
        ('adep', 'String'),
        ('aibt', 'Int'),
        ('aobt', 'Int'),
        ('eibt', 'Int'),
        ('eobt', 'Int'),
        ('sibt', 'Int'),
        ('sobt', 'Int'),
    )

    select = (
        "SELECT"
        " cfd.crew, cfd.pos, act.maintype, fl.udor, fl.fd, fl.adep,"
        " fl.aibt, fl.aobt, fl.eibt, fl.eobt, fl.sibt, fl.sobt "
        "FROM"
        " %(schema)s.crew_flight_duty cfd, %(schema)s.flight_leg fl, %(schema)s.aircraft_type act "
        "WHERE %(where)s"
    )

    def __iter__(self):
        """Return iteration of Record objects."""
        for entry in self.sql_query():
            l = L1Record.fromRow(entry, self.translation)
            if self.acfamily is None or self.acfamily == l.acfamily:
                t = l.aibt
                if t is None:
                    t = l.eibt
                    if t is None:
                        t = l.sibt
                rec = Record('blockhrs', l.crew, l.acfamily, t)
                rec.accvalue = self.blocktime(l)
                rec.l1rec = l #XXX used by PRT report, could be removed.
                yield rec

    def blocktime(self, record):
        """Calculate block time."""
        et = 0
        for x in ('aibt', 'eibt', 'sibt'):
            et = getattr(record, x)
            if et is not None:
                break
        st = 0
        for x in ('aobt', 'eobt', 'sobt'):
            st = getattr(record, x)
            if st is not None:
                break
        return et - st

    def sql_where(self):
        """Return where statement."""
        L = [
            "cfd.pos NOT IN ('DH', 'XS', 'FU', 'AU')",
            "cfd.deleted = 'N'",
            "cfd.next_revid = 0",
            "fl.deleted = 'N'",
            "fl.next_revid = 0",
            "fl.statcode <> 'C'",
            "act.deleted = 'N'",
            "act.next_revid = 0",
            "cfd.leg_udor = fl.udor",
            "cfd.leg_fd = fl.fd",
            "cfd.leg_adep = fl.adep",
            "act.id = fl.actype",
        ]
        L.extend(HiLoFilterFlightLeg('fl', self.hi, self.lo))
        L.extend(EqFilter("act.maintype", self.acfamily))
        L.extend(self.crew_select())
        return " AND ".join(L)

    def crew_select(self):
        """Broken out from sql_where to allow for override in
        L1LoggableBlockHoursQuery."""
        return EqFilter("cfd.crew", self.crew)


# L1LoggableBlockHoursQuery ----------------------------------------------{{{2
class L1LoggableBlockHoursQuery(L1BlockHoursQuery):
    """Run Level 1 database query on crew_flight_duty to get information about
    block hours. This query is trickier since it depends on 'vertical'
    information."""

    def __iter__(self):
        """Return iteration of Record objects."""
        flight_deck = {}
        # Loop two times, first time to get the vertical information
        for entry in self.sql_query():
            l = L1Record.fromRow(entry, self.translation)
            if self.acfamily is None or self.acfamily == l.acfamily:
                leg = (l.udor, l.fd, l.adep)
                if leg in flight_deck:
                    flight_deck[leg].add(l)
                else:
                    flight_deck[leg] = LoggableBlockHours(l, self.blocktime(l))
        # yield Record objects
        for leg in flight_deck:
            if self.crew is None:
                for c in flight_deck[leg]:
                    yield flight_deck[leg][c]
            else:
                yield flight_deck[leg][self.crew]

    def sql_where(self):
        """Return where statement."""
        return L1BlockHoursQuery.sql_where(self) + " AND cfd.pos IN ('FC', 'FP', 'FR')"

    def crew_select(self):
        """Overridden from L1BlockHoursQuery."""
        if self.crew is None:
            return []
        else:
            return [(
                "(cfd.leg_udor, cfd.leg_fd, cfd.leg_adep) "
                "IN"
                " ("
                    "SELECT"
                    " leg_udor, leg_fd, leg_adep "
                    "FROM"
                    " %(schema)s.crew_flight_duty "
                    "WHERE"
                    " deleted = 'N' "
                    "AND"
                    " next_revid = 0 "
                    "AND"
                    " crew = '%(crew)s' "
                    "AND"
                    " pos IN ('FC', 'FP', 'FR')"
                ")") % {'crew': self.crew, 'schema': self.ec.getSchema()}]


# L1SimBlockHoursQuery ---------------------------------------------------{{{2
class L1SimBlockHoursQuery(Level1Query):
    """Base Class, must be sub-classed. Simulator block hours could be both
    ground tasks and personal activities."""

    translation = (
        ('crew', 'String'),
        ('activity', 'String'),
        ('grp', 'String'),
        ('st', 'Int'),
        ('et', 'Int'),
    )

    def __iter__(self):
        """Return iteration of Record objects."""
        for entry in self.sql_query():
            l = L1Record.fromRow(entry, self.translation)
            try:
                acfamily = activity2acfamily(l.activity)
            except AccuError, e:
                warnings.warn(str(e))
                continue
            if self.acfamily is None or self.acfamily == acfamily:
                rec = Record('simblkhrs', l.crew, acfamily, l.et)
                rec.accvalue = self.blocktime(l)
                rec.l1rec = l #XXX used by PRT report, could be removed.
                yield rec

    def blocktime(self, record):
        """Calculate block time."""
        return record.et - record.st


# L1GTSimBlockHoursQuery -------------------------------------------------{{{2
class L1GTSimBlockHoursQuery(L1SimBlockHoursQuery):
    """Simulator Block Hours (crew_ground_duty)."""

    select = (
        "SELECT"
        " cgd.crew, gt.activity, aset.grp, gt.st, gt.et "
        "FROM"
        " %(schema)s.crew_ground_duty cgd, %(schema)s.ground_task gt, %(schema)s.activity_set aset "
        "WHERE %(where)s"
    )

    def sql_where(self):
        """Return where statement."""
        L = [
            "cgd.deleted = 'N'",
            "cgd.next_revid = 0",
            "gt.deleted = 'N'",
            "gt.next_revid = 0",
            "aset.deleted = 'N'",
            "aset.next_revid = 0",
            "cgd.task_udor = gt.udor",
            "cgd.task_id = gt.id",
            "gt.activity = aset.id",
            "aset.grp in ('SIM', 'OPC', 'OTS', 'LPC', 'AST', 'ASF', 'FFS')",
            # Maybe SIM will return too many activities SIM kan also be a PACT
        ]
        L.extend(HiLoFilter('gt.et', self.hi, self.lo))
        L.extend(EqFilter("cgd.crew", self.crew))
        return " AND ".join(L)

# L1CASimBlockHoursQuery -------------------------------------------------{{{2
class L1CASimBlockHoursQuery(L1SimBlockHoursQuery):
    """Simulator Block Hours (crew_activity)."""

    select = (
        "SELECT"
        " ca.crew, ca.activity, aset.grp, ca.st, ca.et "
        "FROM"
        " %(schema)s.crew_activity ca, %(schema)s.activity_set aset "
        "WHERE %(where)s"
    )

    def sql_where(self):
        """Return where statement."""
        L = [
            "ca.deleted = 'N'",
            "ca.next_revid = 0",
            "aset.deleted = 'N'",
            "aset.next_revid = 0",
            "ca.activity = aset.id",
            "aset.grp in ('SIM', 'OPC', 'OTS', 'LPC', 'AST', 'ASF', 'FFS')",
        ]
        L.extend(HiLoFilter('ca.et', self.hi, self.lo))
        L.extend(EqFilter("ca.crew", self.crew))
        return " AND ".join(L)


# SimBlockHoursQuery -----------------------------------------------------{{{2
class SimBlockHoursQuery(Query):
    """Unified query that checks for simulator activities in both
    crew_ground_duty and crew_activity."""
    def __iter__(self):
        L = [x for x in L1CASimBlockHoursQuery(self.ec, self.typ, self.crew, self.acfamily, self.hi, self.lo)]
        L.extend([x for x in L1GTSimBlockHoursQuery(self.ec, self.typ, self.crew, self.acfamily, self.hi, self.lo)])
        return iter(L)


# SchemaQuery ------------------------------------------------------------{{{2
class SchemaQuery(Query):
    """Iterable object with 'Record' objects from the database, not from the
    accumulated tables."""

    measures = {
        'blockhrs': L1BlockHoursQuery,
        'logblkhrs': L1LoggableBlockHoursQuery,
        'simblkhrs': SimBlockHoursQuery,
        'landings': L1CrewLandingQuery,
        'oagblkhrs' : OagEmptyIterator,
        }

    def __iter__(self):
        """Depending on which type that is chosen, this method will return
        either statistics of one type or all types."""
        L = []
        if self.typ is None:
            for t in ACCU_TYPES:
                L.extend([x for x in self.measures[t](self.ec, self.typ, self.crew, self.acfamily, self.hi, self.lo)])
            return iter(L)
        else:
            return (x for x in self.measures[self.typ](self.ec, self.typ, self.crew, self.acfamily, self.hi, self.lo))


# ManuAccuTotalsQuery ----------------------------------------------------{{{2
class ManuAccuTotalsQuery(Query):
    """Iterable object with sorted 'Record' objects from 'AccuQuery' and
    'ManuQuery' with running totals per ('typ', 'crew','acfamily')."""

    def __iter__(self):
        L = [Record.from_record(x) for x in ManuQuery(self.typ, self.crew, self.acfamily, self.hi, self.lo)]
        L.extend([Record.from_record(x) for x in AccuQuery(self.typ, self.crew, self.acfamily, self.hi, self.lo)])
        running_totals(L)
        return iter(L)


# balances ==============================================================={{{1

# Balance ----------------------------------------------------------------{{{2
class Balance:
    """Base class for various balances."""
    def __init__(self):
        self.balance = 0

    def __int__(self):
        return self.balance

    def __cmp__(self, other):
        try:
            return cmp(self.balance, other.balance)
        except:
            return cmp(self.balance, other)


# ManuBalance ------------------------------------------------------------{{{2
class ManuBalance(Balance):
    """
    Totals of manual entries (from crew_log_acc_mod) in interval [lo, hi),
    including 'lo' but not 'hi'.
    It's up to the end-user to make sure that the result is reasonable, crew
    and/or acfamily should be given, otherwise we get strange values.
    """
    def __init__(self, ec, typ, crew=None, acfamily=None, hi=None, lo=None):
        Balance.__init__(self)
        for x in ManuQuery(ec, typ, crew, acfamily, hi, lo):
            self.balance += x.accvalue
            
            
# AccuBalance ------------------------------------------------------------{{{2
class AccuBalance(Balance):
    """
    Totals of accumulated entries (from crew_log_acc) in interval [lo, hi),
    including 'lo' but not 'hi'.  The 'maxtim' attribute is the largest
    accumulated 'tim' found.
    It's up to the end-user to make sure that the result is reasonable, crew
    and/or acfamily should be given, otherwise we get strange values.
    """
    def __init__(self, ec, typ, crew=None, acfamily=None, hi=None, lo=None):
        Balance.__init__(self)
        # Highest datetime of accumulated entry
        self.maxtim = int(AbsTime(0))
        for x in AccuQuery(ec, typ, crew, acfamily, hi, lo):
            if x.tim > self.maxtim:
                self.maxtim = x.tim
            self.balance += x.accvalue
            

# SchemaBalance ----------------------------------------------------------{{{2
class SchemaBalance(Balance):
    """
    Totals of plan entries (from plan) in interval [lo, hi), including 'lo' but
    not 'hi'. The values are computed using Rave variables.
    It's up to the end-user to make sure that the result is reasonable, crew
    and/or acfamily should be given, otherwise we get strange values.
    """
    def __init__(self, ec, typ, crew=None, acfamily=None, hi=None, lo=None):
        Balance.__init__(self)
        for x in SchemaQuery(ec, typ, crew, acfamily, hi, lo):
            self.balance += x.accvalue


# Monthly statistics ====================================================={{{1

# StatInfo ---------------------------------------------------------------{{{2
class StatInfo(dict):
    """Structure that contains dictionary of IntervalStatistics type and
    an attribute 'intervals', where the intervals are defined."""
    def __init__(self, d, i):
        dict.__init__(self, d)
        self.intervals = i


# IntervalStatistics -----------------------------------------------------{{{2
class IntervalStatistics(dict):
    """
    Return this structure:
    { typ1: { crew1: { acfamily1: {
                         interval1: value
                         ...
                         intervalN: value
                     },
                     ...
                     acfamilyN: { ... }
              crew2: { ... }
            }
      typ2: { ... }
    }
    Proposed enhancement: maybe we should save maxtim here??
    """
    def __init__(self, iter, intervals):
        dict.__init__(self)
        self.intervals = intervals
        for entry in iter:
            for i in intervals:
                if i.first <= entry.tim < i.last:
                    self.add(entry, i)

    def add(self, entry, i):
        (typ, crew, acfamily, tim) = entry
        if typ in self:
            if crew in self[typ]:
                if acfamily in self[typ][crew]:
                    self[typ][crew][acfamily][i] = self[typ][crew][acfamily].get(i, 0) + entry.accvalue
                else:
                    self[typ][crew][acfamily] = {i: entry.accvalue}
            else:
                self[typ][crew] = {acfamily: {i: entry.accvalue}}
        else:
            self[typ] = {crew: {acfamily: {i: entry.accvalue}}}


# Help classes for time and crew filtering ==============================={{{1

# EqFilter ---------------------------------------------------------------{{{2
class EqFilter(list):
    """The point of using a list in this case is that we don't have to handle
    the case when the list is empty since we use x.extend(EqFilter(x, y))."""
    def __init__(self, ref, value):
        list.__init__(self)
        if value is not None:
            self.append("%s = '%s'" % (ref, value))

    def __str__(self):
        return " AND ".join(self)


# HiLoFilter -------------------------------------------------------------{{{2
class HiLoFilter(list):
    """Filter to check if a time is between hi and lo."""
    def __init__(self, ref, hi=None, lo=None):
        list.__init__(self)
        if not lo is None:
            self.append("%s >= %d" % (ref, lo))
        if not hi is None:
            self.append("%s < %d" % (ref, hi))

    def __str__(self):
        return " AND ".join(self)


# HiLoFilterFlightLeg ----------------------------------------------------{{{2
class HiLoFilterFlightLeg(HiLoFilter):
    """Special case for flight_leg: use the best available of actual, estimated
    and scheduled times."""
    def __init__(self, ref, hi=None, lo=None):
        list.__init__(self)
        if not (hi is None and lo is None):
            aibt = '%s.aibt' % ref
            eibt = '%s.eibt' % ref
            sibt = '%s.sibt' % ref
            self.append("(%s)" % " OR ".join((
                "(%s)" % HiLoFilter(aibt, hi, lo),
                "(%s IS NULL AND %s)" % (aibt, HiLoFilter(eibt, hi, lo)),
                "(%s IS NULL AND %s)" % (eibt, HiLoFilter(sibt, hi, lo)),
            )))


# Help classes for L1 queries ============================================{{{1

# LoggableBlockHours -----------------------------------------------------{{{2
class LoggableBlockHours(dict):
    """Help class used to calculate Loggable Block Hours.
    Loggable (or Reduced) Block Hours are defined like this:
     * For FC -> number of block hours
     * For FP, FR -> number of block hours reduced in proportion to the number
       of relief pilots."""

    # Number of crew needed to fly the A/C, always two at SAS
    needed_to_fly = 2.0
    typ = 'logblkhrs'

    def __init__(self, rec, blocktime):
        """First time the first crew member will set A/C family and start
        and end times. These are all equal among the crew members."""
        dict.__init__(self, {rec.crew: rec.pos})
        self.rec = rec #XXX Used by PRT report, could be removed.
        self.blocktime = blocktime
        self.acfamily = rec.acfamily
        t = rec.aibt
        if t is None:
            t = rec.eibt
            if t is None:
                t = rec.sibt
        self.tim = t

    def __getitem__(self, crew):
        """Return Record() object with accvalue set to the loggable block
        time."""
        r = Record(self.typ, crew, self.acfamily, self.tim)
        r.l1rec = self.rec #XXX Used by PRT Report, could be removed.
        pos = dict.__getitem__(self, crew)
        if pos == 'FC':
            r.accvalue = self.blocktime
        elif pos in ('FP', 'FR'):
            r.accvalue = int(round(self.blocktime * 2.0 / len(self)))
        return r

    def add(self, rec):
        """Add crew member to the dict."""
        dict.__setitem__(self, rec.crew, rec.pos)


# Command line handling =================================================={{{1
class Main:
    def __init__(self):
        logging.basicConfig()
        self.log = logging.getLogger('utils.crewlog')
        self.log.setLevel(logging.INFO)


    def __call__(self, ec=None, typ=None, crew=None, acfamily=None, hi=None, lo=None):
        self.log.debug("typ='%s', crew='%s', acfamily='%s', hi='%s', lo='%s'" % (
            typ, crew, acfamily, hi, lo))
        if ec is None:
            return refresh(typ=typ, crew=crew, acfamily=acfamily, hi=hi, lo=lo)
        else:
            return refresh_ec(ec, typ=typ, crew=crew, acfamily=acfamily, hi=hi, lo=lo)


    def main(self, *argv):
        rc = 0
        try:
            if len(argv) == 0:
                argv = sys.argv[1:]
            else:
                argv = list(argv)
            parser = OptionParser(
                    version='%%prog %s' % '$Revision$',
                    description="Refresh and update 'crew_log_acc' with values from the plan.")
            parser.add_option("-c", "--connect",
                    dest="connect",
                    help=("Optional connect string to database to where data will be written."
                        " e.g. 'oracle:user/pass@service'. Will use XML config if not given."))
            parser.add_option("-s", "--schema",
                    dest="schema",
                    help="Database schema to use for import. Will use XML config if not given.")
            parser.add_option("-v", "--verbose",
                    action="store_true",
                    dest="verbose",
                    default=False,
                    help="Show verbose messages.")
            parser.add_option("-f", "--from-date",
                    dest="lo",
                    help="Refresh from this date.")
            parser.add_option("-t", "--to-date",
                    dest="hi",
                    help="Refresh to this date.")
            parser.add_option("--crew",
                    dest="crew",
                    help="Only update this crew member.")
            parser.add_option("--ac-family",
                    dest="acfamily",
                    help="Only update this A/C family.")
            parser.add_option("--type",
                    dest="typ",
                    help="Only update this counter can be one of %s." % (ACCU_TYPES,))

            opts, args = parser.parse_args(argv)

            if opts.verbose:
                self.log.setLevel(logging.DEBUG)

            kwargs = {}
            # Check validity of arguments.
            if opts.lo:
                try:
                    kwargs['lo'] = AbsTime(opts.lo)
                except:
                    parser.error("Argument -f FROMDATE is not in a valid format.")
            if opts.hi:
                try:
                    kwargs['hi'] = AbsTime(opts.hi)
                except:
                    parser.error("Argument -t TODATE is not in a valid format.")
            if opts.crew:
                kwargs['crew'] = opts.crew
            if opts.acfamily:
                kwargs['acfamily'] = opts.acfamily
            if opts.typ:
                if not opts.typ in ACCU_TYPES:
                    parser.error("Not a valid choice for --type (%s), valid types are %s." % (
                        opts.typ, str(ACCU_TYPES)))
                kwargs['typ'] = opts.typ
                
            if opts.connect or opts.schema:
                # Open EC based on arguments.
                if opts.schema is None:
                    parser.error("Must give -s SCHEMA together with -c option.")
                if opts.connect is None:
                    parser.error("Must give -c CONNECT together with -s option.")
                try:
                    ec = EC(opts.connect, opts.schema)
                    self.log.debug("connect = '%s', schema = '%s'" % (opts.connect, opts.schema))
                    revid = self(ec, **kwargs)
                finally:
                    try:
                        ec.close()
                    except:
                        pass
            else:
                # Use configured EC
                self.log.debug("Using XML config to get connection string and schema.")
                revid = self(**kwargs)
 
            log_str = "[%s] Finished. Saved with revid = (%d)." % (datetime.now(), revid)
            self.log.info(log_str)
            print log_str # Needed to get the string into the tee log
            
        except SystemExit, se:
            return rc
        except Exception, e: 
            log_str = "[%s] %s" % (datetime.now(), e)
            self.log.error(log_str)
            print log_str # Needed to get the string into the tee log
            return 2
        return rc


# help functions ========================================================={{{1

# activity2acfamily ------------------------------------------------------{{{2
def activity2acfamily(activity):
    """Convert activity code to "simulator A/C family"."""
    acfamily = None
    m = activity_regexp.match(activity)
    if m:
        main_grp, subgrp, actype, time_slot = m.groups()
        acfamily = sim_acfamily_map.get(actype)
    if acfamily is None:
        raise AccuError("No A/C family found for activity '%s'." % activity)
    return acfamily


# merge_add --------------------------------------------------------------{{{2
def merge_add(*a):
    """
    Returns a dictionary where each key in the output dictionary contains the
    sum of the keys from the input dictionaries.
    Example:
        X = {'a': 2, 'b': 3}
        Y = {'b': 4, 'd': 54}
        Z = {'a': 3, 'e': 1}
        merge_add(X, Y, Z) will give {'a': 5, 'b': 7, 'd': 54, 'e': 1}
    """
    R = {}
    for x in a:
        for (k, v) in x.iteritems():
            R[k] = R.get(k, 0) + v
    return R


# merge_statistics -------------------------------------------------------{{{2
def merge_statistics(*a):
    """Merge several dicts with statistics into one."""
    R = {}
    for s in a:
        for typ in s:
            if not typ in R:
                R[typ] = {}
            for crew in s[typ]:
                if not crew in R[typ]:
                    R[typ][crew] = {}
                for acfamily in s[typ][crew]:
                    if not acfamily in R[typ][crew]:
                        R[typ][crew][acfamily] = {}
                    for i in s[typ][crew][acfamily]:
                        R[typ][crew][acfamily][i] = (
                                R[typ][crew][acfamily].get(i, 0) +
                                s[typ][crew][acfamily][i])
    return R


# monthly_sums -----------------------------------------------------------{{{2
def monthly_sums(iter):
    """Return list of accumulated records for time intervals."""
    d = {}
    for e in iter:
        t_floor = int(AbsTime(e.tim).month_floor())
        key = (e.typ, e.crew, e.acfamily, t_floor)
        if key in d:
            d[key].append(e)
        else:
            d[key] = [e]
    L = []
    for key in d:
        total = 0
        for e in d[key]:
            if e.accvalue:
                total += e.accvalue
            else:
                print "Warning: Null accvalue for %s" % repr(e)  
        if total != 0:
            L.append(Record(*key, **{'accvalue': total}))
    return L


# run_with_ec ------------------------------------------------------------{{{2
def run_with_ec(func):
    """Decorator that opens a new EC connection and invokes 'func'. The connect
    string and schema is read from the XML configuration that belongs to the
    installation."""
    def wrapper(*a, **k):
        if 'ec' in k:
            ec = k['ec']
            del k['ec']
            return func(ec, *a, **k)
        else:
            try:
                try:
                    sc = ServiceConfig()
                    connstr = sc.getServiceUrl('database')
                    schemastr = sc.getPropertyValue('db/schema')
                    ec = EC(connstr, schemastr)
                except:
                    raise AccuError('Could not connect to database, check config files.')
                return func(ec, *a, **k)
            finally:
                try:
                    ec.close()
                except:
                    pass
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__ = func.__dict__
    return wrapper


# running_totals ---------------------------------------------------------{{{2
def running_totals(aList, level=3):
    """Help function that sorts aList and creates running totals. The level is
    by default 3 which means that the sum will be on (typ, crew, acfamily)"""
    aList.sort()
    tot = 0
    oldkey = None
    for rec in aList:
        key = rec[:level]
        if oldkey != key:
            tot = 0
            oldkey = key
        tot += rec.accvalue
        rec.total = tot
    return aList


# exported functions ====================================================={{{1

# all_totals -------------------------------------------------------------{{{2
def all_totals_ec(ec, type, crew, acfamily, hi, lo=None):
    """ Returns balance of all contributions (including the plan) at given
    date. """
    m = ManuBalance(ec, type, crew, acfamily, hi, lo)
    a = AccuBalance(ec, type, crew, acfamily, hi, lo)
    r = SchemaBalance(ec, type, crew, acfamily, hi, AbsTime(a.maxtim).month_ceil())
    return int(m) + int(a) + int(r)


# totals -----------------------------------------------------------------{{{2
@run_with_ec
def totals(ec, type, crew, acfamily, hi, lo=None):
    """ Returns balance excluding the plan at given date. """
    m = ManuBalance(ec, type, crew, acfamily, hi, lo)
    a = AccuBalance(ec, type, crew, acfamily, hi, lo)
    return int(m) + int(a)


# refresh ----------------------------------------------------------------{{{2
def refresh_ec(ec, typ=None, crew=None, acfamily=None, hi=None, lo=None):
    """Refresh the accumulator tables with entries from the plan. Returns
    revid."""
    # default is to run from month before previous month until start of
    # previous month
    if hi is None and lo is None:
        this_month_start = now().month_floor()
        hi = this_month_start.addmonths(-1)
        lo = this_month_start.addmonths(-2)
    
    rw = RW(ec)
    # Remove old accumulated entries
    for entry in AccuQuery(ec, typ=typ, crew=crew, acfamily=acfamily, hi=hi, lo=lo):
        rw.crew_log_acc.dbdelete(entry.as_dict())
        rw.apply() #SKCMS-1997: Applying after each operation, since we otherwise get a monster SQL query that can take hours(!) to parse
        
    for entry in monthly_sums(SchemaQuery(ec, typ=typ, crew=crew, acfamily=acfamily, hi=hi, lo=lo)):
        if entry.accvalue != 0:
            rw.crew_log_acc.dbwrite(entry.as_dict())
            rw.apply() #SKCMS-1997: Applying after each operation, since we otherwise get a monster SQL query that can take hours(!) to parse

    return rw.apply()


refresh = run_with_ec(refresh_ec)


# interval_statistics ----------------------------------------------------{{{2
interval_statistics = IntervalStatistics


# stat_intervals ---------------------------------------------------------{{{2
@run_with_ec
def stat_intervals(ec, crew, intervals, typ=None, acfamily=None, hi=None):
    """Return statistics for chosen intervals, using accumulators if
    available.
    NOTE: Can only give reliable results if hi is "now".
    """
    if hi is None:
        hi = now().day_floor()
    acc_end = hi.month_floor().addmonths(-2)
    manu_stat = interval_statistics(
            ManuQuery(ec, typ=typ, crew=crew, acfamily=acfamily, hi=int(hi)),
            intervals)
    accu_stat = interval_statistics(
            AccuQuery(ec, typ=typ, crew=crew, acfamily=acfamily,
                hi=int(acc_end)),
            intervals)
    plan_stat = interval_statistics(
            SchemaQuery(ec, typ=typ, crew=crew, acfamily=acfamily,
                lo=int(acc_end), hi=int(hi)),
            intervals)

    return StatInfo(merge_statistics(manu_stat, accu_stat, plan_stat), intervals)


# stat_1_90_6_12_life ----------------------------------------------------{{{2
@run_with_ec
def stat_1_90_6_12_life(ec, crew, typ=None, acfamily=None, hi=None):
    """Return statistics for current month, last month, last 90 days, last 6
    months and last 12 months.
    NOTE: Can only give reliable results if hi is "now".
    """
    def int_interval(a, b):
        return Interval(int(a), int(b))

    if hi is None:
        hi = now().day_floor()

    this_start = hi.month_floor()
    intervals = [
        int_interval(this_start, hi.month_ceil()),            # This month
        int_interval(this_start.addmonths(-1), this_start),   # Last month
        int_interval(this_start.addmonths(-6), this_start),   # Last 6
        int_interval(this_start.addmonths(-12), this_start),  # Last 12
        int_interval(0, hi),                                  # Lifetime
    ]
    manu_stat = interval_statistics(
            # Gets stats from "crew_log_acc_mod" (manual corrections)
            # All params go directly to the parent class: "Query"
            ManuQuery(ec, typ=typ, crew=crew, acfamily=acfamily, hi=int(hi)),
            intervals)

    accu_stat = interval_statistics(
            # Gets stats from "crew_log_acc". Note the addmonths(-2)!
            # All params go directly to the parent class: "Query"
            AccuQuery(ec, typ=typ, crew=crew, acfamily=acfamily,
            hi=int(this_start.addmonths(-2))),
            intervals)
    plan_stat = interval_statistics(
            # This query picks up data for the last 2 months directly from other tables than "crew_log_acc*"
            # In case of typ="blockhrs", a L1 query defined in class L1BlockHoursQuery is run.
            SchemaQuery(ec, typ=typ, crew=crew, acfamily=acfamily,
            lo=int(this_start.addmonths(-2)), hi=int(hi)),
            intervals)
            # This method runs a SchemaQuery similar to the one above,
            # but for the last 90 days in stead of the last 2 months.

    day_stat = stat_90_days(crew=crew, typ=typ, acfamily=acfamily, hi=hi,
            ec=ec)
    # Put the 90 days interval in correct position
    intervals.insert(2, day_stat.intervals[0])
    # Finally the different stats are "merged" into a (somewhat overly complex) structure
    return StatInfo(merge_statistics(manu_stat, accu_stat, plan_stat, day_stat),
            intervals)


# stat_90_days -----------------------------------------------------------{{{2
@run_with_ec
def stat_90_days(ec, crew, typ=None, acfamily=None, hi=None):
    """Return statistics for last 90 days (rolling)."""
    if hi is None:
        hi = now().day_floor()
    lo = hi.adddays(-90)
    intervals = [Interval(int(lo), int(hi))]
    return interval_statistics(SchemaQuery(ec, typ=typ, crew=crew,
        acfamily=acfamily, lo=int(lo), hi=int(hi)), intervals)


# bit ===================================================================={{{1
def bit():
    """ Built-in test - call test function. 
        Very basic, should be improved.
    """
    try:
        from tm import TM
        ec = EC(TM.getConnStr(), TM.getSchemaStr())
        for x in AccuQuery(ec, typ="logblkhrs", hi=AbsTime(2009, 1, 2, 12, 0), lo=AbsTime(2008, 1, 2, 0, 0)):
            print x, x.accvalue
        for x in ManuQuery(ec, typ="logblkhrs", hi=AbsTime(2009, 1, 2, 12, 0), lo=AbsTime(2008, 1, 2, 0, 0)):
            print x, x.accvalue
        for x in SchemaQuery(ec, typ="logblkhrs", hi=AbsTime(2009, 1, 2, 12, 0), lo=AbsTime(2009, 1, 2, 0, 0)):
            print x, x.accvalue
    finally:
        ec.close()


# run ===================================================================={{{1
run = Main()


# main ==================================================================={{{1
main = run.main


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    #bit()
    #refresh()
    #sys.exit(main())
    main()


# Use cases =============================================================={{{1
# Case 1 - No accumulated values exist:
#
#         |                                     |070410
#    .....+------|------|------|------|------|--+.....
#         061101 061201 070101 070201 070301 070401
#
# Use database queries to calculate, note that this will not work for
# lifetime statistics, since flight_leg etc. are filtered.
#
# Case 2 - Accumulated values exist:
#
#         |                                     |070410
#    .....+======|======|======|======|------|--+.....
#         061101 061201 070101 070201 070301 070401
#
# Use accumulated values and continue with database queries for the
# time period that has not yet been accumulated.
#
# In both these cases above we need to compensate for manual changes (in
# crew_log_acc_mod).

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
