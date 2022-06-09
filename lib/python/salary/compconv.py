"""
Some routines for resetting/converting various compensation days accounts.
"""

# imports ================================================================{{{2
import logging
import math
import utils.time_util as time_util

from AbsTime import AbsTime
from RelTime import RelTime
from salary.accounts import Reset, Conversion, AccountBalanceDict
from salary.reasoncodes import REASONCODES
from tm import TM
from utils.dave import EC
from utils.TimeServerUtils import now


# logging ================================================================{{{1
logging.basicConfig(format='%(asctime)s: %(name)-12s: %(levelname)s: %(message)s')
log = logging.getLogger('salary.compconv')
log.setLevel(logging.DEBUG)


# exports ================================================================{{{1
__all__ = ['F3_to_F31', 'F3_to_F3S', 'F7S_gain', 'F33_gain',
    'bought_sold_reset']


# classes ================================================================{{{1

# Cache ------------------------------------------------------------------{{{2
class Cache(dict):
    """ This class will speed up searches by caching search results. """
    def __init__(self):
        # Holds the intervals where condition is true, per crew
        dict.__init__(self)

    def __call__(self, id, timestamp):
        if id not in self:
            # save list of intervals for this crew member
            self[id] = self.set_okIntervals(id)
        for (start, stop) in self[id]:
            if start <= timestamp <= stop:
                return True
        return False
    

# FDCache ----------------------------------------------------------------{{{2
class FDCache(Cache):
    """ Cached look-up for Flight Deck. """
    def __init__(self, fromDate, toDate):
        Cache.__init__(self)
        self.interval = time_util.TimeInterval(fromDate, toDate)

    def set_okIntervals(self, crewid):
        okIntervals = time_util.IntervalSet()
        crew = TM.crew[(crewid,)]
        for crew_emp in crew.referers('crew_employment', 'crew'):
            ti = time_util.TimeInterval(crew_emp.validfrom, crew_emp.validto)
            if ti.overlap(self.interval):
                if crew_emp.crewrank.maincat.id == 'F':
                    okIntervals.add(ti)
        okIntervals.merge()
        return list(sorted(okIntervals))

# QACache ----------------------------------------------------------------{{{2
class QACCCache(Cache):
    """ Cached look-up for Qimber Agreement group. """
    def __init__(self, fromDate, toDate):
        Cache.__init__(self)
        self.interval = time_util.TimeInterval(fromDate, toDate)

    def set_okIntervals(self, crewid):
        okIntervals = time_util.IntervalSet()
        crew = TM.crew[(crewid,)]
        for crew_cont in crew.referers('crew_contract', 'crew'):
            ti = time_util.TimeInterval(crew_cont.validfrom, crew_cont.validto)
            if ti.overlap(self.interval):
                if crew_cont.contract.agmtgroup.id == 'QA_CC_AG':
                    okIntervals.add(ti)
        okIntervals.merge()
        return list(sorted(okIntervals))


# LHCache ----------------------------------------------------------------{{{2
class LHCache(Cache):
    """ Cached look-up for Long-Haul pilots. """
    def __init__(self, fromDate, toDate):
        Cache.__init__(self)
        self.interval = time_util.TimeInterval(fromDate, toDate)

    def set_okIntervals(self, crewid):
        """ Longhaul if Pilot has qualification for A3 or A4. """
        okIntervals = time_util.IntervalSet()
        crew = TM.crew[(crewid,)]
        for crew_qual in crew.referers('crew_qualification', 'crew'):
            ti = time_util.TimeInterval(crew_qual.validfrom, crew_qual.validto)
            if crew_qual.qual.typ == 'ACQUAL' and crew_qual.qual.subtype in ('A3', 'A4'):
                okIntervals.add(ti)
        okIntervals.merge()
        return list(sorted(okIntervals))


# Increment_F7S classes =================================================={{{1

# F7SCrewRecord-----------------------------------------------------------{{{2
class F7SCrewRecord(Conversion):
    """
    Base class for the different crew categories. Is subclass of Conversion,
    from where the record() method comes.
    """
    def __init__(self, ent, year, data):
        """Save some common init data."""
        # The booking date should be the first of next year.  Typically this
        # conversion function is run in the end of November, If run at
        # 2009-11-16 then the booking date should be 2010-01-01, the days
        # should be available from the 1st of Jan. [JIRA: SASCMS-1027]
        # See F7S_gain below.
        Conversion.__init__(self, year)
        # Expand these attributes already now, so we can get an early exception.
        self.crewid = ent.crew.id
        self.crewrank = ent.crewrank.id
        self.country = ent.country.id
        self.year = year
        self.data = data

    def increment(self):
        """Return number of F7S days to increase the crew account with."""
        amount = int(round(self._increment() * 100))
        log.debug("crew id=%s, rank=%s, country=%s, amount=%d" % (self.crewid,
            self.crewrank, self.country, amount))
        self.record(self.crewid, "F7S", amount)

    def _increment(self):
        """Must be subclassed."""
        raise NotImplementedError("Must define _increment().")


