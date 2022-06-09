
# [acosta:06/230@10:12] First version
# [acosta:06/314@17:03] Updated to use Extperkey.
# [acosta:08/115@15:53] Fixed BZ 25341 and BZ 26825.

"""
33.2 List 9 - Who Flew What

This is a list showing performed flights, showed as legs from the month
before. It shows the crew on each leg with the purpose to be able to
determine who was captain, who was purser, and so on.

This list is intended for back office staff and authorities.
"""

# imports ================================================================{{{1
import time
import Cfh
import Cui
import carmensystems.rave.api as R
import utils.DisplayReport as display

from AbsTime import AbsTime
from carmensystems.publisher.api import *

from utils.rave import RaveIterator
from SASReport import SASReport


# constants =============================================================={{{1
TITLE = 'List 9 - Who Flew What'
CREW_COL_WIDTHS = (15, 45, 10, 10, 30, 125)
FLIGHT_COL_WIDTHS = (35, 80, 30, 60, 50, 50, 50, 50, 50, 50, 245)


# classes ================================================================{{{1

# CrewInfo ---------------------------------------------------------------{{{2
class CrewInfo:
    def __init__(self):
        self.fields = {
            'crewStr': 'report_common.%crew_string_at_date%(leg.%start_utc%)',
            'crewNumber': 'report_common.%employee_number_at_date%(leg.%start_utc%)',
            'rank': 'crew.%rank_at_date%(leg.%start_utc%)',
            'dutyCode': 'report_common.%duty_code%',
            'seniority': 'crew.%seniority%',
            'logname': 'crew.%login_name_at_date%(leg.%start_utc%)',
            'firstName': 'report_common.%crew_firstname%',
            'lastName': 'report_common.%crew_surname%',
            'firstName': 'report_common.%crew_firstname%',
            'higherRank': 'crew_pos.%higher_rank%',
            'lowerRank': 'crew_pos.%lower_rank%',
            'is_active': 'leg.%is_active_flight%',
            'is_pilot': 'crew.%is_pilot%',
            'sccStar': 'crew_pos.%chief_of_cabin% and crew_pos.%ac_need_in_pos%(5) > 0',
            'sccPlus': 'crew_pos.%chief_of_cabin% and not crew_pos.%ac_need_in_pos%(5) > 0',
            'restr_medical': 'report_common.%restrs_type_at_date%("MEDICAL", leg.%start_utc%)',
            'restr_training': 'report_common.%restrs_type_at_date%("TRAINING", leg.%start_utc%)',
            'restr_new': 'report_common.%restrs_type_at_date%("NEW", leg.%start_utc%)',
            'qual_lcp': 'report_common.%qlns_type_at_date%("LCP", leg.%start_utc%)',
            'qual_instructor': 'report_common.%instr_qlns_at_date%(leg.%start_utc%)',
            'qual_position': 'report_common.%qlns_type_at_date%("POSITION", leg.%start_utc%)',
        }


# FlightInfo -------------------------------------------------------------{{{2
class FlightInfo:
    fields = {
        'legNo': 'leg.%leg_number%',
        'legsTotal': 'report_crewlists.%num_legs_above%',
        'depStn': 'report_common.%start_stn%',
        'scheduledStart': 'report_common.%leg_scheduled_start%',
        'actualStart': 'report_common.%leg_start%',
        'arrStn': 'report_common.%end_stn%',
        'scheduledEnd': 'report_common.%leg_scheduled_end%',
        'actualEnd': 'report_common.%leg_end%',
        'acType': 'report_common.%ac_type%'
    }


# RowMaker ---------------------------------------------------------------{{{2
class RowMaker:
    """Callable object."""
    def __init__(self, coltype, widths):
        """Create row with columns of type 'coltype', and widths specified in
        seq. 'widths'."""
        self.coltype = coltype
        self.widths = widths

    def __call__(self, *a, **k):
        """Return row with columns with widths specified in self.widths."""
        cols = []
        for i in xrange(len(a)):
            cols.append(self.coltype(a[i], width=self.widths[i]))
        # Add empty column for space.
        cols.append(self.coltype())
        return Row(*cols, **k)

    def __int__(self):
        """Total width of all columns."""
        return sum(self.widths)


# CFH Formatting functions ==============================================={{{1

# AColumn ----------------------------------------------------------------{{{2
def FlightColumn(*a, **k):
    return Column(*a, **k)


# BColumn ----------------------------------------------------------------{{{2
def CrewColumn(*a, **k):
    #k['border'] = border_all()
    return Column(*a, **k)


