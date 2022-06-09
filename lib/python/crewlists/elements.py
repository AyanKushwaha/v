# changelog {{{2
# [acosta:06/262@14:56] First version
# [acosta:06/270@13:41] Changed almost all attributes to elements.
# [acosta:07/094@17:13] Restructured code, introduced Reply and ReplyError objects.
# [acosta:07/095@10:12] Broke out replyBody code, since it is common for several reports.
# [acosta:07/277@14:29] Added dummy_reply to always give some kind of XML structure back.
# [acosta:07/292@10:22] Fix for Bugzilla #20531
# }}}

"""
This module contains code that is common for some reports that have 'replyBody'
as their XML root element.
    CrewList
    CrewBasic
    CrewRoster
    CrewFlight
    FutureActivities
    DutyCalculation
"""

# imports ================================================================{{{1
import crewlists.status as status
import utils.xmlutil as xml
import utils.briefdebrief as breifdebrief # SKPROJ-170 - extiter -> briefdebrief as extiter  creates dependencies to rave which causes DIG to spasm out.
import traceback

from crewlists.replybody import Reply, ReplyError, schema_version
from utils.xmlutil import XMLElement
from utils.divtools import default
from AbsTime import AbsTime
from RelTime import RelTime
from Airport import Airport
from copy import copy


# exports ================================================================{{{1
__all__ = ['report', 'dummy_reply']


# public functions ======================================================={{{1

# report -----------------------------------------------------------------{{{2
def report(a):
    """
    Return an XML-formatted string.

    The indata parameter 'a' is an 'Activity' object.
    report and dummy_reply have to be in sync.
    """
    request = a.inparams.requestName
    if request == 'CrewList':
        reply = crewListReply(a)
    elif request == 'CrewFlight':
        reply = crewFlightReply(a)
    elif request == 'CrewRoster':
        reply = crewRosterReply(a)
    elif request == 'CrewBasic':
        reply = crewBasicReply(a)
    elif request == 'FutureActivities':
        reply = crewPreActivityReply(a)
    elif request == 'DutyCalculation':
        reply = dutyCalculationReply(a)
    elif request == 'CheckInOut':
        reply = CheckInOut(a.header, a)
        if not a.ok():
            raise ReplyError(request, a.header.mesno, payload=reply)
    else:
        raise ReplyError(request, status.REPORT_NOT_FOUND)

    return str(Reply(request, payload=reply))


# dummy_reply ------------------------------------------------------------{{{2
def dummy_reply(request, inparams=None):
    """
    Return an empty XML structure, based on the "real" implementation, but with
    all dummy values (empty tags).
    All possible reports in report have to be mimicked here.
    """
    if request == 'CrewList':
        reply = XMLElement('crewListReply', crewListActivity(VoidActivity(request, inparams), VoidIterator()))
    elif request == 'CrewFlight':
        reply = XMLElement('crewFlightReply', crewFlightInfo(VoidActivity(request, inparams), VoidIterator()))
    elif request == 'CrewRoster':
        reply = XMLElement('crewRosterReply', crew(VoidActivity(request, inparams), VoidIterator()))
    elif request == 'CrewBasic':
        reply = XMLElement('crewBasicReply', crew(VoidActivity(request, inparams), VoidIterator()))
    elif request == 'FutureActivities':
        reply = XMLElement('crewPreActivityReply', crew(VoidActivity(request, inparams), VoidIterator()))
    elif request == 'DutyCalculation':
        reply = XMLElement('dutyCalculationReply', crewLegalityInfo(VoidActivity(request, inparams), VoidIterator()))
    elif request == 'CheckInOut':
        reply = CheckInOut(VoidIterator(), VoidIterator())
    else:
        reply = ''
    return reply


# getNumberOfDays --------------------------------------------------------{{{2
def getNumberOfDays(st, et):
    """ Returns number of days for multi-day activitiy """
    diff = et.day_floor() - st.day_floor()
    days = diff.split()[0] / 24
    if days == 0:
        days = 1
    return days


# isEmptyMealCode --------------------------------------------------------{{{2
def isEmptyMealCode(mealcode):
    if mealcode is None:
        return True
    if isinstance(mealcode, VoidValue):
        return True
    if mealcode.strip(', ') == '':
        return True
    return False


# Simulator briefing and debriefing ======================================{{{1

# SimBriefDebriefExtender ------------------------------------------------{{{2
class SimBriefDebriefExtender(breifdebrief.BriefDebriefExtender):
    """Adds SIM briefing / debriefing."""
    times = (
        ('std_utc', 'sta_utc'), ('std_lt', 'sta_lt')
    )

    fields = {
        'is_simulator': 'report_crewlists.%leg_is_simulator%',
        'checkin': 'report_crewlists.%leg_check_in%',
        'checkout': 'report_crewlists.%leg_check_out%',
    }

    class Briefing:
        def __init__(self, a):
            if not (a.is_simulator and int(a.checkin) > 0):
                raise breifdebrief.BriefDebriefException('No briefing')
            self.__dict__ = a.__dict__.copy()
            self.taskcode = 'B' + a.taskcode[1:]
            self.stop_duration = RelTime(0)
            self.crewlist_allowed = False
            for s, e in SimBriefDebriefExtender.times:
                if hasattr(a, s):
                    setattr(self, s, getattr(a, s) - a.checkin)
                    setattr(self, e, getattr(a, s))

    class Debriefing:
        def __init__(self, a):
            if not (a.is_simulator and int(a.checkout) > 0):
                raise breifdebrief.BriefDebriefException('No debriefing')
            self.__dict__ = a.__dict__.copy()
            self.taskcode = 'D' + a.taskcode[1:]
            try:
                if int(a.stop_duration) > 0:
                    self.stop_duration = a.stop_duration - a.checkout
                    a.stop_duration = RelTime(0)
            except:
                pass
            self.crewlist_allowed = False
            for s, e in SimBriefDebriefExtender.times:
                if hasattr(a, e):
                    setattr(self, s, getattr(a, e))
                    setattr(self, e, getattr(a, e) + a.checkout)


# Void values for generating empty replies in case of error =============={{{1

# VoidValue --------------------------------------------------------------{{{2
class VoidValue:
    """ Behaves like 'nothing' for most uses. """
    def __init__(self, name=None):
        """
        Not used right now, could be used to try to find out type of a value
        by looking at the attribute name.
        """
        self.name = name

    def __str__(self):
        return ""

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def split(self, *a, **k):
        if len(a) > 0: # like in "848 / 333".split("/")
            return ""
        else: # like AbsTime("20071003 10:10").split()
            class VoidTimeTuple(tuple):
                """
                If more than two items are requested, return something that mimics
                AbsTime().split()[:x].
                Otherwise mimic RelTime((0, 0)).
                """
                def __new__(cls, *a, **k):
                    """ Note, tuple is immutable, we have to use '__new__'. """
                    return tuple.__new__(cls, (1, 1, 1, 0, 0))

                def __getslice__(self, i, j, *a, **k):
                    if j > 2:
                        return tuple.__getslice__(self, i, j, *a, **k)
                    else:
                        return (0, 0)[i:j]
            return VoidTimeTuple()

    def __add__(self, other):
        return 0

    def __div__(self, other):
        return 0.0


# VoidIterator -----------------------------------------------------------{{{2
class VoidIterator(VoidValue):
    """
    Dummy 'RaveIterator'.
    Always return 'VoidValue' for all attributes.
    The chain() method returns a list containing a single VoidIterator.
    """
    def __getattr__(self, attr):
        return VoidValue(attr)

    def __iter__(self):
        return iter([VoidIterator()])

    def chain(self, *a, **k):
        return [VoidIterator()]


# VoidActivity -----------------------------------------------------------{{{2
class VoidActivity:
    """
    Mimic the reports' 'Activity' objects, but let the input data and the
    iterator be VoidIterators.
    """
    def __init__(self, requestName=None, inparams=None):
        self.iterator = VoidIterator()
        if inparams is None:
            self.inparams = VoidIterator()
            self.inparams.requestName = requestName
        else:
            self.inparams = inparams

    def paxinfo(self, *a, **k):
        return VoidIterator()

    def cioinfo(self, *a, **k):
        return VoidIterator()

    def delayinfo(self, *a, **k):
        return VoidIterator()