# F7SFD ------------------------------------------------------------------{{{2
class F7SFD(F7SCrewRecord):
    """Flight crew get 0, 1 or 2 F7S days every year based on: (1) Number of
    reduction days the previous year, and, (2) The employment time."""
    def __init__(self, ent, year, data):
        """For flight crew the number of F7S days is dependent on leave of
        absence taken the previous year."""
        F7SCrewRecord.__init__(self, ent, year, data)
        self.hi = year
        self.lo = year.addyears(-1)
        self.non_reducing_activities = ()
        self.empdate = ent.crew.employmentdate
        self.quitdate = ent.crew.retirementdate

    def _increment(self):
        """Return number of F7S days. Reduction is nearly identical for FD from
        Danmark, Norway and Sweden. The only difference is that Danish crew
        does not get reductions for a couple of LOA codes."""
        # Reduction factor = amount of "non-loa" time per year
        loa_days = round(self._reduce() / 1440.0)
        # Reduce if crew has not been employed long enough, or, if crew will
        # quit work the coming year.
        yyyy = self.year.split()[0]
        if self.empdate is None:
            started_late = True
            log.warning("Crew with crewid %s does not have an employment date in crew." % (self.crewid))
        else:
            started_late = (self.empdate >= AbsTime(yyyy , 7, 1, 0, 0))
        if self.quitdate is None:
            left_early = False
        else:
            left_early = (self.quitdate < AbsTime(yyyy, 7, 1, 0, 0))
        if loa_days >= 365:
            return 0
        elif loa_days > 92:
            return 1 - (0, 1)[left_early or started_late]
        else:
            return 2 - (0, 1)[left_early or started_late]

    def _reduce(self):
        """Return integer = number of minutes LOA within interval.
        EntityConnection is used to be able to search a wider interval."""
        loa_time = 0
        for a in self.data.ec.crew_activity.search(
                "crew = '%s' AND et > %d AND st < %d AND activity LIKE 'LA%%%%'" % (
                self.crewid, self.lo, self.hi)):
            if a.activity in self.non_reducing_activities:
                continue
            loa_time += time_util.overlap(a.st, a.et, self.lo, self.hi)
        return loa_time


# F7SCC ------------------------------------------------------------------{{{2
class F7SCC(F7SCrewRecord):
    """Base class for cabin crew. The _reduce() method is used by
    subclasses."""
    def __init__(self, ent, year, data):
        F7SCrewRecord.__init__(self, ent, year, data)
        self.lo = year
        self.hi = year.addyears(1)
        self.reducing_activities = ()

    def _reduce(self):
        """Return integer = number of minutes LOA within interval.
        EntityConnection is used to be able to search a wider interval."""
        assert self.reducing_activities != (), "Can't call reduce without reducing_activities!"
        loa_time = 0
        for a in self.data.ec.crew_activity.search(
                "crew = '%s' AND et > %d AND st < %d AND activity IN %s" % (
                self.crewid, self.lo, self.hi, self.reducing_activities)):
            loa_time += time_util.overlap(a.st, a.et, self.lo, self.hi)
        return loa_time


# F7SCCDK ----------------------------------------------------------------{{{2
class F7SCCDK(F7SCC):
    """Danish cabin crew will get 9 F7S days, which are reduced if crew will
    have planned leave-of-absence for the coming year until and including the
    31th of May. New requirement: Temp crew will not get F7S.  New (CR 473):
    F7S days rounded to one decimal."""
    def __init__(self, ent, year, data):
        F7SCC.__init__(self, ent, year, data)
        self.reducing_activities = ('LA47', 'LA51', 'LA76', 'LA77', 'LA89')

    def _increment(self):
        """Return number of F7S days. Crew that have been both temporary
        ('vikarier') and 'ordinary crew' will be reduced proportionally to the
        amount of time they have been temporary."""
        if not self.crewid in self.data.contracts:
            log.error("Crew with id %s does not have a valid entry in 'crew_contract'." % (self.crewid,))
            return 0
        active_time = 0
        for c in self.data.contracts[self.crewid]:
            if c.validto < self.lo or c.validfrom > self.hi:
                continue
            # If contract data is invalid (raises Exception), then
            # this is caught outside, crew will not get any F7S
            if "Temp" not in c.contract.desclong:
                active_time += time_util.overlap(c.validfrom, c.validto, self.lo, self.hi)
        # Convert RelTime to int
        hi = int(self.hi)
        lo = int(self.lo)
        # Reduction factor = amount of "non-loa" time per year
        rf = float(hi - lo - self._reduce()) / (hi - lo)
        # Weighted amount of time crew has been temp crew
        wd = float(9 * active_time) / (hi - lo)
        # CR 473 (SASCMS-2033) - F7S days rounded to one decimal
        return round(rf * wd, 1)


