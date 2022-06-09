
# [acosta:06/209@11:07] Added header
# [acosta:06/314@16:56] Updated to use extperkey.
# [acosta:08/284@15:20] Emergency fix for faulty CuiPublishRosters()

"""
This module handles interaction with the Rave interface.
"""

# imports ================================================================{{{1
import Cui
import carmensystems.rave.api as rave
#import carmusr.tracking.Publish as Publish
import carmusr.tracking.Rescheduling as Rescheduling
import utils.extiter as extiter
import utils.briefdebrief as briefdebrief
import utils.pubtools as pubtools

from AbsTime import AbsTime
from RelTime import RelTime
from tm import TM
from utils.paxfigures import CIOStatus
from utils.rave import RaveIterator, Entry, MiniEval
from utils.selctx import SingleCrewFilter, BasicContext
from utils.published_roster import RosterChanges
from carmusr.tracking.Publish import TRACKING_PUBLISHED_TYPE, TRACKING_DELIVERED_TYPE, TRACKING_INFORMED_TYPE


# setup logging =========================================================={{{1
import logging
log = logging.getLogger('cio.rv')


# Exception classes ======================================================{{{1

# NotFoundException ------------------------------------------------------{{{2
class NotFoundException(Exception):
    """ No rosters/dutypasses where found for the given id. """
    msg = ''
    def __init__(self, msg):
        self.msg = "No rosters found for crew with id = '%s'." % msg
        log.error(self.msg)
        Exception.__init__(self, self.msg)

    def __str__(self):
        return self.msg


# Classes for use with RaveIterator ======================================{{{1

# CrewInfo ---------------------------------------------------------------{{{2
class CrewInfo:
    """ Evaluated on leg """
    def __init__(self, date=None):
        if date is None:
            date = 'leg.%start_lt%'
        self.fields = {
            'id': 'report_crewlists.%crew_id%',
            'empno': 'report_crewlists.%%crew_empno_at_date%%(%s)' % (date),
            'rank': 'report_crewlists.%%crew_title_rank%%(%s)' % (date),
            'sub_category': 'report_crewlists.%%crew_sub_category%%(%s)' % (date),
            'logname': 'report_crewlists.%%crew_logname_at_date%%(%s)' % (date),
            'seniority': 'report_crewlists.%%crew_seniority%%(%s)' % (date),
            'base': 'report_crewlists.%%crew_base%%(%s)' % (date),
            'scc': 'report_crewlists.%%crew_scc%%(%s)' % (date),
            'mandatory_checkin': 'report_crewlists.%cio_mandatory_ci%',
            'end_utc': 'report_crewlists.%leg_end_utc%',
            'duty_code': 'report_crewlists.%duty_code%',
            'qual': 'report_crewlists.%%crew_ac_qlns%%(%s)' % (date),
            'prev_activity': 'report_crewlists.%pr_prev_activity%',
            'next_activity': 'report_crewlists.%pr_next_activity%',
            'checked_in': 'report_crewlists.%cio_crew_checked_in%',
        }


# FlightInfo -------------------------------------------------------------{{{2
class FlightInfo:
    """ Flight info, evaluated on leg """
    fields = {
        'actype': 'report_crewlists.%leg_ac_type%',
        'adep': 'report_crewlists.%leg_adep%',
        'ades': 'report_crewlists.%leg_ades%',
        'flight_name': 'report_crewlists.%leg_flight_name%',
        'sta_lt': 'report_crewlists.%leg_sta_lt%',
        'std_lt': 'report_crewlists.%leg_std_lt%',
        'udor': 'report_crewlists.%leg_udor%',
    }