# Field definitions for RaveIterator ====================================={{{1
# These classes are used by the RaveIterator utility.

# CrewInfo ---------------------------------------------------------------{{{2
class CrewInfo:
    """
    Collects info for a crew.

    These variables can be evaluated on level chain.
    """
    def __init__(self, searchdate='fundamental.%now%'):
        """
        The searchdate will give rank, base, etc. at a given date.
        """
        self.fields = {
            'id': 'report_crewlists.%crew_id%',
            'seniority': 'report_crewlists.%%crew_seniority%%(%s)' % (searchdate),
            'empno': 'report_crewlists.%%crew_empno_at_date%%(%s)' % (searchdate),
            'sex': 'report_crewlists.%crew_gender%',
            'gn': 'report_crewlists.%crew_gn%',
            'sn': 'report_crewlists.%crew_sn%',
            'logname': 'report_crewlists.%%crew_logname_at_date%%(%s)' % (searchdate),
            'company':  'report_crewlists.%%crew_company%%(%s)' % (searchdate),
            'base': 'report_crewlists.%%crew_base%%(%s)' % (searchdate),
            'main_rank': 'report_crewlists.%%crew_main_rank%%(%s)' % (searchdate),
            'title_rank': 'report_crewlists.%%crew_title_rank%%(%s)' % (searchdate),
            'sub_category': 'report_crewlists.%%crew_sub_category%%(%s)' % (searchdate),
            'civic_station': 'report_crewlists.%%crew_civic_station%%(%s)' % (searchdate),
            'station': 'report_crewlists.%%crew_station%%(%s)' % (searchdate),
            'ac_qlns': 'report_crewlists.%%crew_ac_qlns%%(%s)' % (searchdate),
            'group_type': 'report_crewlists.%%crew_group_type%%(%s)' % (searchdate),
            'scc': 'report_crewlists.%%crew_scc%%(%s)' % (searchdate),
            'line_check': 'report_crewlists.%%crew_line_check%%(%s)' % (searchdate),
            'released_until': 'report_crewlists.%released_until%',
        }


# CrewInfoForLeg ---------------------------------------------------------{{{2
class CrewInfoForLeg(CrewInfo):
    """
    These variables cannot be evalutated on level chain.
    """
    def __init__(self, date='fundamental.%now%'):
        CrewInfo.__init__(self, date)
        self.fields.update({
            'checkedin': 'report_crewlists.%cio_duty_crew_checked_in%',
            'dutycode': 'report_crewlists.%duty_code%',
            'prev_duty': 'report_crewlists.%pr_prev_duty%',
            'next_duty': 'report_crewlists.%pr_next_duty%',
            'prev_activity': 'report_crewlists.%pr_prev_activity%',
            'next_activity': 'report_crewlists.%pr_next_activity%',
            'next_flight_id': 'report_crewlists.%next_flight_id%',
            'next_flight_udor': 'report_crewlists.%next_flight_udor%',
            'next_flight_depsta': 'report_crewlists.%next_flight_depsta%',
            'next_flight_arrsta': 'report_crewlists.%next_flight_arrsta%',
            'next_flight_std_utc': 'report_crewlists.%next_flight_std_UTC%',
            'next_flight_sta_utc': 'report_crewlists.%next_flight_sta_UTC%',
            'next_flight_std_lt': 'report_crewlists.%next_flight_std_lt%',
            'next_flight_sta_lt': 'report_crewlists.%next_flight_sta_lt%',
            'last_flown': 'report_crewlists.%last_flown_date%',
        })


# CrewInfoForLegWithRoster -----------------------------------------------{{{2
class CrewInfoForLegWithRoster(CrewInfoForLeg):
    def __init__(self, date='fundamental.%now%', roster_start='fundamental.%pp_start%', roster_end='fundamental.%pp_end%'):
        CrewInfoForLeg.__init__(self, date)
        self.fields.update({
            'released_until': 'report_crewlists.%released_until%',
            'packed_roster': 'report_crewlists.%%pr_packed_roster_relative%%(%s, %s)' % (roster_start, roster_end),
        })


# CrewInfoLegality -------------------------------------------------------{{{2
class CrewInfoLegality:
    # evaluated on roster
    def __init__(self, startdate='fundamental.%pp_start%', enddate='fundamental.%pp_end%'):
        self.fields = {
            'agreement_name': 'report_crewlists.%agreement_name%',
            'packed_roster': 'report_crewlists.%%pr_packed_roster%%(%s, %s)' % (startdate, enddate),
        }

# DocumentInfo -----------------------------------------------------------{{{2
class DocumentInfo:
    """
    Collects document info for a crew.
    """
    fields = {
        'typ': 'report_crewlists.%doc_typ%',
        'subtype': 'report_crewlists.%doc_subtype%',
        'docno': 'report_crewlists.%doc_docno%',
        'validto': 'report_crewlists.%doc_validto%',
    }


# DutyInfo ---------------------------------------------------------------{{{2
class DutyInfo:
    """
    Info used for dutycalculations.
    """
    fields = {
        'acc_fatigue1': 'report_crewlists.%acc_fatigue_1x24%',
        'acc_fatigue': 'report_crewlists.%acc_fatigue%',
        'acc_level_of_fatigue': 'report_crewlists.%acc_level_of_fatigue%',
        'active_landings': 'report_crewlists.%active_landings_in_duty%',
        'ci_time': 'report_crewlists.%ci_time%',
        'co_time': 'report_crewlists.%co_time%',
        'dut1': 'report_crewlists.%dut1%',
        'dut1B': 'report_crewlists.%dut1B%',
        'dut1F': 'report_crewlists.%dut1F%',
        'dut7B': 'report_crewlists.%dut7B%',
        'dut7': 'report_crewlists.%dut7%',
        'dut7Facc': 'report_crewlists.%dut7Facc%',
        'dut7F': 'report_crewlists.%dut7F%',
        'dut_night': 'report_crewlists.%dut_night%',
        'dutP': 'report_crewlists.%dutP%',
        'end_lt': 'report_crewlists.%duty_end_lt%',
        'fatigue': 'report_crewlists.%fatigue%',
        'level_of_fatigue': 'report_crewlists.%level_of_fatigue%',
        'is_long_term_rest': 'report_crewlists.%long_term_rest%',
        'max_dut1': 'report_crewlists.%max_dut1%',
        'max_dut7': 'report_crewlists.%max_dut7%',
        'max_dutP': 'report_crewlists.%max_dutP%',
        'off_duty_station': 'report_crewlists.%duty_off_duty_station%',
        'points_passive': 'report_crewlists.%points_passive%',
        'points7B': 'report_crewlists.%points_7B%',
        'points7F': 'report_crewlists.%points_7F%',
        'points7P': 'report_crewlists.%points_7P%',
        'points7': 'report_crewlists.%points_7%',
        # 'points_max7': 'report_crewlists.%points_max7%',
        # 'points_max': 'report_crewlists.%points_max%',
        # 'points_rest': 'report_crewlists.%points_rest%',
        'seq_no': 'report_crewlists.%seq_no%',
        'slip': 'report_crewlists.%slip%',
        'start_lt': 'report_crewlists.%duty_start_lt%',
        'time_off': 'report_crewlists.%time_off%',
        'time_off_last_24': 'report_crewlists.%time_off_last_24%',
        'time_off_min': 'report_crewlists.%time_off_min%',
    }