# crew_row_maker ========================================================={{{1
crew_row_maker = RowMaker(CrewColumn, CREW_COL_WIDTHS)


# flight_row_maker ======================================================={{{1
flight_row_maker = RowMaker(FlightColumn, FLIGHT_COL_WIDTHS)


# List9 =================================================================={{{1
class List9(SASReport):
    """
    Create the report using the Python Publisher API.

    Arguments to report:

    'starttime' - Optional. Real start time of report generation.
    'firstdate' - Optional. First day of period requested.
    'lastdate'  - Optional. Last day of period requested (time point not included in
                  interval).

    If any of the times above are empty, then a Rave evaluation will try
    to get the previous month.

    'CONTEXT'   - Context to use when iterating ('default_context', 'sp_crew').
                  Optional. When not set, 'sp_crew' will be used.
    """

    def create(self):

        starttime = None
        firstdate = None
        lastdate = None
        if self.arg('starttime'):
            starttime = AbsTime(int(self.arg('starttime')))
        if self.arg('firstdate'):
            firstdate = AbsTime(int(self.arg('firstdate')))
        if self.arg('lastdate'):
            lastdate = AbsTime(int(self.arg('lastdate')))
        context = self.arg('CONTEXT')

        if starttime is None or firstdate is None or lastdate is None:
            (n, s, e) = R.eval('fundamental.%now%',
                    'add_months(report_common.%month_start%, -1)',
                    'report_common.%month_start%')
            if starttime is None:
                starttime = n
            if firstdate is None:
                firstdate = s
            if lastdate is None:
                lastdate = e

        if context is None:
            context = 'sp_crew'

        flightItr = RaveIterator(
            RaveIterator.iter('iterators.flight_set',
                    where=(
                        'leg.%is_flight_duty%',
                        'leg.%%end_UTC%% >= %s' % firstdate,
                        'leg.%%end_UTC%% < %s' % lastdate,
                    ),
                    sort_by=('leg.%udor%', 'leg.%flight_id%')),
            {
                'flight': 'leg.%flight_id%', 
                'udor':'leg.%udor%'
            })

        flightLegItr = RaveIterator(
            RaveIterator.iter('iterators.flight_leg_set',
                    sort_by=('leg.%leg_number%', 'leg.%flight_id%')), 
            FlightInfo())

        legItr = RaveIterator(
            RaveIterator.iter('iterators.leg_set',
                    where='fundamental.%is_roster%',
                    sort_by='report_crewlists.%sort_key%'),
            CrewInfo())

        flightLegItr.link(legs=legItr)
        flightItr.link(flightLegs=flightLegItr)
        flights = flightItr.eval(context)

        SASReport.create(self, TITLE, orientation=LANDSCAPE,
                showPlanData=False)

        prev_udor = None
        for flight in flights:
            if prev_udor is None or flight.udor != prev_udor:
                if not prev_udor is None:
                    self.newpage()
                header = self.getDefaultHeader()
                header.add(Row(
                    Text("%s" % str(starttime).split()[0], colspan=2),
                    Text(TITLE, colspan=3), Text("%s (UTC)" %
                        str(flight.udor).split()[0], colspan=2),
                    Text(time.strftime('PER %b %Y', 
                        firstdate.split() + (0, 0, 1, 0)).upper(), colspan=5,
                        align=RIGHT),
                    font=self.HEADERFONT))
                header.add(Column(
                    flight_row_maker(
                        Column('Flight', 'Number'),
                        Column('Flt Origin', 'Start Date'),
                        Column('Leg', 'No'),
                        Column('Total No', 'Legs in Flt'),
                        Column('Dep', 'Airport'),
                        Column('Sched', 'Dep'),
                        Column('Actual', 'Dep'),
                        Column('Arrival', 'Airport'),
                        Column('Sched', 'Arrival'),
                        Column('Actual', 'Arrival'),
                        Column('Aircraft', 'Type Used'),
                        font=self.HEADERFONT,
                        background=self.HEADERBGCOLOUR), 
                        width=self.pageWidth))
                #header.add(flight_row_maker(*[str(x) for x in FLIGHT_COL_WIDTHS]))
                header.add(Row(height=8))
                self.setHeader(header)
            prev_udor = flight.udor

            for flightLeg in flight.chain('flightLegs'):
                self.add(Column(
                    flight_row_maker(
                        Column(flight.flight),
                        Column("%s" % str(flight.udor).split()[0][:-4]),
                        Column('%02d' % flightLeg.legNo),
                        Column('%02d' % flightLeg.legsTotal),
                        Column(flightLeg.depStn),
                        Column(flightLeg.scheduledStart.time_of_day()),
                        Column('(%s)' % flightLeg.actualStart.time_of_day()),
                        Column(flightLeg.arrStn),
                        Column(flightLeg.scheduledEnd.time_of_day()),
                        Column('(%s)' % flightLeg.actualEnd.time_of_day()),
                        Column(flightLeg.acType),
                        font=self.HEADERFONT), 
                        width=self.pageWidth))

                # Divide into three columns
                pilot_col = []
                ap_as_col = []
                other_col = []
                # Separate into two rows, one with passive and another 
                # with active flights (WP 390, Non-core)
                pilot_col_dh = []
                ap_as_col_dh = []
                other_col_dh = []
                for leg in flightLeg.chain('legs'):
                    if leg.is_active:
                        if leg.is_pilot:
                            pilot_col.append(leg)
                        elif leg.rank in ("AP", "AS"):
                            ap_as_col.append(leg)
                        else:
                            other_col.append(leg)
                    else:
                        if leg.is_pilot:
                            pilot_col_dh.append(leg)
                        elif leg.rank in ("AP", "AS"):
                            ap_as_col_dh.append(leg)
                        else:
                            other_col_dh.append(leg)
                    
                has_active_crew = (len(pilot_col) > 0 or len(ap_as_col) > 0 or len(other_col) > 0)
                has_passive_crew = (len(pilot_col_dh) > 0 or len(ap_as_col_dh) > 0 or len(other_col_dh) > 0)
                active_crew_row = Row(
                    self.crew_column(pilot_col),
                    self.crew_column(ap_as_col),
                    self.crew_column(other_col),
                background="#dedede")
                passive_crew_row = Row(
                    self.crew_column(pilot_col_dh),
                    self.crew_column(ap_as_col_dh),
                    self.crew_column(other_col_dh),
                background="#dedede")
                
                if has_active_crew and has_passive_crew:
                    crewRow = Row(
                        Column(active_crew_row, 
                               Row(height=14),
                               passive_crew_row),
                        background="#dedede")
                elif has_active_crew:
                    crewRow = active_crew_row
                elif has_passive_crew:
                    crewRow = passive_crew_row
                else:
                    crewRow = Row(height=1)
                self.add(Isolate(
                    Column(
                        Row(height=6),
                        crewRow,
                        Row(height=16),
                        width=self.pageWidth)))
                self.page0()

    def crew_column(self, crewList):
        col = Column(width=int(crew_row_maker))
        got_passive = False
        for crew in crewList:
            r_and_q = []
            for attr in ('restr_training', 'restr_medical', 'restr_new',
                    'qual_lcp', 'qual_instructor', 'qual_position'):
                x = getattr(crew, attr)
                if x:
                    y = self.getunique(x)
                    r_and_q.append(Row(y))
            if not r_and_q:
                restr_qual = "-"
            else:
                restr_qual = Column(*r_and_q)

            if crew.sccStar:
                textSCC = "*"
            elif crew.sccPlus:
                textSCC = "+"
            else:
                textSCC = ""

            #if crew.is_active or got_passive or not has_active_crew:
            #    _border = None
            #else:
            #    _border = border(top=1)
            #    got_passive = True
            col.add(
                crew_row_maker(
                    crew.rank, 
                    restr_qual, 
                    crew.dutyCode, 
                    textSCC, 
                    crew.crewNumber,
                    crew.logname)) 
                    #border=_border))

        if not crewList:
            #col.add(crew_row_maker(*[str(x) for x in CREW_COL_WIDTHS]))
            col.add(crew_row_maker('', '', '', '', '', ''))
        return col
    
    def getunique(self, list):
        els = list.split()
        result = " "
        for e in els:
            if not e in result:
                result += "%s " % e
        return result[:-1]


# runReport =============================================================={{{1
def runReport(scope='window'):
    """Run PRT Report in scope 'scope'."""
    if scope == 'plan':
        area = Cui.CuiNoArea
        context = 'sp_crew'
    else:
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, scope)
        context = 'default_context'
    rptForm = display.reportFormDate('List9')
    rptForm.show(True)
    if rptForm.loop() == Cfh.CfhOk:
        args = 'startDate=%s endDate=%s CONTEXT=%s scheduled=no' % (
                rptForm.getStartDate(), rptForm.getEndDate(), context)
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope,
            '../lib/python/report_sources/include/List9.py', 0, args)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