# RevRosterInfo ----------------------------------------------------------{{{3
class RevRosterInfo(FlightInfo):

    class LegEntry(Entry):
        """Subclass Entry and supply keys() method that returns tuple used
        for comparisons."""
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
                self.adep, # From FlightInfo
                self.ades, # From FlightInfo
                self.meal_stop,
                self.dutycd
            )

    def __init__(self):
        self.fields.update({
            'actcode': 'report_crewlists.%pr_name%',
            'ci': 'report_crewlists.%checkin_time%',
            'dutycd': 'report_crewlists.%duty_code%',
            'has_checkin': 'report_crewlists.%leg_has_check_in%',
            'flight_id': 'report_crewlists.%leg_flight_id%',
            'is_flight': 'report_crewlists.%leg_is_flight%',
            'meal_stop': 'report_crewlists.%leg_is_meal_stop%',
            'meal_code': 'report_crewlists.%rm_meal_code%',
            'sta_hb': 'report_crewlists.%leg_sta_hb%',
            'sta_utc': 'report_crewlists.%leg_sta_utc%',
            'std_hb': 'report_crewlists.%leg_std_hb%',
            'std_utc': 'report_crewlists.%leg_std_utc%',
            # WP FAT Int 285 - stop duration should be scheduled stop.
            'stop': 'report_crewlists.%stop_duration_scheduled%',
            'task_code': 'report_crewlists.%task_code%',
            # To be able to extend list with briefing/debriefing
            'is_simulator': 'report_crewlists.%leg_is_simulator%',
            'checkin': 'report_crewlists.%leg_check_in%',
            'checkout': 'report_crewlists.%leg_check_out%',
        })


# NextDutyPassInfo -------------------------------------------------------{{{2
class NextDutyPassInfo(FlightInfo):
    """ Info for next duty pass, Used for Special Info, evaluated on a leg. """
    def __init__(self):
        self.fields.update(
        {
            'ca1': 'report_cio.%ca1%',
            'cc_need': 'report_cio.%cc_need%',
            'fd': 'leg.%flight_descriptor%',
            'number_of_cc': 'report_cio.%number_of_cc%',
            'rank': 'report_crewlists.%crew_title_rank%(leg.%start_utc%)',
            'reduced_need': 'studio_select.%reduced_need%',
            'jar_need_cc': 'crew_pos.%total_cabin_crew_jar_need%',
            'booked': 'crew_pos.%leg_booked_cc%',
        })


# RosterInfo -------------------------------------------------------------{{{2
class RosterInfo:
    """ Roster info evaluated on chain. """
    fields = {
        'id': 'crew.%id%',
        'now': 'fundamental.%now%',
        'now_cph': 'station_localtime("CPH", fundamental.%now%)',
        'estimated_et': 'checkinout.%estimated_et%',
        'estimated_st': 'checkinout.%estimated_st%',
        'extperkey': 'crew.%employee_number%',
        'logname': 'crew.%login_name%',
        'checked_in': 'report_crewlists.%cio_crew_checked_in%',
        'cio_status': 'checkinout.%cio_report%',
        'co_dutycd': 'report_cio.%co_dutycd%',
        'co_activityid': 'report_cio.%co_activityid%',
        'co_origsdt_utc': 'report_cio.%co_origsdt_utc%',
        'co_stnfr': 'report_cio.%co_stnfr%',
        'co_std': 'report_cio.%co_std%',
        'ci_std': 'report_cio.%ci_std%',
        'co_sta': 'report_cio.%co_sta%',
        'ci_sta': 'report_cio.%ci_sta%',
        'co_eta': 'report_cio.%co_eta%',
        'co_flight_name': 'report_cio.%co_flight_name%',
        'ci_flight_name': 'report_cio.%ci_flight_name%',
        'ci_to_ap_sby': 'report_cio.%ci_to_ap_sby%',
        'co_udor': 'report_cio.%co_udor%',
        'ci_udor': 'report_cio.%ci_udor%',
        'ci_checkin': 'report_cio.%ci_checkin%',
        'ci_actype': 'report_cio.%ci_actype%',
        'ci_pic_logname': 'report_cio.%ci_pic_logname%',
        'ci_ca1_logname': 'report_cio.%ci_ca1_logname%',
        'ci_deadhead': 'report_cio.%ci_deadhead%',
        'next_checkin': 'report_cio.%next_checkin%',
        'next_flight_name': 'report_cio.%next_flight_name%',
        'next_is_passive': 'report_cio.%next_is_passive%',
        'next_is_active_another_day':
        'report_cio.%next_is_active_another_day%',
        'next_req_cio': 'report_cio.%next_req_cio%',
        'next_std': 'report_cio.%next_std%',
        'next_udor': 'report_cio.%next_udor%',
        'next_is_pact': 'report_cio.%next_is_pact%',
        'f_loaded_data_period_start_utc': 'fundamental.%pp_start%', #BZ 38015
        'f_loaded_data_period_end_utc': 'fundamental.%pp_end%',
        'last_scheduled_time': 'report_cio.%last_scheduled_time%',
    }