# FlightInfo -------------------------------------------------------------{{{2
class FlightInfo:
    """
    Collects info for a leg.
    """
    fields = {
        'id': 'report_crewlists.%leg_flight_id%',
        'udor': 'report_crewlists.%leg_udor%',
        'legno': 'report_crewlists.%leg_legno%',
        'sumlegs': 'report_crewlists.%num_legs_above%',
        'depsta': 'report_crewlists.%leg_adep%',
        'arrsta': 'report_crewlists.%leg_ades%',
        'end_country': 'report_crewlists.%leg_end_country%',
        'std_utc': 'report_crewlists.%leg_std_utc%',
        'sta_utc': 'report_crewlists.%leg_sta_utc%',
        'std_lt': 'report_crewlists.%leg_std_lt%',
        'sta_lt': 'report_crewlists.%leg_sta_lt%',
        'atd_utc': 'report_crewlists.%leg_atd_utc%',
        'ata_utc': 'report_crewlists.%leg_ata_utc%',
        'atd_lt': 'report_crewlists.%leg_atd_lt%',
        'ata_lt': 'report_crewlists.%leg_ata_lt%',
        'etd_utc': 'report_crewlists.%leg_etd_utc%',
        'eta_utc': 'report_crewlists.%leg_eta_utc%',
        'etd_lt': 'report_crewlists.%leg_etd_lt%',
        'eta_lt': 'report_crewlists.%leg_eta_lt%',
        'end_utc': 'report_crewlists.%leg_end_utc%',
        'actype': 'report_crewlists.%leg_ac_type%',
        'acmaintype': 'report_crewlists.%leg_ac_family%',
        'acreg': 'report_crewlists.%leg_ac_reg%',
        'is_deadhead': 'report_crewlists.%leg_is_deadhead%',
        'taskcode': 'report_crewlists.%leg_code%',
        'oaa_id': 'report_crewlists.%oaa_id%',
        'is_flight': 'report_crewlists.%leg_is_flight%',
        'dutycode': 'report_crewlists.%duty_code%',
        'type_of_flight': 'report_crewlists.%type_of_flight%',
        'orig_date_local': 'report_crewlists.%leg_ldor%',
        'pic_logname': 'report_crewlists.%rc_pic_logname%',
        'is_not_operating': 'report_crewlists.%leg_is_not_operating%',
        'checkin_time': 'report_crewlists.%checkin_time%',
        'checkout_time': 'report_crewlists.%checkout_time%',
        'stop_duration': 'report_crewlists.%stop_duration_scheduled%',
        'is_meal_stop': 'report_crewlists.%leg_is_meal_stop%',
        'is_on_duty': 'report_crewlists.%leg_is_on_duty%',
        'show_times_and_stations': 'report_crewlists.%show_times_and_stations%',
        'meal_code': 'report_crewlists.%rm_meal_code_excl_meal_break%',
        'meal_break': 'report_crewlists.%rm_meal_break_code%',
        'std_date_lt': 'report_crewlists.%std_date_lt%',
        'crewlist_allowed': 'report_crewlists.%crewlist_allowed%',
        'cio_mandatory_ci': 'report_crewlists.%cio_mandatory_ci%',
        'cio_mandatory_co': 'report_crewlists.%cio_mandatory_co%',
    }
    fields.update(SimBriefDebriefExtender.fields)

    # # Non-operating-crew-related fields. This will only work for the first 20 assigned nop crews.
    # # Rave indexes begin from 1, that is why we have xrange(1, 21) here.
    # for i in xrange(1, 21):
    #     fields['nop_crew_id_%02d' % (i)] = 'report_crewlists.%%nop_crew_id%%(%d)' % (i)
    #     fields['nop_crew_position_%02d' % (i)] = 'report_crewlists.%%nop_crew_position%%(%d)' % (i)
    #     fields['nop_crew_gn_%02d' % (i)] = 'report_crewlists.%%nop_crew_gn%%(%d)' % (i)
    #     fields['nop_crew_sn_%02d' % (i)] = 'report_crewlists.%%nop_crew_sn%%(%d)' % (i)
    #     fields['nop_crew_gender_%02d' % (i)] = 'report_crewlists.%%nop_crew_gender%%(%d)' % (i)


# LegInfoLegality --------------------------------------------------------{{{2
class LegInfoLegality:
    fields = {
        'udor': 'report_crewlists.%leg_udor%',
        'ldor': 'report_crewlists.%leg_ldor%',
        'flight_id': 'report_crewlists.%leg_flight_id%',
        'code': 'report_crewlists.%leg_code%',
        'is_flight_duty': 'report_crewlists.%leg_is_flight%',
        'is_ground_duty': 'report_crewlists.%leg_is_ground_duty%',
        'is_off_duty': 'report_crewlists.%leg_is_off_duty%',
        'atd_utc': 'report_crewlists.%leg_atd_utc%',
        'ata_utc': 'report_crewlists.%leg_ata_utc%',
        'atd_lt': 'report_crewlists.%leg_atd_lt%',
        'ata_lt': 'report_crewlists.%leg_ata_lt%',
        'etd_utc': 'report_crewlists.%leg_etd_utc%',
        'eta_utc': 'report_crewlists.%leg_eta_utc%',
        'etd_lt': 'report_crewlists.%leg_etd_lt%',
        'eta_lt': 'report_crewlists.%leg_eta_lt%',
        'adep': 'report_crewlists.%leg_adep%',
        'ades': 'report_crewlists.%leg_ades%',
        'std_utc': 'report_crewlists.%leg_std_utc%',
        'sta_utc': 'report_crewlists.%leg_sta_utc%',
        'std_lt': 'report_crewlists.%leg_std_lt%',
        'sta_lt': 'report_crewlists.%leg_sta_lt%',
        'stop': 'report_crewlists.%stop_duration_scheduled_actual%',
        'is_meal_stop': 'report_crewlists.%leg_is_meal_stop%',
        'meal_code': 'report_crewlists.%rm_meal_code%',
        'dutycode': 'report_crewlists.%duty_code%',
    }
    fields.update(SimBriefDebriefExtender.fields)


# MinMaxDateInfo ---------------------------------------------------------{{{2
class MinMaxDateInfo:
    fields = {
        'min': 'report_crewlists.%prev_max3_start_in_ac_rot%',
        'max': 'report_crewlists.%leg_start_utc%',
    }


# MonthInfo --------------------------------------------------------------{{{2
class MonthInfo:
    fields = {
        'start_date': 'report_crewlists.%ix_months_ago%(fundamental.%now%)',
        'block_hours': 'report_crewlists.%monthly_block_time_ix_months_ago%(fundamental.%now%)',
        'duty_hours': 'report_crewlists.%monthly_duty_time_ix_months_ago%(fundamental.%now%)',
    }


# PointsInfo -------------------------------------------------------------{{{2
class PointsInfo:
    fields = {                                        # OLD COMMENTS:
        'start_lt': 'report_crewlists.%leg_start_lt%',# Check this!
        'end_lt': 'report_crewlists.%leg_end_lt%',    # Check this!
        'per_hour': '0',                              # Check this!
        'points': '0',                                # Check this!
        'type': '"X"',                                # Check this!
        'rest_on_board': '"X"',                       # Check this!
        'rest_on_board_ca': '"X"',                    # Check this!
    }


# TaskInfo ---------------------------------------------------------------{{{2
class TaskInfo:
    """ Collects info for a task.  """
    fields = {
        'taskcode': 'report_crewlists.%leg_code%',
        'std_lt': 'report_crewlists.%leg_std_lt%',
        'sta_lt': 'report_crewlists.%leg_sta_lt%',
        'description': 'report_crewlists.%task_description%',
    }
    fields.update(SimBriefDebriefExtender.fields)


# XML elements / classes ================================================={{{1