# F7SCCNO ----------------------------------------------------------------{{{2
class F7SCCNO(F7SCC):
    """Norwegian cabin crew will get F7S days based on duty percentage only.
    CR 473: F7S days reduced for LOA; result rounded with no decimal."""
    def __init__(self, ent, year, data):
        F7SCC.__init__(self, ent, year, data)
        self.reducing_activities = ('LA41', 'LA44', 'LA48', 'LA51', 'LA63')

    def _increment(self):
        """Only based on duty percentage."""
        if not self.crewid in self.data.contracts:
            log.error("Crew with id %s does not have a valid entry in 'crew_contract'." % (self.crewid,))
            return 0
        d = {}
        for c in self.data.contracts[self.crewid]:
            if c.validto < self.lo or c.validfrom > self.hi:
                continue
            if "Temp" in c.contract.desclong:
                # Temporary crew ("vikarier") does not get F7S
                continue
            # SASCMS-1086
            # 100% and 93,7% will get 5 F7S
            # 80% and 75% will get 4 F7S
            # 60% and 50% will get 3 F7S
            dutyperc = c.contract.dutypercent
            if dutyperc > 80:
                category = 1 # 5 F7S days per year
            elif dutyperc > 60:
                category = 2 # 4 F7S days per year
            else:
                category = 3 # 3 F7S days per year
            d[category] = d.get(category, 0) + time_util.overlap(c.validfrom, c.validto, self.lo, self.hi)
        # Convert all RelTime to int
        hi = int(self.hi)
        lo = int(self.lo)
        # Reduction factor = amount of "non-loa" time per year
        rf = float(hi - lo - self._reduce()) / (hi - lo)
        # Weighted amount of days
        wd = float(5 * d.get(1, 0) + 4 * d.get(2, 0) + 3 * d.get(3, 0)) / (hi - lo)
        return round(wd * rf)


# F7SCCSE ----------------------------------------------------------------{{{2
class F7SCCSE(F7SCC):
    """Swedish cabin crew will get 5 F7S days if they have a 100% duty
    percentage, 4 F7S days if 75% and 3 F7S days if 50%. This amount will be
    weighed, in case the crew will change his/her contract during the period.
    The days will be reduced proportionally with the amount of planned LOA.
    CR 473: new reducing activity LA48; reduction for LOA is calculated using
    previous year instead of F7S year."""
    def __init__(self, ent, year, data):
        """Define reducing activities, and self.hi and self.lo."""
        F7SCC.__init__(self, ent, year, data)
        self.reducing_activities = ('IL12', 'IL12R', 'IL14', 'IL14R', 'LA21',
                'LA42', 'LA44', 'LA47', 'LA48', 'LA51', 'LA61', 'LA62', 'LA63',
                'LA66', 'LA71', 'LA89', 'LA91', 'LA91R')
        self.hi = year
        self.lo = year.addyears(-1)

    def _increment(self):
        """Return number of F7S days. In this case the calculation is based on
        both the contract and planned LOA."""
        if not self.crewid in self.data.contracts:
            log.error("Crew with id %s does not have a valid entry in 'crew_contract'." % (self.crewid,))
            return 0
        d = {}
        for c in self.data.contracts[self.crewid]:
            if c.validto < self.lo or c.validfrom > self.hi:
                continue
            # If contract data is invalid (raises Exception), then
            # this is caught outside, crew will not get any F7S
            dutyperc = c.contract.dutypercent
            if dutyperc > 75:
                category = 1 # 5 F7S days per year
            elif dutyperc > 50:
                category = 2 # 4 F7S days per year
            else:
                category = 3 # 3 F7S days per year
            d[category] = d.get(category, 0) + time_util.overlap(c.validfrom, c.validto, self.lo, self.hi)
        # Convert all RelTime to int
        hi = int(self.hi)
        lo = int(self.lo)
        # Reduction factor = amount of "non-loa" time per year
        rf = float(hi - lo - self._reduce()) / (hi - lo)
        # Weighted amount of time
        wd = (5.0 * d.get(1, 0) + 4.0 * d.get(2, 0) + 3.0 * d.get(3, 0)) / (hi - lo)
        return math.ceil(rf * wd)


# F7SCrewDict ------------------------------------------------------------{{{2
class F7SCrewDict(dict):
    """A dictionary with crewid as key and where the value is one of the
    F7SCrewRecord classes above. The setting of items is overridden to be able
    to update crew with employment dates, and to make only one insertion per
    crew, regardless of how many crew_employment records where found in the
    interval."""
    def __init__(self, year, data):
        """Use only one instance of EntityConnection."""
        dict.__init__(self)
        self.year = year
        self.data = data

    def __setitem__(self, crewid, ent):
        """Contains an object factory for F7SCrewRecord classes."""
        if not crewid in self:
            try:
                country = ent.country.id
                class_ = self.data.get_class(ent.crewrank.maincat.id, ent.country.id)
                if class_ is not None:
                    dict.__setitem__(self, crewid, class_(ent, self.year, self.data))
            except Exception, e:
                raise
                log.error(e)