# classes ================================================================{{{1

# ACrewList --------------------------------------------------------------{{{2
class ACrewList(list):
    """ Crew list and info about a flight. """

    # [acosta:08/168@14:39] Changed in connection with WP Cct 937 and according
    # to spec.
    format = "%-3.3s %-3.3s %-3.3s %-5.5s %-3.3s %-20.20s %-1.1s %-6.6s %5.5s %s"
    columns = ('CAT', 'SCC', 'DUT', 'EMPNO', 'B', 'NAME', ' ', 'QUAL', 'SENNO', '        ROSTER')
    header = format % columns

    def __init__(self, f):
        """ Create header from flight leg info. """
        list.__init__(self)
        self.flight = f
        self.flightindic = "%-20.20s     %s-%s    STD %s    STA %s    %s" % (
            "%s/%s" % (f.flight_name, str(f.udor).split()[0]),
            f.adep,
            f.ades,
            "%02d:%02d" % f.std_lt.split()[3:5],
            "%02d:%02d" % f.sta_lt.split()[3:5],
            f.actype,
        )

    def append(self, crew):
        """ Append a crew list row. """
        list.append(self, self.CrewObject(crew))

    def __str__(self):
        """ For basic tests. """
        return '\n'.join([self.flightindic, self.header] + [str(x) for x in self])

    class CrewObject:
        def __init__(self, c):
            self.__dict__ = c.__dict__

        def __str__(self):
            return ACrewList.format % (
                self.rank + self.sub_category,
                ("", "YES")[self.scc],
                self.duty_code,
                self.empno,
                self.base,
                self.logname,
                (" ", "+")[self.checked_in],
                self.qual.replace(' ',''),
                self.seniority,
                "%10s * %s" % (self.prev_activity, self.next_activity)
            )


# CrewList ---------------------------------------------------------------{{{2
class CrewList(list):
    """
    Create a crew list for the next leg in a roster.

    usage:
        cl = cio.rv.CrewList(id)
        for l in cl:
            print l.flightindic
            print l.header
            for row in l:
                print row

    """
    def __init__(self, id, all=False):
        list.__init__(self)
        if all: # Only used for testing.
            self.where_expr = 'report_cio.%until_next_checkout%'
        else:
            self.where_expr = 'report_cio.%is_next_active_flight%'
        ri = RaveIterator(RaveIterator.iter('iterators.roster_set', where='crew.%%id%% = "%s"' % (id)))
        li = RaveIterator(RaveIterator.iter('iterators.leg_set', where=self.where_expr), FlightInfo())
        ei = RaveIterator(RaveIterator.iter('equal_legs'))
        oi = RaveIterator(RaveIterator.iter('iterators.leg_set',
            where='fundamental.%is_roster%',
            sort_by='report_crewlists.%sort_key%'), CrewInfo())
        ri.link(li)
        li.link(ei)
        ei.link(oi)
        roster_set = ri.eval(SingleCrewFilter(id).context())
        try:
            roster = roster_set[0]
        except:
            raise NotFoundException(id)

        cio_status = CIOStatus()
        for this_leg in roster.chain():
            c = ACrewList(this_leg)
            for equal_leg_context in this_leg.chain():
                for other_leg in equal_leg_context.chain():
                    c.append(self.add_ci_status(cio_status(other_leg.id),
                        other_leg))
            if c:
                self.append(c)
        cio_status.close()

    def add_ci_status(self, status_rows, leg):
        """Modify the Entry object by adding an attribute 'checked_in', the
        value is decided by querying the database using an EntityConnection."""
        #leg.checked_in = False
        if leg.mandatory_checkin:
            # Only leg with mandatory check-in will have the marker.
            for row in status_rows:
                # Wanted to use ciostatus from cio.db, but that would create
                # a circular dependency, anyway the value of ciostatus.CI = 1
                if (row['st'] is not None 
                        and row['st'] <= int(leg.end_utc)
                        and row ['et'] is not None
                        and row['et'] >= int(leg.end_utc)
                        and row['status'] & 1):
                    # Had status CI and st < leg.end < et
                    leg.checked_in = True
                    break
        return leg

    def __str__(self):
        """ for Basic Tests """
        return '\n'.join([str(x) for x in self])