# activityInfo -----------------------------------------------------------{{{2
class activityInfo(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        for leg in c.chain('legs'):
            self.append(UCLegalityActivityInfo(leg))


# actMaxDutyInfo ---------------------------------------------------------{{{2
class actMaxDutyInfo(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        for dp in c.chain('dutypasses'):
            self.append(UCLegalityActMaxDutyInfo(dp))


# actMaxPointInfo --------------------------------------------------------{{{2
class actMaxPointInfo(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        for dp in c.chain('dutypasses'):
            self.append(UCLegalityActMaxPointInfo(dp))


# acType -----------------------------------------------------------------{{{2
class acType(XMLElement):
    def __init__(self, a, f):
        XMLElement.__init__(self)
        self.append(xml.string('acTypeCode', f.actype))
        if a.inparams.requestName == 'CrewFlight':
            self.append(xml.string('IATAMainType', f.acmaintype))


# aircraft ---------------------------------------------------------------{{{2
class aircraft(XMLElement):
    def __init__(self, a, f):
        XMLElement.__init__(self)
        self.append(xml.string('acRegShort', f.acreg))
        self.append(acType(a, f))
        if a.inparams.requestName == 'CrewFlight':
            # [acosta:07/257@18:22] This has been discussed so many times, now
            # I will just fill in some empty stuff here.
            self.append(XMLElement('acVersion', XMLElement('acConfigOrVersion', None)))


# CheckInOut -------------------------------------------------------------{{{2
class CheckInOut(XMLElement):
    """ The ACCI XML root element """
    def __init__(self, h, i):
        XMLElement.__init__(self)
        self.append(xml.integer('messageNo', h.mesno))
        self.append(xml.char('cicoIndic', h.cico))
        self.append(xml.string('dutyCd', h.dutycd))
        self.append(xml.string('activityId', h.activityid))
        self.append(xml.date('origDate', h.udor, utc=True))
        self.append(xml.string('stnFr', h.adep))
        self.append(xml.dateTime('std', h.std, utc=True))
        self.append(xml.dateTime('sta', h.sta, utc=True))
        self.append(xml.dateTime('eta', h.eta, utc=True))
        self.append(xml.string('perkey', h.perkey))
        self.append(xml.char('lookForHotel', ('N', 'Y')[h.look_for_ht == True]))
        self.append(xml.char('flightInfoIndic', ('N', 'Y')[h.fli_info == True]))
        self.append(xml.char('crewListIndic', ('N', 'Y')[h.cli_info == True]))
        self.append(xml.char('revisionIndic', ('N', 'Y')[h.rev_info == True]))
        self.append(xml.integer('hotelInfoAfterLine', 0))
        self.append(printLines(i))
        self.append(formatLines(i))


# crew -------------------------------------------------------------------{{{2
class crew(XMLElement):
    def __init__(self, a, c):
        XMLElement.__init__(self)
        self.append(xml.string('crewId', c.id))
        self.append(xml.integer('seniority', c.seniority))
        self.append(xml.string('name', c.logname))
        self.append(xml.string('empno', c.empno))
        self.append(xml.char('gender', ('M', 'F')[c.sex == 'F']))
        self.append(xml.string('mainRank', c.main_rank))
        self.append(xml.string('titleRank', c.title_rank))
        self.append(xml.string('subCategory', c.sub_category))
        if a.inparams.requestName == 'CrewBasic':
            if a.inparams.getCrewBasicInfo:
                self.append(crewBasicInfo(c, True))
            if a.inparams.getCrewContact:
                self.append(crewContact(c))
        elif a.inparams.requestName == 'CrewList':
            self.append(crewBasicInfo(c))
            if a.inparams.getPackedRoster:
                self.append(crewRoster(a, c))
        elif a.inparams.requestName == 'CrewRoster':
            if a.inparams.getCrewBasicInfo:
                self.append(crewBasicInfo(c))
            self.append(crewRoster(a, c))
        elif a.inparams.requestName == 'FutureActivities':
            self.append(crewRoster(a, c))


# crewActivity -----------------------------------------------------------{{{2
class crewActivity(XMLElement):
    def __init__(self, a, f, c, mealActivity=False, mealCode=None):
        XMLElement.__init__(self)
        # WP Int-FAT 35, no CI/CO times on activities not requiring CI/CO.
        if f.cio_mandatory_ci:
            checkin_time = f.checkin_time
        else:
            checkin_time = VoidValue()

        if f.cio_mandatory_co:
            checkout_time = f.checkout_time
        else:
            checkout_time = VoidValue()
        if not mealActivity:
            if f.stop_duration is None:
                f.stop_duration = VoidValue()
            # Note difference to ("B", "F")[f.is_flight] which will not work if 'is_flight' is 'None'
            self.append(xml.string('activityType', ("B", "F")[f.is_flight == True]))
            self.append(xml.string('dutyCode', f.dutycode)) # crew.dutycode,
            self.append(xml.dateTime('checkInTime', checkin_time))
            self.append(xml.dateTime('checkOutTime', checkout_time))
            self.append(xml.duration('stopDuration', f.stop_duration))
            self.append(xml.boolean('crewListAllowed', f.crewlist_allowed))
            self.append(xml.boolean('flyingPassive', f.is_deadhead))
        else:
            self.append(xml.string('activityType', 'B'))
            self.append(xml.string('dutyCode', ''))
            self.append(xml.dateTime('checkInTime', VoidValue()))
            self.append(xml.dateTime('checkOutTime', VoidValue()))
            self.append(xml.duration('stopDuration', VoidValue()))
            self.append(xml.boolean('crewListAllowed', False))
            self.append(xml.boolean('flyingPassive', False))

        if f.is_flight and not mealActivity:
            self.append(crewFlightActivity(a, f))
        else:
            self.append(crewBaseActivity(a, f, mealActivity, mealCode))


# crewAircraftPrevActivityList -------------------------------------------{{{2
class crewAircraftPrevActivityList(XMLElement):
    def __init__(self, a, f):
        # Only the first leg in the 'leg_set' (marked "crew") is necessary,
        # we are iterating over 'leg_set' since transform cannot
        # be applied to 'unique_leg_set'.
        XMLElement.__init__(self)
        for leg in f.chain('crew'):
            for acTrans in leg.chain('acrot'):
                for acChain in acTrans.chain():
                    for acFlight in acChain.chain():
                        for acLeg in acFlight.chain():
                            self.append(crewFlightActivity(a, acLeg, True))
            break


# crewBaseActivity -------------------------------------------------------{{{2
class crewBaseActivity(XMLElement):
    def __init__(self, a, f, mealActivity=False, mealCode=None):
        XMLElement.__init__(self)
        if mealCode is None:
            mealCode = f.meal_code
        self.append(xml.dateTime('startDateLt', f.std_lt))
        self.append(xml.integer('legSeqNumber', f.legno))
        self.append(xml.integer('legSeqTotal', f.sumlegs))
        if mealActivity:
            self.append(xml.string('taskCode', mealCode))
            # WP FAT Int 49 - Meal codes should have time from 12:00 - 12:01
            (y, mo, d, h, m) = f.std_lt.split()
            self.append(xml.dateTime('std', AbsTime(y,mo,d,12,0)))
            self.append(xml.dateTime('sta', AbsTime(y,mo,d,12,1)))
            self.append(xml.string('depStation', VoidValue()))
            self.append(xml.string('arrStation', VoidValue()))
        else:
            self.append(xml.string('taskCode', f.taskcode))
            if hasattr(a.inparams, 'getAdHoc') and a.inparams.getAdHoc:
                self.append(xml.string('adHoc', f.oaa_id))
            if f.show_times_and_stations:
                if a.inparams.getTimesAsLocal:
                    self.append(xml.dateTime('std', f.std_lt))
                    self.append(xml.dateTime('sta', f.sta_lt, lex24=True))
                else:
                    self.append(xml.dateTime('std', f.std_utc, utc=True))
                    self.append(xml.dateTime('sta', f.sta_utc, utc=True, lex24=True))
                self.append(xml.string('depStation', f.depsta))
                self.append(xml.string('arrStation', f.arrsta))
            else:
                self.append(xml.dateTime('std', f.std_lt))
                self.append(xml.dateTime('sta', VoidValue()))
                self.append(xml.string('depStation', VoidValue()))
                self.append(xml.string('arrStation', VoidValue()))


# crewBasicInfo ----------------------------------------------------------{{{2
class crewBasicInfo(XMLElement):
    def __init__(self, c, station=False):
        XMLElement.__init__(self)
        self.append(xml.string('company', c.company))
        self.append(xml.string('base', c.base))
        self.append(xml.string('civicStation', c.civic_station))
        if station:
            self.append(xml.string('station', c.station))
        self.append(xml.string('acQualGroup', str(c.ac_qlns).replace(' ','')))
        self.append(xml.boolean('lineCheckCrew', c.line_check))
        self.append(xml.string('groupType', c.group_type))
        self.append(xml.boolean('sccQualified', c.scc))


# crewBasicReply ---------------------------------------------------------{{{2
class crewBasicReply(XMLElement):
    def __init__(self, a):
        XMLElement.__init__(self)
        try:
            c = a.iterator[0]
        except IndexError:
            traceback.print_exc()
            raise ReplyError(a.inparams.requestName, status.CREW_NOT_FOUND, inparams=a.inparams)
        self.append(crew(a, c))


# crewContact ------------------------------------------------------------{{{2
class crewContact(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        if isinstance(c, VoidIterator):
            return
        # WP FAT-INT 315: Only phone number contacts, max 2 and with max
        # length 20 chars. The specified 'main' and 'second' contact
        # corresponds to phone number of 'main address' and 'second address'
        # records respectively, fed from HR-sync Address Info messages.
        # Therefore we use 'home1' as 'main' and 'home2' as 'second' contact
        # if available. If not, we use contact info originating from
        # migrated data as 'main' contact (contact records having 
        # 'which' = 'home' or 'main' come from migrated data).
        for r in self.search(c.id):
            self.append(XMLElement('crewContactInfo',
                    xml.string('addressType', '1'),
                    xml.string('contactType', r.typ.typ),
                    xml.string('contactNumber', r.val),
                )
            )

    def search(self, crewid):
        from tm import TM
        L = []
        for r in TM.crew_contact.search("(&(crew.id=%s)(which.which=main*)(|(typ.typ=Tel)(typ.typ=Mobile)))" % crewid):
            try:
                w = r.which.which
            except Exception, e:
                continue
            L.append((w, r))
        L.sort()
        return [r for (w, r) in L]


# crewDetailedRoster -----------------------------------------------------{{{2
class crewDetailedRoster(XMLElement):
    def __init__(self, a, c):
        XMLElement.__init__(self)
        for flight in c.chain():
            for leg in flight.chain():
                # Split multi-day activities in CrewRoster reply
                if isinstance(leg, VoidValue):
                    self.append(crewActivity(a, leg, c))
                else:
                    numDays = getNumberOfDays(leg.std_utc, leg.sta_utc)
                    if numDays > 1 and a.inparams.requestName == 'CrewRoster':
                        ap = Airport(default(leg.depsta))
                        legcopy = copy(leg)
                        for dayno in range(numDays):
                            legcopy.sta_lt = legcopy.std_lt + RelTime(1,0,0)
                            # Note that this accounts for passing DST switch
                            legcopy.sta_utc = ap.getUTCTime(legcopy.sta_lt)

                            # Set zero stop duration except for last day
                            if dayno < numDays -1:
                                legcopy.stop_duration = VoidValue()
                            # WP INT 137: Include act. ending within period.
                            if a.inparams.startDate is None or a.inparams.endDate is None or \
                               (legcopy.sta_lt > a.inparams.startDate and \
                               legcopy.sta_lt <= a.inparams.endDate):
                                self.append(crewActivity(a, legcopy, c))
                            legcopy.std_lt = legcopy.sta_lt
                            legcopy.std_utc = legcopy.sta_utc
                    else:
                        # WP INT 137: Include act. ending within period.
                        if a.inparams.endDate is None or leg.sta_lt <= a.inparams.endDate:
                            # Add 'meal activity' to CrewRoster reply if required
                            if leg.is_flight and a.inparams.requestName == 'CrewRoster':
                                if not isEmptyMealCode(leg.meal_code):
                                    self.append(crewActivity(a, leg, c, mealActivity=True))
                            # WP FAT Int 49, 'meal activity' should come before the flight, according to CSC.
                            self.append(crewActivity(a, leg, c))
                            # Add 'meal activity' to CrewRoster reply if required X,V should come after the flight.
                            if leg.is_flight and a.inparams.requestName == 'CrewRoster':
                                if not isEmptyMealCode(leg.meal_break) and ('X' in leg.meal_break or 'V' in leg.meal_break):
                                    self.append(crewActivity(a, leg, c, mealActivity=True, mealCode=leg.meal_break))


# crewDutySummary --------------------------------------------------------{{{2
class crewDutySummary(XMLElement):
    def __init__(self, a, f):
        XMLElement.__init__(self)
        totals = {}
        for crew in f.chain('crew'):
            value = totals.get(crew.dutycode, 0)
            value += 1
            totals[crew.dutycode] = value
        for k in totals.keys():
            self.append(XMLElement('crewDutySummaryInfo')(
                    xml.string('dutyCode', k),
                    xml.integer('numberOfCrew', totals[k]),
                )
            )


# crewFlightActivity -----------------------------------------------------{{{2
class crewFlightActivity(XMLElement):
    def __init__(self, a, f, prev=False):
        XMLElement.__init__(self)
        self.append(flightLeg(a, f, prev))
        if a.inparams.requestName in ('CrewList', 'CrewFlight'):
            self.append(crewFlightExtendedInfo(a, f, prev))


# crewFlightDocument -----------------------------------------------------{{{2
class crewFlightDocument(XMLElement):
    def __init__(self, c, country):
        XMLElement.__init__(self)
        list = []
        passports = []
        visas = []
        for doc in c.chain("doc"):
            try:
                # [acosta:06/348@13:15] Ugly solution to the problem of missing
                # references.  I prefer not to use 'getRefI()' too much...
                if doc.typ.startswith("PASSPORT"):
                    passports.append(doc)
            except:
                pass
            try:
                if doc.typ.startswith("VISA"):
                    if doc.subtype.startswith(country):
                        visas.append(doc)
            except:
                pass
        if passports:
            list.append(xml.string('nationality', "%2.2s" % passports[0].subtype)) # char(2)
            list.append(xml.string('passportNumber', passports[0].docno))
        else:
            # This is really stupid, but otherwise the schema will not validate.
            list.append(xml.string('nationality', "  ")) # char(2)
            list.append(xml.string('passportNumber', None))
        if visas:
            list.append(xml.string('visaNumber', visas[0].docno))
            list.append(xml.date('visaExpireDate', visas[0].validto))
        else:
            # This is also stupid... (see above)
            list.append(xml.string('visaNumber', None))
            list.append(xml.date('visaExpireDate', None))
        self.extend(list)


# crewFlightExtendedInfo -------------------------------------------------{{{2
class crewFlightExtendedInfo(XMLElement):
    def __init__(self, a, f, prev=False):
        XMLElement.__init__(self)
        # prev signals info for previous A/C activity
        if prev:
            self.append(xml.date('stdLocal', f.orig_date_local))
        else:
            self.append(xml.string('typeOfFlight', f.type_of_flight))
            self.append(xml.string('pilotInCommandName', "%s" % (f.pic_logname)))
            self.append(xml.date('stdLocal', f.orig_date_local))


# crewFlightInfo ---------------------------------------------------------{{{2
class crewFlightInfo(XMLElement):
    def __init__(self, a, f):
        XMLElement.__init__(self)
        self.append(crewFlightActivity(a, f))
        self.append(crewDutySummary(a, f))
        self.append(crewAircraftPrevActivityList(a, f))


# crewFlightReply --------------------------------------------------------{{{2
class crewFlightReply(XMLElement):
    def __init__(self, a):
        XMLElement.__init__(self)
        try:
            a.iterator[0]
        except:
            raise ReplyError(a.inparams.requestName, status.FLIGHT_NOT_FOUND, inparams=a.inparams)
        for f in a.iterator:
            self.append(crewFlightInfo(a, f))


# crewLegalityInfo -------------------------------------------------------{{{2
class crewLegalityInfo(XMLElement):
    def __init__(self, a, c):
        XMLElement.__init__(self)
        self.append(UCCrewLegalityInfo(a, c))


# crewList ---------------------------------------------------------------{{{2
class crewList(XMLElement):
    def __init__(self, a, f):
        XMLElement.__init__(self)
        i = 1
        unique_crewids = set()
        for c in f.chain():
            if c.id in unique_crewids:
                continue
            self.append(crewListMember(a, f, c)(sortIndex=i))
            i += 1
            unique_crewids.add(c.id)

        # normal crew data has been added, adding non-operating crew data now
        if not isinstance(f, VoidValue):
            pass
            # for i in xrange(1, 21):
            #     if not getattr(f, 'nop_crew_id_%02d' % (i)):
            #         # no more non-operating crews on this leg
            #         break
            #     nop_crew_dict = {
            #         'crewid':   getattr(f, 'nop_crew_id_%02d' % (i)),
            #         'position': getattr(f, 'nop_crew_position_%02d' % (i)),
            #         'gn':       getattr(f, 'nop_crew_gn_%02d' % (i)),
            #         'sn':       getattr(f, 'nop_crew_sn_%02d' % (i)),
            #         'gender':   getattr(f, 'nop_crew_gender_%02d' % (i)),
            #     }
            #     self.append(crewListMember(a, f, None, non_operating_crew=nop_crew_dict))


# crewListActivity -------------------------------------------------------{{{2
class crewListActivity(XMLElement):
    def __init__(self, a, f):
        XMLElement.__init__(self)
        if f.is_flight:
            self.append(xml.string('activityType', "F"))
            self.append(crewFlightActivity(a, f))
        elif not f.crewlist_allowed:
            # See SASCMS-2121, crew not allowed to get crew list for a PACT.
            raise ReplyError(a.inparams.requestName, status.REQUEST_NOT_SUPPORTED, inparams=a.inparams)
        else:
            self.append(xml.string('activityType', "B"))
            self.append(crewBaseActivity(a, f))
        self.append(crewList(a, f))


# crewListMember ---------------------------------------------------------{{{2
class crewListMember(XMLElement):
    def __init__(self, a, f, c, non_operating_crew=None):
        XMLElement.__init__(self)
        if not non_operating_crew:
            self.append(xml.string('dutyCode', c.dutycode))
            checkedin = c.checkedin
            # WP Int-Fat 363, using EntityConnection to find "real"
            # CI status
            if (f.cio_mandatory_ci
                and not isinstance(a, VoidActivity)):
                for row in a.cioinfo(c.id):
                    if (row['st'] is not None
                            and row['st'] <= int(f.end_utc)
                            and row['et'] is not None
                            and row['et'] >= int(f.end_utc)
                            and row['status'] & 1):
                        # Had status CI and st <= leg.end <= et
                        checkedin = True
                        break
            self.append(xml.boolean('checkedIn', checkedin))
            if a.inparams.getPrevNextDuty:
                self.append(xml.string('prevDuty', c.prev_activity))
                self.append(xml.string('nextDuty', c.next_activity))
            if a.inparams.getPrevNextAct:
                self.append(xml.string('prevActivity', c.prev_activity))
                self.append(xml.string('nextActivity', c.next_activity))
            if a.inparams.getNextFlightDuty:
                # Don't print out if crew has no next duty.
                if c.next_flight_depsta:
                    self.append(nextFlightDuty(a, c))
            if a.inparams.getLastFlownDate:
                self.append(xml.date('lastFlownDate', c.last_flown))
            if a.inparams.getCrewFlightDocuments:
                self.append(crewFlightDocument(c, f.end_country))
            self.append(crew(a, c))
        else:
            # a non-operating crew has been passed as a parameter
            self.append(xml.string('dutyCode', ''))
            self.append(xml.boolean('checkedIn', False))
            nop_xml_element = XMLElement(tag='crew')
            nop_xml_element.append(xml.string('crewId', ''))
            nop_xml_element.append(xml.string('seniority', ''))
            full_name = non_operating_crew['sn'] + ' ' + non_operating_crew['gn']
            full_name = full_name.strip()
            nop_xml_element.append(xml.string('name', full_name))
            nop_xml_element.append(xml.string('empno', non_operating_crew['crewid']))
            nop_xml_element.append(xml.string('gender', non_operating_crew['gender']))
            nop_xml_element.append(xml.string('mainRank', ''))
            nop_xml_element.append(xml.string('titleRank', non_operating_crew['position']))
            nop_xml_element.append(xml.string('subCategory', ''))
            self.append(nop_xml_element)


# crewListReply ----------------------------------------------------------{{{2
class crewListReply(XMLElement):
    def __init__(self, a):
        XMLElement.__init__(self)
        try:
            a.iterator[0]
        except Exception, e:
            raise ReplyError(a.inparams.requestName, status.FLIGHT_NOT_FOUND, inparams=a.inparams)
        for f in a.iterator:
            self.append(crewListActivity(a, f))


# crewPreActivity --------------------------------------------------------{{{2
class crewPreActivity(XMLElement):
    def __init__(self, p):
        XMLElement.__init__(self)
        self.append(xml.string('taskCode', p.taskcode))
        self.append(xml.dateTime('std', p.std_lt))
        self.append(xml.dateTime('sta', p.sta_lt, lex24=True))
        self.append(xml.string('actDescription', p.description))


# crewPreActivityReply ---------------------------------------------------{{{2
class crewPreActivityReply(XMLElement):
    def __init__(self, a):
        XMLElement.__init__(self)
        try:
            c = a.iterator[0]
        except:
            raise ReplyError(a.inparams.requestName, status.CREW_NOT_FOUND, inparams=a.inparams)
        self.append(crew(a, c))


# crewPreRoster ----------------------------------------------------------{{{2
class crewPreRoster(XMLElement):
    def __init__(self, a, c):
        XMLElement.__init__(self)
        for activity in c.chain():
            self.append(crewPreActivity(activity))


# crewRoster -------------------------------------------------------------{{{2
class crewRoster(XMLElement):
    def __init__(self, a, c):
        XMLElement.__init__(self)
        self.append(xml.date('rosterReleasedUntil', c.released_until))
        if a.inparams.requestName == 'CrewList':
            self.append(xml.string('crewPackedRoster', c.packed_roster))
        elif a.inparams.requestName == 'FutureActivities':
            self.append(crewPreRoster(a, c))
        else:
            self.append(crewDetailedRoster(a, c))


# crewRosterReply --------------------------------------------------------{{{2
class crewRosterReply(XMLElement):
    def __init__(self, a):
        XMLElement.__init__(self)
        try:
            c = a.iterator[0]
        except:
            raise ReplyError(a.inparams.requestName, status.CREW_NOT_FOUND, inparams=a.inparams)
        self.append(crew(a, c))


# delayedDeparture -------------------------------------------------------{{{2
class delayedDeparture(XMLElement):
    def __init__(self, d):
        XMLElement.__init__(self)
        self.append(xml.string('reasonCode', d.code))
        # Bugzilla #20531 NOTE: the duration is stored in database as a coded
        # string, not as a RelTime.
        if d.duration is None or str(d.duration) == '': # Null, empty, no content.
            self.append(xml.duration('duration', d.duration))
        else:
            self.append(xml.string('duration', d.duration))
        self.append(xml.string('subReasonCode', d.subcode))


# delays -----------------------------------------------------------------{{{2
class delays(XMLElement):
    def __init__(self, a, f):
        XMLElement.__init__(self)
        for delay in a.delayinfo(f.udor, f.id, f.depsta):
            self.append(delayedDeparture(delay))


# dutyCalculationReply ---------------------------------------------------{{{2
class dutyCalculationReply(XMLElement):
    def __init__(self, a):
        XMLElement.__init__(self)
        self['version'] = schema_version
        try:
            c = a.iterator[0]
        except:
            raise ReplyError(a.inparams.requestName, status.CREW_NOT_FOUND, inparams=a.inparams)
        self.append(crewLegalityInfo(a, c))


# dutyInfo ---------------------------------------------------------------{{{2
class dutyInfo(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        for dp in c.chain('dutypasses'):
            self.append(UCLegalityDutyInfo(dp))


# flightLeg --------------------------------------------------------------{{{2
class flightLeg(XMLElement):
    def __init__(self, a, f, prevlegs=False):
        XMLElement.__init__(self)
        self.append(xml.string('flightId', f.id))
        self.append(xml.date('originDate', f.udor, utc=True))
        self.append(xml.integer('legSeqNumber', f.legno))
        self.append(xml.integer('legSeqTotal', f.sumlegs))
        self.append(xml.string('depStation', f.depsta))
        self.append(xml.string('arrStation', f.arrsta))
        if a.inparams.getTimesAsLocal:
            self.append(xml.dateTime('std', f.std_lt))
            self.append(xml.dateTime('sta', f.sta_lt))
        else:
            self.append(xml.dateTime('std', f.std_utc, utc=True))
            self.append(xml.dateTime('sta', f.sta_utc, utc=True))

        if not prevlegs:
            self.append(aircraft(a, f))
            if a.inparams.requestName == 'CrewFlight':
                self.append(delays(a, f))
                #XXX flightLeg - what happened to diversions (especially in CrewFlight) ???
                self.append(paxFigures(a, f))
            else:
                #XXX flightLeg - why not flightLegStatus for CrewFlight???
                self.append(flightLegStatus(a, f))
                if hasattr(a.inparams, 'getFlightLegSVC') and a.inparams.getFlightLegSVC:
                    self.append(paxFigures(a, f))


# flightLegStatus --------------------------------------------------------{{{2
class flightLegStatus(XMLElement):
    def __init__(self, a, f):
        XMLElement.__init__(self)
        if a.inparams.getTimesAsLocal:
            if self.__exists(f.etd_lt):
                self.append(xml.dateTime('etd', f.etd_lt))
            else:
                self.append(xml.dateTime('etd', f.std_lt))
            if self.__exists(f.eta_lt):
                self.append(xml.dateTime('eta', f.eta_lt))
            else:
                self.append(xml.dateTime('eta', f.sta_lt))
            if self.__exists(f.atd_lt):
                self.append(xml.dateTime('atd', f.atd_lt))
            else:
                self.append(xml.dateTime('atd', f.std_lt))
            if self.__exists(f.ata_lt):
                self.append(xml.dateTime('ata', f.ata_lt))
            else:
                self.append(xml.dateTime('ata', f.sta_lt))
        else:
            if self.__exists(f.etd_utc):
                self.append(xml.dateTime('etd', f.etd_utc, utc=True))
            else:
                self.append(xml.dateTime('etd', f.std_utc, utc=True))
            if self.__exists(f.eta_utc):
                self.append(xml.dateTime('eta', f.eta_utc, utc=True))
            else:
                self.append(xml.dateTime('eta', f.sta_utc, utc=True))
            if self.__exists(f.atd_utc):
                self.append(xml.dateTime('atd', f.atd_utc, utc=True))
            else:
                self.append(xml.dateTime('atd', f.std_utc, utc=True))
            if self.__exists(f.ata_utc):
                self.append(xml.dateTime('ata', f.ata_utc, utc=True))
            else:
                self.append(xml.dateTime('ata', f.sta_utc, utc=True))

    def __exists(self, value):
        return not (value is None or int(value) == 0)


# formatLines ------------------------------------------------------------{{{2
class formatLines(XMLElement):
    """ A complex element consisting of the ACCI format lines. """
    def __init__(self, acci):
        XMLElement.__init__(self)
        i = 1
        for line in acci:
            if hasattr(line, 'formats') and not isinstance(line, VoidValue):
                # This is only needed for schema validation... (ugly? - yes!)
                if not line.formats:
                    class EmptyFormat:
                        code = ""
                        start = 0
                        end = 0
                    self.append(lineFormat(0, EmptyFormat()))
                for format in line.formats:
                    self.append(lineFormat(i, format))
            elif isinstance(line, VoidValue):
                self.append(lineFormat(1, line))
            i += 1


# lineFormat -------------------------------------------------------------{{{2
class lineFormat(XMLElement):
    def __init__(self, lineno, format):
        XMLElement.__init__(self)
        self.append(xml.integer('lineNo', lineno))
        self.append(xml.string('formatDefinition', format.code))
        self.append(xml.integer('startPos', format.start))
        self.append(xml.integer('endPos', format.end))


# nextFlightDuty ---------------------------------------------------------{{{2
class nextFlightDuty(XMLElement):
    def __init__(self, a, c):
        XMLElement.__init__(self)
        self.append(xml.string('flightId', c.next_flight_id))
        self.append(xml.date('originDate', c.next_flight_udor, utc=True))
        self.append(xml.string('depStation', c.next_flight_depsta))
        self.append(xml.string('arrStation', c.next_flight_arrsta))
        if a.inparams.getTimesAsLocal:
            self.append(xml.dateTime('std', c.next_flight_std_lt))
            self.append(xml.dateTime('sta', c.next_flight_sta_lt))
        else:
            self.append(xml.dateTime('std', c.next_flight_std_utc, utc=True))
            self.append(xml.dateTime('sta', c.next_flight_sta_utc, utc=True))


# paxFigures -------------------------------------------------------------{{{2
class paxFigures(XMLElement):
    def __init__(self, a, f):
        XMLElement.__init__(self)
        totApax = totBpax = totPpax = 0
        ppax = {}
        bpax = {}
        apax = {}
        for pax in a.paxinfo(f.udor, f.id, f.depsta):
            svc = pax.svc
            if pax.svc == 'Y':
                svc = 'M'
            
            ppax[svc] = ppax.get(svc, 0)
            bpax[svc] = bpax.get(svc, 0)
            apax[svc] = apax.get(svc, 0)
            if pax.apax is not None:
                totApax += int(pax.apax)
                apax[svc] += int(pax.apax)
            if pax.bpax is not None:
                totBpax += int(pax.bpax)
                bpax[svc] += int(pax.bpax)
            if pax.ppax is not None:
                totPpax += int(pax.ppax)
                ppax[svc] += int(pax.ppax)

        for svc in ('C', 'M'):
            paxfigure = 0
            if totApax > 0:
                paxfigure = apax.get(svc, 0)
            elif totBpax > 0:
                paxfigure = bpax.get(svc, 0)
            elif totPpax > 0:
                paxfigure = ppax.get(svc, 0)
            self.append(paxFigureServiceClass(svc, paxfigure))


# paxFigureServiceClass --------------------------------------------------{{{2
class paxFigureServiceClass(XMLElement):
    def __init__(self, svc, paxfigure):
        XMLElement.__init__(self)

        self.append(xml.string('serviceClass', svc))
        self.append(xml.integer('paxFigure', paxfigure))
        self.append(xml.string('mealCode', 'Z')) #XXX p.meal_code))


# pointsInfo -------------------------------------------------------------{{{2
class pointsInfo(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        for dp in c.chain('dutypasses'):
            self.append(UCLegalityPointsInfo(dp))


# printLine --------------------------------------------------------------{{{2
class printLine(XMLElement):
    """ A 'quasi-formatted' printout line. """
    def __init__(self, line):
        XMLElement.__init__(self)
        self.append(xml.string('line', line))


# printLines -------------------------------------------------------------{{{2
class printLines(XMLElement):
    """ A complex element consisting of the ACCI print lines. """
    def __init__(self, acci):
        XMLElement.__init__(self)
        for line in acci:
            self.append(printLine(line))


# statInfo ---------------------------------------------------------------{{{2
class statInfo(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        for m in c.chain('months'):
            self.append(UCLegalityStat(m))


# UCCrewLegalityInfo -----------------------------------------------------{{{2
class UCCrewLegalityInfo(XMLElement):
    def __init__(self, a, c):
        XMLElement.__init__(self)
        self.append(xml.string('empno', a.inparams.perKey))
        # NOTE: 'errors' element omitted completely
        # self.append(errors(c))
        self.append(xml.string('agreementName', c.agreement_name))
        self.append(warningList(c))
        self.append(XMLElement('packedSchedules', UCLegalityPackedSchedule(c)))
        self.append(XMLElement('legalityInfo', UCLegalityInfo(c)))
        self.append(statInfo(c))


# UCLegalityActivityInfo -------------------------------------------------{{{2
class UCLegalityActivityInfo(XMLElement):
    def __init__(self, e):
        XMLElement.__init__(self)
        if self.__exists(e.atd_utc) and self.__exists(e.ata_utc):
            depTime = e.atd_utc
            arrTime = e.ata_utc
            taIndicator = 'A'
        elif self.__exists(e.etd_utc) and self.__exists(e.eta_utc):
            depTime = e.etd_utc
            arrTime = e.eta_utc
            taIndicator = 'E'
        else:
            depTime = e.std_utc
            arrTime = e.sta_utc
            taIndicator = ' '
        self.append(xml.date('activityDate', e.ldor))
        self.append(xml.date('activityDateUTC', e.udor, utc=True))
        if e.is_flight_duty:
            self.append(xml.string('activityName', e.flight_id))
        else:
            self.append(xml.string('activityName', e.code))
        self.append(xml.char('isFlight', ('N', 'Y')[e.is_flight_duty == True]))
        self.append(xml.char('isGround', ('N', 'Y')[e.is_ground_duty == True]))
        self.append(XMLElement('isInfo', 'N'))
        self.append(xml.char('isOffDuty', ('N', 'Y')[e.is_off_duty == True]))
        self.append(xml.time('depTime', depTime))
        self.append(xml.time('arrTime', arrTime))
        self.append(xml.string('depStation', e.adep))
        self.append(xml.string('arrStation', e.ades))
        self.append(xml.time('stdTime', e.std_utc))
        self.append(xml.time('staTime', e.sta_utc))
        self.append(xml.string('stop', e.stop))
        self.append(xml.char('mealStopIndicator', ("_", "%1.1s" % e.meal_code)[e.is_meal_stop == True]))
        self.append(xml.char('taIndicator', taIndicator))
        self.append(xml.string('dutyCode', e.dutycode))

    def __exists(self, value):
        return not (value is None or int(value) <= 24*60)


# UCLegalityActMaxDutyInfo -----------------------------------------------{{{2
class UCLegalityActMaxDutyInfo(XMLElement):
    def __init__(self, dp):
        XMLElement.__init__(self)
        self.append(xml.date('dpDate', dp.start_lt))
        self.append(xml.duration('maxDutP', dp.max_dutP))
        self.append(xml.duration('actDutP', dp.dutP))
        self.append(xml.duration('maxDut1', dp.max_dut1))
        self.append(xml.duration('actDut1', dp.dut1))
        self.append(xml.duration('dut1F', dp.dut1F))
        self.append(xml.duration('dut1B', dp.dut1B))
        # Not using 3x24 anymore, these values are "dummies".
        self.append(xml.duration('maxDut3', None))
        self.append(xml.duration('actDut3', None))
        self.append(xml.duration('dut3F', None))
        self.append(xml.duration('dut3B', None))
        self.append(xml.duration('maxDut7', dp.max_dut7))
        self.append(xml.duration('actDut7', dp.dut7))
        self.append(xml.duration('dut7F', dp.dut7F))
        self.append(xml.duration('dut7B', dp.dut7B))
        self.append(xml.duration('accumulatedDuty7F', dp.dut7Facc))


# UCLegalityActMaxPointInfo ----------------------------------------------{{{2
class UCLegalityActMaxPointInfo(XMLElement):
    def __init__(self, dp):
        XMLElement.__init__(self)
        self.append(xml.date('dpDate', dp.start_lt))
        #XX max_points not used or defined any longer
	self.append(xml.integer('maxPointsDutyPass', 0))
        self.append(xml.decimal('fatigue1Decimal', "%0.2f" % (dp.acc_fatigue1 / 100.0)))
        self.append(xml.decimal('lofDecimal', "%0.2f" % (dp.acc_level_of_fatigue / 100.0)))
        self.append(xml.decimal('fatigueDecimal', "%0.2f" % (dp.acc_fatigue / 100.0)))
        self.append(xml.integer('passive', dp.points_passive))
        # self.append(xml.decimal('maxPoints7', "%0.2f" % (dp.points_max7 / 100.0)))
        self.append(xml.decimal('points7Pass', "%0.2f" % (dp.points7P / 100.0)))
        self.append(xml.decimal('actPoints7', "%0.2f" % (dp.points7 / 100.0)))
        self.append(xml.integer('points7F', dp.points7F))
        self.append(xml.integer('points7B', dp.points7B))


# UCLegalityDutyInfo -----------------------------------------------------{{{2
class UCLegalityDutyInfo(XMLElement):
    def __init__(self, dp):
        XMLElement.__init__(self)
        self.append(xml.date('dpDate', dp.start_lt))
        self.append(xml.string('dutyPassIndicator', dp.seq_no))
        self.append(xml.date('ciDate', dp.ci_time))
        self.append(xml.time('ciTime', dp.ci_time))
        self.append(xml.date('coDate', dp.co_time))
        self.append(xml.time('coTime', dp.co_time))
        self.append(xml.integer('activeLandings', dp.active_landings))
        self.append(xml.duration('dutP', dp.dutP))
        self.append(xml.duration('dutNight', dp.dut_night))
        self.append(xml.duration('dut1', dp.dut1))
        #XXX 3x24 removed, not used by any rule anylonger.
        self.append(xml.duration('dut3', None))
        self.append(xml.duration('dut7', dp.dut7))
        self.append(xml.string('offDutyStation', dp.off_duty_station))
        self.append(xml.duration('timeOffToNextDuty', dp.time_off))
        self.append(xml.duration('slip', dp.slip))
        self.append(xml.duration('timeOffMinRequired', dp.time_off_min))
        self.append(xml.duration('timeOffLast24Hrs', dp.time_off_last_24))
        self.append(xml.integer('fatigue', dp.fatigue))
        #XXX pointsRest not used or defined 20140930
        self.append(xml.integer('pointsRest', 0))
        self.append(xml.char('longTermRest', ('N', 'Y')[dp.is_long_term_rest == True]))
        self.append(xml.integer('lof', dp.level_of_fatigue))


# UCLegalityInfo ---------------------------------------------------------{{{2
class UCLegalityInfo(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        self.append(dutyInfo(c))
        self.append(pointsInfo(VoidIterator()))
        self.append(activityInfo(c))
        self.append(actMaxDutyInfo(c))
        self.append(actMaxPointInfo(c))


# UCLegalityPackedSchedule -----------------------------------------------{{{2
class UCLegalityPackedSchedule(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        for p in c.packed_roster.split('/'):
            self.append(xml.string('packedRoster', p.strip() + "/"))


# UCLegalityPointsInfo ---------------------------------------------------{{{2
class UCLegalityPointsInfo(XMLElement):
    def __init__(self, dp):
        XMLElement.__init__(self)
        sortOrder = 1
        for p in dp.chain('points'):
            self.append(UCLegalityPoint(p, sortOrder))
            sortOrder += 1


# UCLegalityPoint --------------------------------------------------------{{{2
class UCLegalityPoint(XMLElement):
    def __init__(self, p, s):
        XMLElement.__init__(self)
        self.append(xml.integer('sortOrder', s))
        self.append(xml.char('periodApplies', 'Y'))
        self.append(xml.dateTime('pointsStartTime', p.start_lt))
        self.append(xml.dateTime('pointsEndTime', p.end_lt))
        self.append(xml.integer('pointsPerHour', p.per_hour))
        self.append(xml.integer('points', p.points))
        self.append(xml.char('pointsPeriodType', p.type))
        self.append(xml.char('pointsRestOnBoard', p.rest_on_board))
        self.append(xml.char('pointsRestCaRest', p.rest_on_board_ca))


# UCLegalityStat ---------------------------------------------------------{{{2
class UCLegalityStat(XMLElement):
    def __init__(self, m):
        XMLElement.__init__(self)
        self.append(xml.date('month', m.start_date))
        self.append(xml.duration('blockHours', m.block_hours))
        self.append(xml.duration('dutyHours', m.duty_hours))


# UCWarning --------------------------------------------------------------{{{2
class UCWarning(XMLElement):
    def __init__(self, w):
        XMLElement.__init__(self)
        self.append(xml.date('warningDate', w.startdate))
        self.append(xml.string('warningId', w.rule))
        self.append(xml.string('warningMask', ""))
        self.append(xml.string('warningLimit', w.limitvalue))
        self.append(xml.string('warningActual', w.actualvalue))
        self.append(xml.string('warningOverShoot', w.overshoot))
        self.append(xml.string('warningLimitExec', "")) # XXX Not in Rave
        self.append(xml.string('warningText', w.failtext))
        self.append(XMLElement('forcedFlag', 'N')) # XXX forcedFlag


# warningList ------------------------------------------------------------{{{2
class warningList(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        for w in c.chain('warnings'):
            self.append(UCWarning(w))


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