# F7SData ----------------------------------------------------------------{{{2
class F7SData:
    def __init__(self):
        self.ec = EC(TM.getConnStr(), TM.getSchemaStr())

    def get_class(self, cat, country):
        """Factory returning conversion classes. If no match found, then
        (implicitly) None is returned. This has to be handled by the class that
        is using this method."""
        # None for JP, CN, ...
        if cat == 'C':
            if country == "DK":
                return F7SCCDK
            elif country == "NO":
                return F7SCCNO
            elif country == "SE":
                return F7SCCSE
        elif cat == "F":
            if country == "NO":
                return F7SFD


# Increment_F7S ----------------------------------------------------------{{{2
class Increment_F7S:
    """Add F7S accounts for all crew."""
    
    def __init__(self, year, accountdate=None, data_class=F7SData):
        """Init EntityConnection, also set a reasonable search interval for
        employment records."""
        if not accountdate:
            accountdate = year
        self.tim = accountdate # bookingdate
        # See SASCMS-2482
        self.lo = year.addyears(-1)
        self.hi = year.addyears(1)
        self.data = data_class()

    def increment(self):
        """Search crew_employment, for each crew, if appropriate, create an
        item in the dict. Each object will take care of the increment, so that
        the different rules can apply to the different crew categories."""
        crewDict = F7SCrewDict(self.tim, self.data)
        for crew in TM.crew_employment.search("(&(validto>%s)(validfrom<%s))" % (self.lo, self.hi)):
            try:
                crewid = crew.crew.id
            except Exception, e:
                log.error(e)
                continue
            crewDict[crewid] = crew
        # This stuff is for performance reasons, to avoid scanning crew_contract thousands of times...
        self.data.contracts = {}
        for contract in TM.crew_contract.search("(&(validto>%s)(validfrom<%s))" % (self.lo, self.hi)):
            try:
                crewid = contract.crew.id
                _ = contract.contract.desclong # provoke to get possible referential errors
                _ = contract.contract.dutypercent # provoke to get possible referential errors
            except Exception, e:
                log.error(e)
                continue
            if crewid in self.data.contracts:
                self.data.contracts[crewid].append(contract)
            else:
                self.data.contracts[crewid] = [contract]
        for crewid in sorted(crewDict):
            try:
                crewDict[crewid].increment()
            except Exception, e:
                log.error(e)


# Increment F33 classes =================================================={{{1

# F33AbsenceMap ----------------------------------------------------------{{{2
class F33AbsenceMap(dict):
    """Mapping with Danish and Swedish pilots with VG contracts as keys. The
    values are time intervals where the crew member had LOA/illness."""
    def __init__(self, ec, hi, f33_crew, reducing):
        dict.__init__(self)
        # Mapping crew -> IntervalSet
        for ca in ec.crew_activity.search("et > %d AND st < %d" % (hi.addmonths(-4), hi)):
            if ca.crew in f33_crew and ca.activity in reducing:
                self.setdefault(ca.crew, time_util.IntervalSet()).add(
                        time_util.TimeInterval(ca.st, ca.et))