# EvalNextDutypass -------------------------------------------------------{{{2
class EvalNextDutypass(list):
    """
    Evaluate a number of Rave variables for each leg in next dutypass.  Used
    for flight messages (in cio.db)

    usage:
        ndp = cio.rv.EvalNextDutypass(id)
        for leg in ndp:
            ...
    """
    def __init__(self, id):
        list.__init__(self)
        ri = RaveIterator(RaveIterator.iter('iterators.roster_set', where='crew.%%id%%="%s"' % (id)))
        # [acosta:09/231@11:24] Updated to show info until next mandatory C/O.
        li = RaveIterator(
            RaveIterator.iter('iterators.leg_set',
                where=(
                    'report_cio.%until_next_checkout%',
                    'report_crewlists.%leg_is_flight%',
                    ),
                sort_by='leg.%start_lt%'),
            NextDutyPassInfo()
        )
        ri.link(li)
        rosters = ri.eval(SingleCrewFilter(id).context())
        try:
            self.extend(rosters[0].chain())
        except:
            raise NotFoundException(id)

    def __str__(self):
        """ for Basic Tests """
        return '\n'.join([str(x) for x in self])


# EvalRoster -------------------------------------------------------------{{{2
class EvalRoster:
    """
    Evaluate a number of roster variables for a crew.

    Usage:
       x = cio.rv.EvalRoster(crewid)
       if str(x.cio_status) == 'report_cio.ci':
          ...

    Will raise exception 'NotFoundException' if no rosters are found for the
    given crew id.
    """
    def __init__(self, id):
        cond = None
        ctx = 'sp_crew'
        if id:
            cond = 'crew.%%id%%="%s"' % id
            ctx = None
        ri = RaveIterator(
            RaveIterator.iter('iterators.roster_set', where=cond),
            RosterInfo()
        )
        
        rosters = ri.eval(ctx or SingleCrewFilter(id).context())
        try:
            self.__dict__ = rosters[0].__dict__
            self.rosters = rosters
            
        except:
            raise NotFoundException(id)

    def __str__(self):
        """
        For testing purposes. Prints out the values of all the fetched Rave
        variables.
        """
        return '\n'.join(["%-35s = %s" % (k, v) for (k, v) in self.__dict__.iteritems()])


# PassiveLegs ------------------------------------------------------------{{{2
class PassiveLegs(list):
    """
    Return a list of flightnumber/udor for each passive leg in the next duty.

    usage:
        pl = cio.rv.PassiveLegs(id)
        for leg in pl:
            ...
    """
    def __init__(self, id):
        list.__init__(self)
        self.id = id
        ri = RaveIterator(RaveIterator.iter('iterators.roster_set', where='crew.%%id%%="%s"' % (id)))
        li = RaveIterator(
            RaveIterator.iter('iterators.leg_set', where='report_cio.%is_deadhead_until_next_checkout%', 
                sort_by='leg.%start_UTC%'),
            {'flight_name': 'report_cio.%flight_name%', 'udor': 'leg.%udor%'}
        )
        ri.link(li)

        rosters = ri.eval(SingleCrewFilter(id).context())

        try:
            self.extend(rosters[0].chain())
        except:
            raise NotFoundException(id)

    def __str__(self):
        """ For Basic Tests """
        return '\n'.join([str(x) for x in self])