# Increment_F33 ----------------------------------------------------------{{{2
class Increment_F33(Conversion):
    """
    F33 Days
    --------
    * Valid for Danish and Swedish pilots only.
    * Crew with Regional Contract (RC) in Variable Group (VG) will get one F33
      day every fourth month.
    * Crew with VG (and not RC) will get one F33 day every third month.
    * VG is defined as having grouptype == 'V' in crew_contract.
    * RC is defined as having A/C qualification for small plane (in this case,
      only CJ (Bombardier CRJ) is regarded).
    * The day will not be given if crew had more than 30 days of
      Leave-of-Absence (LOA) the previous time period (tertile or quarter).
    * As LOA activities we count activities with activity group in:
      {'LOA'},           # SASCMS-2284, 2813: No more: 'OFD', 'MET', 'ILL'
      together with the following activities: {'MI', 'SD', 'GD'}.
    * UPDATE (SASCMS-1914): Algorithm updated to be able to handle crew that
      goes to or from variable group.
      - For each crew that has been in VG the past 4 months:
        + Count number of days crew has been in VG.
        + If number of days in VG less than total minus 30 days, no day will
          be awarded.
        + Check number of LOA/ILL days for crew.

    * This same concept and process is extended to Fix Group (FG) SKD: SASCMS-2690
    """
    
    def __init__(self, lastdate, accountdate):
        """Init EntityConnection, also set a reasonable search interval for
        employment records."""
        # F33 days will not be introduced until the 1st of January 2010, the
        # first days will be awarded after a quarter.
        self.turn_on_date = AbsTime(2010, 4, 1, 0, 0)
        # These are used to find interval where crew has valid contract.
        self.hi = lastdate.month_floor()
        if not accountdate:
            accountdate = self.hi
        Conversion.__init__(self, accountdate)
        # Use four months for preliminary searches.
        self.lo = self.hi.addmonths(-4)
        run_month = self.hi.split()[1] - 1
        # Only run for VG RC pilots every tertile
        self.block_for_rc = run_month % 4
        # Only run for VG Main pilots every quarter
        self.block_for_main = run_month % 3

    def increment(self):
        """Increment number of F33 days for selected crew. The job is run
        monthly, but some months we will just return."""

        # No point in closing EntityConnection in mirador, will be done by __del__
        ec = EC(TM.getConnStr(), TM.getSchemaStr())

        # Don't run this before turn_on_date!
        if self.hi < self.turn_on_date:
            log.warning("No F33 days will be awarded before %s. Returning and nothing saved!" % self.turn_on_date)
            return

        if self.block_for_rc and self.block_for_main:
            log.info("No F33 days will be awarded this month, since it's not a new quarter or tertile.")
            return
        
        runs = []
        
        if not self.block_for_main:
            runs.append(True)
        else:
            # No F33 for VG/Main pilots in FEB, MAR, MAY, JUN, AUG, SEP, NOV, DEC
            log.info("No F33 days will be awarded for pilots in group VG/Main this month.")
            
        if not self.block_for_rc:
            runs.append(False)
        else:
            # No F33 for VG/RC pilots in FEB, MAR, APR, JUN, JUL, AUG, OCT, NOV, DEC
            log.info("No F33 days will be awarded for pilots in group VG/RC this month.")
        
        for run_main in runs:
            if run_main:
                number_of_months = 3
            else:
                number_of_months = 4
            low_date = self.hi.addmonths(-number_of_months)
            ti = time_util.TimeInterval(low_date, self.hi)
            t_interval = time_util.IntervalSet([ti])
            t_days = (int(self.hi) - int(low_date)) / 1440
            log.debug("Running with interval %s, total %s days." % (ti, t_days))

            # Mapping of crewid's to time intervals with FG (FIXED Group contract only SKD)
            cat_reg_crew = {}
            if not run_main:
                cat_reg_crew = self._get_crew(['F'], ['SKD'])
            fg_crew = self._get_fg(cat_reg_crew)
            # mapping of crewid's to time intervals with VG (Variable Group contract)
            vg_crew = self._get_vg()
            # Merging vg_crew and fg_crew
            mg_crew = {}
            for vg_crewid in vg_crew.keys():
                mg_crew[vg_crewid] = vg_crew[vg_crewid]
                if fg_crew.has_key(vg_crewid):
                    mg_crew[vg_crewid] = mg_crew[vg_crewid].union(fg_crew[vg_crewid])
            for fg_crewid in fg_crew.keys():
                if not vg_crew.has_key(fg_crewid):
                    mg_crew[fg_crewid] = fg_crew[fg_crewid]

            # mapping of crewid's to time intervals with qualification CJ
            rc_crew = self._get_rc()
            # set of activity id's that may reduce F33 allocation.
            reducing = self._get_reducing()
            # mapping of crewid's to crew_employment entry for DK and SE Pilots in VG
            ce_map = self._get_ce_map(mg_crew)
            # Mapping f33crew -> number of LOA last 3/last 4
            absence_map = F33AbsenceMap(ec, self.hi, ce_map, reducing)
    
            for crewid in sorted(ce_map):
                # Interval of time periods crew has been SKD/SKS and pilot.
                emp_interval = time_util.IntervalSet([
                    time_util.TimeInterval(x.validfrom, x.validto) for x in ce_map[crewid]])
                if run_main:
                    # VG/Main, get number of days crew has been in VG (but not in RC)
                    # Use 'intersection' of the sets to get the period crew has
                    # been both pilot SKD/SKS and belongs to VG.
                    q_interval = mg_crew[crewid] & emp_interval
                    if crewid in rc_crew:
                        # Remove periods where crew has been 'RC'
                        q_interval -= rc_crew[crewid]
                    if not q_interval:
                        # Crew was RC all time, not qualified for Main
                        continue
                else:
                    if not crewid in rc_crew:
                        # Crew has never been RC within the past 4 months.
                        continue
                    q_interval = rc_crew[crewid] & mg_crew[crewid] & emp_interval
                q_days = sum([int(x.magnitude()) for x in (q_interval & t_interval)]) / 1440
                if q_days < t_days - 30:
                    log.debug("No F33 for %s, not qualified for F33 this period; qualified for %s/%s days." % (crewid, q_days, t_days))
                    continue
                # Now check for absence within q_interval
                if crewid in absence_map:
                    a_interval = q_interval - absence_map[crewid]
                else:
                    a_interval = q_interval
                a_days = sum([int(x.magnitude()) for x in (a_interval & t_interval)]) / 1440
                if a_days < t_days - 30:
                    # Number of active days too small.
                    log.debug("No F33 for %s, too much absence this period; active for %s/%s/%s days." % (crewid, a_days, q_days, t_days))
                    continue
                self._add_days(ce_map[crewid][-1])

    def _add_days(self, ce):
        """Add one F33 day if crew has not been absent more than 30 days in
        his/her interval."""
        amount = 100
        log.debug("F33: crew id=%s, rank=%s, region=%s, amount=%d" % (ce.crew.id,
            ce.crewrank.id, ce.region.id, amount))
        self.record(ce.crew.id, "F33", amount)
        
    def _get_crew(self, cat, reg):
        """Return mapping of contracts. Key
        is crewid and value is a list of crew ids."""
        crew_list = {}
        for ce in TM.crew_employment.search("(&(validto>%s)(validfrom<%s))" % (self.lo, self.hi)):
            try:
                crewid = ce.crew.id
                maincat = ce.crewrank.maincat.id
                region = ce.region.id
            except Exception, e:
                log.error(e)
                continue
            if maincat in cat and region in reg:
                crew_list[crewid] = crewid
        return crew_list

    def _get_ce_map(self, vg):
        """Return mapping of Danish and Swedish pilots with VG contracts. Key
        is crewid and value is a list of crew_employment records."""
        crew_map = {}
        for ce in TM.crew_employment.search("(&(validto>%s)(validfrom<%s))" % (self.lo, self.hi)):
            try:
                crewid = ce.crew.id
                maincat = ce.crewrank.maincat.id
                region = ce.region.id
            except Exception, e:
                log.error(e)
                continue
            if crewid in vg and maincat == 'F' and region in ('SKD', 'SKS'):
                crew_map.setdefault(crewid, []).append(ce)
        return crew_map
        
    def _get_rc(self):
        """Return mapping of crew with A/C qualification Regional Contract
        (RC), we define these as crew with qualification for small airplanes.
        Currently we only have Fokker 50 (F50, F5), Canadair Regional Jet (CRJ,
        CJ) and Dash 8 (Q400, Q4). Since F33 is only given to SKD and SKS crew,
        and Q400 has been phased out, we only need to check for qualification
        ACQUAL+CJ.
        The values of the mapping are the time intervals where the crew was
        belonging to segment 'RC'."""
        rc_crew = {}
        for entry in TM.crew_qualification_set[('ACQUAL', 'CJ')].referers('crew_qualification', 'qual'):
            if entry.validfrom < self.hi and entry.validto > self.lo:
                try:
                    rc_crew.setdefault(entry.crew.id, time_util.IntervalSet()).add(
                            time_util.TimeInterval(entry.validfrom, entry.validto))
                except Exception, e:
                    log.error("Could not add qualification '%s' [%s]." % (entry, e))
        return rc_crew

    def _get_reducing(self):
        """Return set of activity types that can reduce the allocation of F33
        days."""
        # MI, SD, GD will reduce
        reducing_set = set(['MI', 'SD', 'GD'])
        for entry in TM.activity_set:
            if entry.grp.id in ('LOA', ):  # SASCMS-2284, 2813: No more: 'OFD', 'MET', 'ILL'
                reducing_set.add(entry.id)
        return reducing_set

    def _get_fg(self, valid):
        """Return mapping of crew with "Fixed Group" contracts. The
        definition is that the contract should have grouptype 'F', 'FV' or 'X'.
        The values of the mapping are the time intervals where the crew was
        belonging to 'Fixed Group'. (SASCMS-2690 2010-11-09)"""
        fg_crew = {}
        for entry in TM.crew_contract.search(
            "(&(validfrom<%s)(validto>%s)(|(contract.grouptype=FV)(contract.grouptype=F)(contract.grouptype=X)))"%\
                                (self.hi, self.lo)):
            try:
                if valid.has_key(entry.crew.id):
                    fg_crew.setdefault(entry.crew.id, time_util.IntervalSet()).add(
                            time_util.TimeInterval(entry.validfrom, entry.validto))
            except Exception, e:
                log.error("Could not add contract data '%s' [%s]." % (entry, e))
        return fg_crew

    def _get_vg(self):
        """Return mapping of crew with "Variable Group" contracts. The
        definition is that the contract should have grouptype 'V'.
        The values of the mapping are the time intervals where the crew was
        belonging to 'Variable Group'."""
        vg_crew = {}
        for entry in TM.crew_contract.search("(&(validfrom<%s)(validto>%s)(contract.grouptype=V))" % (self.hi, self.lo)):
            try:
                vg_crew.setdefault(entry.crew.id, time_util.IntervalSet()).add(
                        time_util.TimeInterval(entry.validfrom, entry.validto))
            except Exception, e:
                log.error("Could not add contract data '%s' [%s]." % (entry, e))
        return vg_crew