# PrelCA1 ----------------------------------------------------------------{{{2
class PrelCA1(list):
    """
    Return a list of flightnumber/udor for each leg where the crew member is
    assigned as C/A 1 in the next duty.

    usage:
        pl = cio.rv.PrelCA1(id)
        for leg in pl:
            ...
    """
    def __init__(self, id):
        list.__init__(self)
        self.id = id
        ri = RaveIterator(RaveIterator.iter('iterators.roster_set', where='crew.%%id%%="%s"' % (id)))
        li = RaveIterator(
            RaveIterator.iter('iterators.leg_set', where=(
                    'report_cio.%ca1% = crew.%id%', 
                    'report_crewlists.%crew_title_rank%(leg.%start_lt%) <> "AP"',
                    'report_cio.%until_next_checkout%'
                ), sort_by='leg.%start_UTC%'),
            {
                'flight_name': 'report_cio.%flight_name%', 
                'udor': 'leg.%udor%',
                'adep': 'leg.%start_station%',
                'ades': 'leg.%end_station%',
            }
        )
        ri.link(li)
        rosters = ri.eval(SingleCrewFilter(id).context())
        try:
            self.extend(rosters[0].chain())
        except:
            raise NotFoundException(id)

    def __str__(self):
        """ For Basic Tests """
        return '\n'.join([str(x) for x in self])


# Help classes for RevisedRosterInfo--------------------------------------{{{2

# DefaultDict ------------------------------------------------------------{{{2
class DefaultDict(dict):
    """For formatting with %(string)s. Return empty string if no item or value
    is None."""
    default_value = ''
    def __getitem__(self, k):
        v = dict.get(self, k, self.default_value)
        if v is None:
            return self.default_value
        return v


# time_tuple -------------------------------------------------------------{{{2
class time_tuple(tuple):
    """Convert AbsTime() to tuple (5 items). If flag 'end_time' is True and the
    time is 0:00 o'clock, present the time as previous day at 24 o'clock."""
    def __new__(cls, atime, end_time=False):
        t = atime.split()
        if end_time:
            if t[3:5] == (0, 0):
                # Use previous date at 24:00
                t = (atime - RelTime(1)).split()[:3] + (24, 0)
        return tuple.__new__(cls, t)


# SimBriefDebriefExtender ------------------------------------------------{{{2
class SimBriefDebriefExtender(briefdebrief.BriefDebriefExtender):
    times = (
        ('std_utc', 'sta_utc'), 
        ('std_hb', 'sta_hb'),
        ('std_lt', 'sta_lt'),
    )
    class Briefing(RevRosterInfo.LegEntry):
        def __init__(self, a):
            if not (a.is_simulator and int(a.checkin) > 0):
                raise briefdebrief.BriefDebriefException('No briefing')
            self.__dict__ = a.__dict__.copy()
            self.actcode = 'B' + a.actcode[1:]
            for s, e in SimBriefDebriefExtender.times:
                setattr(self, s, getattr(a, s) - a.checkin)
                setattr(self, e, getattr(a, s))

    class Debriefing(RevRosterInfo.LegEntry):
        def __init__(self, a):
            if not (a.is_simulator and int(a.checkout) > 0):
                raise briefdebrief.BriefDebriefException('No debriefing')
            self.__dict__ = a.__dict__.copy()
            self.actcode = 'D' + a.actcode[1:]
            for s, e in SimBriefDebriefExtender.times:
                setattr(self, s, getattr(a, e))
                setattr(self, e, getattr(a, e) + a.checkout)


# RosterIterator -----------------------------------------------------{{{3
class RosterIterator:
    """Iterate legs in one crew member's roster."""
    def __init__(self, crewid):
        self.scf = SingleCrewFilter(crewid)
        self.ri = extiter.ExtRaveIterator(
            RaveIterator.iter('iterators.roster_set', where=self.scf.asTuple()),
            modifier=SimBriefDebriefExtender)
        self.ri.link(LegIterator())

    def eval(self, type=None):
        try:
            return self.ri.eval(self.scf.context(type))[0]
        except:
            return []