# Convert_F3_to_F31 ======================================================{{{1
class Convert_F3_to_F31(Conversion):
    """ F3 to F31 conversion for long haul pilots. """

    def __init__(self, hi, lo=None, accountdate=None):
        if not accountdate:
            accountdate = hi
        Conversion.__init__(self, accountdate)
        self.hi = hi
        self.lo = lo

        # cache to indicate if crew is FD
        self.fd = FDCache(lo, hi)

        # cache to indicate if crew is Long Haul Pilot
        self.lh = LHCache(lo, hi)

    def convert(self):
        """ Create conversion records for each value in self.balance """
        balance = AccountBalanceDict("F3", self.hi, self.lo, filter=self.filter)
        for (id, value) in balance.iteritems():
            remove, add = self.func(value)
            self.record(id, "F3", -remove)
            self.record(id, "F31", add)
            log.debug("crew %s has %s on F3 account -> F3:-%s, F31:%s" % (id, value, remove, add))

    def func(self, x):
        """ Conversion function. """
        # Create five F31 for every three F3, but at least two F3 will have to
        # remain.
        d, m = divmod(x / 100.0, 3)
        if d <= 0:
            return 0, 0
        elif m >= 2:
            return int(300 * d), int(500 * d)
        elif d > 1:
            return int(300 * (d - 1)), int(500 *(d - 1))
        return 0, 0

    def filter(self, record): 
        """ Only convert for Flight Deck that is qualified for Long Haul. """
        return self.fd(record.crew.id, self.hi) and self.lh(record.crew.id, self.hi)


# Convert_F3_to_F3S ======================================================{{{1
class Convert_F3_to_F3S(Conversion):
    """ F3 to F3S conversion for pilots. """
    
    def __init__(self, hi, lo=None, accountdate=None):
        if not accountdate:
            accountdate = hi
        Conversion.__init__(self, accountdate)
        self.hi = hi
        self.lo = lo
        # Cache for flight crew look-up
        self.fd = FDCache(lo, hi)

    def convert(self):
        """ Create conversion records. """
        # Create F3 balance for each FD crew
        self.f3_balance = AccountBalanceDict("F3", self.hi, self.lo, filter=self.fd_filter)
        self.f3s_balance = AccountBalanceDict("F3S", self.hi, self.lo, filter=self.f3s_filter)

        for (id, f3) in self.f3_balance.iteritems():
            # Only remove F3 if crew got positive balance.
            if f3 > 0:
                f3s = self.f3s_balance.get(id, 0)
                (remove, add) = self.func(f3, f3s)
                self.record(id, "F3", -remove)
                self.record(id, "F3S", add)
                log.debug("crew %s: F3:%s, F3S:%s -> F3:-%s, F3S:%s" %
                          (id, f3, f3s, remove, add))

    def func(self, f3, f3s):
        """ Conversion is based on balance on both F3 and F3S accounts. """
        x = 0
        if f3 > 0: # Only take from F3 if balance is positive
            x = min(f3, max(0, 200 - f3s)) # F3S must be at most 200
        return (x, x)

    def fd_filter(self, record):
        """ Only convert for Flight crew. """
        return self.fd(record.crew.id, record.tim)

    def f3s_filter(self, record):
        """ Only add F3S entries for crew that has got F3 balance. """
        return record.crew.id in self.f3_balance
    
class Convert_BOUGHT_COMP_TO_F3(Conversion):
    """ BOUGHT_COMP converted to F3 (BOUGHT_COMP is also paid out in previous salary run). """
    
    def __init__(self, hi, lo=None, accountdate=None):
        if not accountdate:
            accountdate = hi
        Conversion.__init__(self, accountdate)
        self.hi = hi
        self.lo = lo
        log.info("Conversion BOUGHT_COMP -> F3 : %s-%s" % (lo, hi))

    def convert(self):
        """ Create conversion records. """
        # Create F3 balance for each FD crew
        self.bc_balance = AccountBalanceDict("BOUGHT_COMP", self.hi, self.lo)

        for (id, bal) in self.bc_balance.iteritems():
            if bal > 0:
                self.record(id, "F3", bal)
                log.info("  crew %s: BOUGHT_COMP balance: %f" % (id, bal/100.0))

class Convert_BOUGHT_COMP_F3S_TO_F3S(Conversion):
    """ BOUGHT_COMP_F3S converted to F3S. """
    
    def __init__(self, hi, lo=None, accountdate=None):
        if not accountdate:
            accountdate = hi
        Conversion.__init__(self, accountdate)
        self.hi = hi
        self.lo = lo
        log.info("Conversion BOUGHT_COMP_F3S -> F3S : %s-%s" % (lo, hi))

    def convert(self):
        """ Create conversion records. """
        # Create F3 balance for each FD crew
        self.bc_balance = AccountBalanceDict("BOUGHT_COMP_F3S", self.hi, self.lo)

        for (id, bal) in self.bc_balance.iteritems():
            if bal > 0:
                self.record(id, "F3S", bal)
                log.info("  crew %s: BOUGHT_COMP_F3S balance: %f" % (id, bal/100.0))

class Convert_BOUGHT_F3_TO_F3(Conversion):
    """ BOUGHT_F3 converted to F3 """

    def __init__(self, hi, lo=None, accountdate=None):
        if not accountdate:
            accountdate = hi
        Conversion.__init__(self, accountdate)
        self.hi = hi
        self.lo = lo
        log.info("Conversion BOUGHT_F3 -> F3 : %s-%s" % (lo, hi))

    def convert(self):
        """ Create conversion records. """
        # Create F3 balance for each crew
        self.bc_balance = AccountBalanceDict("BOUGHT_F3", self.hi, self.lo)

        prev_conv = AccountBalanceDict("BOUGHT_F3", self.hi + RelTime(1), self.hi)

        for crew in prev_conv:
            self.bc_balance[crew] = self.bc_balance.get(crew, 0) + prev_conv[crew]

        for (id, bal) in self.bc_balance.iteritems():
            if bal > 0:
                self.record(id, "F3", bal)
                log.info("  crew %s: BOUGHT_F3 balance: %f" % (id, bal / 100.0))