# LegIterator --------------------------------------------------------{{{3
class LegIterator(RaveIterator):
    """Subclass RaveIterator to get a way of transforming records to tuples."""
    def __init__(self):
        # This day or later
        iterator = RaveIterator.iter('iterators.leg_set',
                where=(
                    'round_down(leg.%start_utc%, 24:00) >= round_down(fundamental.%now%, 24:00)',
                    'leg.%end_utc% <= default(report_cio.%last_scheduled_time%, fundamental.%pp_end%)',
                ))
        RaveIterator.__init__(self, iterator, RevRosterInfo())

    def create_entry(self):
        """Important extension to RaveIterator."""
        return RevRosterInfo.LegEntry()


# RevisedRosterInfo ------------------------------------------------------{{{2
class RevisedRosterInfo(list):
    """Formatted information showing differences between original roster and
    revised roster.

    Usage:
        ri = rv.RevisedRosterInfo(self.id, self.r.now)
        if ri:
            if ri.last_created is not None:
                print ri.last_created
            for duty in ri:
                period_start, period_end = duty.interval
                print duty.original_roster
                print duty.header
                for row in duty:
                    print row
            ri.setDelivered()
    """
    def __init__(self, id, now, from_state=TRACKING_DELIVERED_TYPE, to_state=TRACKING_PUBLISHED_TYPE):
        list.__init__(self)
        self.id = id
        self.now = now
        roster_changes = RosterChanges(RosterIterator(id), from_state, to_state)
        self.rows, self.last_created = revision_info(id, now, roster_changes)
        try:
            self.max_time = AbsTime(roster_changes.max_time)
        except:
            log.warning("Could not find largest date for publishing. Has the actual period been published in Rostering?")
            self.max_time = None
        for interval, original, revised in roster_changes:
            self.append(self.RevisedRosterMessage(interval, original, revised,
                roster_changes.changed_set))

    def setDelivered(self):
        """Mark notification(s) as delivered."""
        for x in self.rows:
            x.delivered = self.now

    class RevisedRosterMessage:
        """Take care of formatting of the final roster message."""
        format  = ("%(wd)-4.4s  %(ci)-6.6s  %(mark)-4s%(duty)-8.8s    "
                "%(dep)3.3s  %(std)4.4s  %(sta)4.4s  %(arr)3.3s    "
                "%(ac)4.4s %(stop)4.4s %(meal)s")
        header = format % DefaultDict(wd='DAY', ci='C/I', mark='DUTY', dep='DEP',
                std='STD', sta='STA', arr='ARR', ac='A/C', stop='STOP', meal='MS')

        def __init__(self, interval, original, revised, changed):
            self.interval = interval
            self.original = original
            self.revised = revised
            self.changed = changed
            self.original_roster = self.packed(original)

        def packed(self, o):
            olen = len(o)
            L = []
            for i in xrange(0, olen):
                ac = o[i].actcode
                if i > 0:
                    restdays = int(o[i].std_hb) / 1440 - int(o[i - 1].std_hb) / 1440
                    for j in xrange(0, restdays):
                        L.append('/')
                actdays = reduce(lambda a, b: int(b) / 1440 - int(a) / 1440, o[i].interval())
                # Take care of activities spanning multiple days.
                if actdays > 1:
                    if ac.endswith('/ -'):
                        L.append(ac.split('/')[0] + '/')
                    else:
                        L.append(ac)
                    for j in xrange(1, actdays):
                        if ac.endswith('/ -'):
                            L.append('-')
                        else:
                            L.append(o[i].actcode)
                        L.append('/')
                else:
                    L.append(ac)
            return ' '.join(L)

        def __iter__(self):
            """Return iterator over list of formatted lines."""
            L = []
            prev_date = (0, 0, 0)
            for f in self.revised:
                t_std = f.std_lt
                t_sta = f.sta_lt
                duty = f.actcode
                dep = f.adep
                arr = f.ades
                if f.is_flight:
                    ac = f.actype
                    if f.stop is None:
                        stop = ""
                    else:
                        stop = "%02d%02d" % f.stop.split()[:2]
                    meal = ('', 'Y')[bool(f.meal_stop)]
                else:
                    ac = stop = meal = ""
                    if (int(f.std_hb), int(f.sta_hb)) != f[:2]:
                        # Update start/end times for base activities
                        # NOTE: This will not work well for base activity in
                        # different timezone from homebase and we begin or
                        # leave summer time where summer time shift at home
                        # base differs from local summer time shift.
                        t_std = f.std_lt + (AbsTime(f[0]) - f.std_hb)
                        t_sta = f.sta_lt + (AbsTime(f[1]) - f.sta_hb)
                ci = mark = ''
                if f in self.changed:
                    mark = '-->'
                if f.has_checkin:
                    ci = "(%02d%02d)" % f.ci.split()[3:5]

                # Correction for endtime at 0:00
                std = time_tuple(t_std)
                sta = time_tuple(t_sta, end_time=True)

                if std[:3] != prev_date:
                    # New day, print weekday and day of month
                    wd = "%2.2s%02d" % (self.weekday(std), std[2])
                else:
                    wd = ""
                prev_date = std[:3]

                if std[:3] != sta[:3]:
                    # Activity spans several days - add two rows
                    L.append(self.format % DefaultDict(wd=wd, ci=ci, mark=mark,
                        duty=duty, dep=dep, std=("%02d%02d" % std[3:5])))
                    # Weekday will always be printed since new day by definition.
                    L.append(self.format % DefaultDict(
                        wd="%2.2s%02d" % (self.weekday(sta), sta[2]), 
                        sta=("%02d%02d" % sta[3:5]), arr=arr, stop=stop,
                        meal=meal))
                else:
                    L.append(self.format % DefaultDict(wd=wd, ci=ci, mark=mark,
                        duty=duty, dep=dep, std=("%02d%02d" % std[3:5]),
                        sta=("%02d%02d" % sta[3:5]), arr=arr, stop=stop,
                        meal=meal))

                # Add 'meal activity' if required
                if (f.is_flight and f.meal_code is not None and
                        f.meal_code.strip(', ') != ''):
                    # All fields empty, except for meal code
                    L.append(self.format % DefaultDict(meal=f.meal_code))

            return iter(L)

        def weekday(self, date_tuple):
            """Return day of week."""
            how = AbsTime(*(date_tuple[:3] + (0, 0))).time_of_week().split()[0]
            return ('MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU')[how // 24]

        def __str__(self):
            """For tests."""
            return '\n'.join((
                '---',
                str(self.interval),
                'original:',
                '\n'.join([' - %s' % x for x in self.original]),
                'revised:',
                '\n'.join([' - %s' % x for x in self.revised]),
            ))


# functions =============================================================={{{1

# bit --------------------------------------------------------------------{{{2
def bit():
    """ Built-In Test. """
    #print "--- EvalRoster ---"
    #print EvalRoster(x)
    #print "--- EvalNextDutyPass ---"
    #print EvalNextDutypass(x)
    #print "--- Passive legs ---"
    #print PassiveLegs(x)
    #print "--- CrewList Next leg ---"
    #print CrewList(x)
    #print "--- CrewList legs in next duty-pass ---"
    #print CrewList(x, all=True)
    print PrelCA1('15703')
    x = RevisedRosterInfo('34353')
    for msg in x:
        print "ORIGINAL ROSTER", msg.interval
        print msg.original_roster
        print msg.header
        for row in msg:
            print row


# extperkey2id -----------------------------------------------------------{{{2
def extperkey2id(extperkey):
    """ Return crew id for a given employment number """
    return rave.eval('sp_crew', 'crew.%%extperkey_to_id_at_date%%("%s", fundamental.%%now%%)' % (extperkey))[0]


def getEqualLegsCrew(crewid,legFilter='',equalLegFilter=''):
    """ Return crew which shares same leg as crewid and which fulfills the filter statements """
    if BasicContext().isRS:
        ctx_type = None # In RS mode, the PUBLISHED roster is the default.
    else:
        ctx_type = TRACKING_PUBLISHED_TYPE

    context = SingleCrewFilter(crewid).context(ctx_type)

    li = RaveIterator(RaveIterator.iter('iterators.leg_set', where=legFilter))
    ei = RaveIterator(RaveIterator.iter('equal_legs'))
    oi = RaveIterator(RaveIterator.iter('iterators.leg_set', where=equalLegFilter), {'crewid' : 'crew.%id%'})
    li.link(ei)
    ei.link(oi)

    crewLegs = li.eval(context)

    crewlist = []
    for crewLeg in crewLegs:
        for equal_leg in crewLeg.chain():
            for roster in equal_leg.chain():
                crewlist.append(roster.crewid)

    # Get unique crewids
    crewlist = list(set(crewlist))
    return crewlist

# publish ----------------------------------------------------------------{{{2
def publish(crewid, st_utc, et_hb, equalLegsCrewlist=None):
    """Use external modules to publish within interval."""
    # st is in UTC, et is in HB time
    st_hb, et_utc = rave.eval('report_cio.%%utc_to_hb%%("%s", %s)' % (crewid, st_utc),
            'report_cio.%%hb_to_utc%%("%s", %s)' % (crewid, et_hb))
    # Note: Publication requires start and end times to be UTC, rescheduling
    # wants to have home base dates!
    pubtools.copy_tags(crewid, st_utc, et_utc, TRACKING_PUBLISHED_TYPE,
            (TRACKING_INFORMED_TYPE, TRACKING_DELIVERED_TYPE))
    # When running in interactive-studio (test mode), the current context is
    # "Latest", but we want the rescheduling info to be based on the PUBLISHED
    # roster that just has been informed. 
    if BasicContext().isRS:
        ctx_type = None # In RS mode, the PUBLISHED roster is the default.
        publishType = BasicContext().publishType
    else:
        ctx_type = TRACKING_PUBLISHED_TYPE
        publishType = TRACKING_PUBLISHED_TYPE

    if equalLegsCrewlist:
        equalLegsCrewlist.append(crewid)
        Cui.CuiLoadPublishedRosters(Cui.gpc_info, equalLegsCrewlist, publishType)

    Rescheduling.publish(start_date=st_hb.day_floor(), end_date=et_hb.day_floor(),
                         context=SingleCrewFilter(crewid).context(ctx_type),
                         sel_mode=Rescheduling.INFORM_ALL, freeze_x_flag=True)


# revision_info ----------------------------------------------------------{{{2
def revision_info(id, now, roster_changes):
    """Return rows (for update) and when roster was updated last (a string or
    None)."""
    rows = []
    last_created = None
    # Get information about last_created and last_created_by from table
    # 'crew_notification' in model.
    crew_ref = TM.crew[(id,)]
    dates = []
    try:
        # roster_changes is a list of tuples: (interval, original, revised)
        max_date = max(x[0].last for x in roster_changes)
    except:
        max_date = now
    for r in crew_ref.referers('crew_notification', 'crew'):
        if r.typ.subtype == 'Assignment':
            if r.st < max_date:
                dates.append(r.created)
                if r.delivered is None:
                    rows.append(r)

    # Returns a sorted list of dates,... 
    publ = rave.eval(SingleCrewFilter(id).context(),
                               rave.foreach("iterators.leg_set", "published_time"))[0]

    if publ is not None:
        _, publ = publ[-1] # Pick out the last date in the list (tuple).
        if publ is not None:
            dates.append(publ)
            log.info("Had to use roster publish date for crew '%s'." % id)

    dates.sort()

    try:
        # Use latest change date (from activities and/or published presented to crew).
        last_created = str(dates[-1])
    except Exception, e:
        log.warning('Last created was not filled in.')
        
    return rows, last_created


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run Built-In Test """
    #import profile
    #profile.run("bit()")

    print CrewList("34359")


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