class Convert_BOUGHT_F3_2_TO_F3(Conversion):
    """ BOUGHT_F3 converted to F3 """

    def __init__(self, hi, lo=None, accountdate=None):
        if not accountdate:
            accountdate = hi
        Conversion.__init__(self, accountdate)
        self.hi = hi
        self.lo = lo
        log.info("Conversion BOUGHT_F3_2 -> F3 : %s-%s" % (lo, hi))

    def convert(self):
        """ Create conversion records. """
        # Create F3 balance for each crew
        self.bc_balance = AccountBalanceDict("BOUGHT_F3_2", self.hi, self.lo)

        prev_conv = AccountBalanceDict("BOUGHT_F3_2", self.hi + RelTime(1), self.hi)

        for crew in prev_conv:
            self.bc_balance[crew] = self.bc_balance.get(crew, 0) + prev_conv[crew]

        for (id, bal) in self.bc_balance.iteritems():
            if bal > 0:
                self.record(id, "F3", bal)
                log.info("  crew %s: BOUGHT_F3_2 balance: %f" % (id, bal / 100.0))

# public functions ======================================================={{{1
# NOTE: The public functions are intended to be "helpers", they use the default
# values that are used in batch jobs.
def F3_to_F31(hi=None, accountdate=None):
    """ Convert F3 -> F31 for longhaul pilots - to be run monthly.
    
    Longhaul qualification might change, so this function uses a default
    start interval, to avoid always including a historical change. 
    SASCMS-2127: This job should run on the 17th and including entries until
    the 17th.
    """
    if hi is None:
        hi = now().day_floor()
    log.info("Conversion F3 -> F31 will be run with booking date %s." % hi)
    Convert_F3_to_F31(hi, None, accountdate).convert()


def F3_to_F3S(hi=None, accountdate=None):
    """ Convert F3 to F3S for all pilots - to be run yearly. """
    if hi is None:
        hi = now().year_ceil()
    log.info("Conversion F3 -> F3S will be run with booking date %s." % hi)
    Convert_F3_to_F3S(hi, None, accountdate).convert()


def F7S_gain(hi=None, accountdate=None):
    """ Increment F7S for all crew - to be run yearly. """
    if hi is None:
        hi = now().year_ceil()
    log.info("F7S days will be incremented for year %s." % hi.split()[0])
    Increment_F7S(hi, accountdate).increment()


def F33_gain(hi=None, accountdate=None):
    """Increment F33 for pilots in VG - to be run monthly. 
    NOTE: Not all months will result in F33 days, only months that can be
    divided by three or four (start of new quarter or tertile)."""
    if hi is None:
        hi = now().month_floor()
    log.info("F33 days will be incremented for year %s and month %s." % hi.split()[:2])
    Increment_F33(hi, accountdate).increment()


def bought_sold_reset(hi=None, accountdate=None):
    """ Reset BOUGHT, BOUGHT_BL, and SOLD accounts - to be run monthly. """
    if hi is None:
        hi = now().month_floor()
    log.info("Reset job will run for entries before %s." % hi)
    Reset("BOUGHT", hi).reset()
    Reset("BOUGHT_BL", hi).reset()
    Convert_BOUGHT_COMP_TO_F3(hi).convert()
    Reset("BOUGHT_COMP", hi).reset()
    Convert_BOUGHT_COMP_F3S_TO_F3S(hi).convert()
    Reset("BOUGHT_COMP_F3S", hi).reset()
    Reset("BOUGHT_8", hi).reset()
    Reset("BOUGHT_FORCED", hi).reset()
    Convert_BOUGHT_F3_TO_F3(hi).convert()
    Reset("BOUGHT_F3", hi, None, REASONCODES['OUT_CONV']).reset()
    Convert_BOUGHT_F3_2_TO_F3(hi).convert()
    Reset("BOUGHT_F3_2", hi, None, REASONCODES['OUT_CONV']).reset()
    Reset("SOLD", hi).reset()

def reset_accounts(accounts, hi, reason=None, filter=None):
    """ Reset BOUGHT, BOUGHT_BL and SOLD accounts - to be run monthly. """
    if not hi:
        raise ValueError("Reset date must be specified")
    for account in accounts:
        reason_code = REASONCODES.get(reason, reason)
        log.info("Reset account %s before %s using (%s, %s)." % (account, hi, reason_code or "<default reason>", filter and "filter" or "no filter"))
        Reset(account, hi, reason=reason_code, filterfunc=filter).reset()


# bit ===================================================================={{{1
def bit():
    import time
    F7S_gain(AbsTime(*time.localtime()[:5]))


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    log.setLevel(logging.INFO)
    import profile
    profile.run("bit()")
    pass


# modeline ==============================================================={{{2
# vim: set fdm=marker fdl=1:
# eof
