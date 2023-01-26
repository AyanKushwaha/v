
# [acosta:08/039@15:10] Created.

"""
More readable version of the check-in report.
"""

import carmensystems.rave.api as rave
import Cui
import Crs
import cio.rv as rv
import cio.db as db

from AbsTime import AbsTime
from RelTime import RelTime

from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from carmensystems.basics.CancelException import CancelException

# PRT formatting functions ==============================================={{{1

# AText ------------------------------------------------------------------{{{2
def AText(*a, **k):
    """Standard text."""
    #k['valign'] = TOP
    return Text(*a, **k)


# B ----------------------------------------------------------------------{{{2
def B(*a, **k):
    """Bold text."""
    k['font'] = Font(weight=BOLD)
    return AText(*a, **k)


# ChangedRow -------------------------------------------------------------{{{2
def ChangedRow(*a, **k):
    """Mark changed assignment by setting darker background."""
    k['background'] = '#f0f0f0'
    return Row(*a, **k)


# H1 ---------------------------------------------------------------------{{{2
def H1(*a, **k):
    """Header text level 1: size 12, bold, space above."""
    k['font'] = Font(size=10, weight=BOLD)
    # Add some space on top of the header.
    k['padding'] = padding(2, 12, 2, 2)
    return AText(*a, **k)


# H2 ---------------------------------------------------------------------{{{2
def H2(*a, **k):
    """Header text level 2: size 9 bold."""
    k['font'] = Font(size=8, weight=BOLD)
    return AText(*a, **k)


# HeaderRow --------------------------------------------------------------{{{2
def HeaderRow(*a, **k):
    """The header row will have a slightly darker background."""
    k['background'] = '#cdcdcd'
    return Row(*a, **k)


# I ----------------------------------------------------------------------{{{2
def I(*a, **k):
    """Italics."""
    k['font'] = Font(size=8, style=ITALIC)
    return AText(*a, **k)


# IndentedRow ------------------------------------------------------------{{{2
def IndentedRow(*a, **k):
    """Simulate indention by adding empty column first on row."""
    return Isolate(Row(Column(width=12), Column(Row(*a, **k))))


# RowSpacer --------------------------------------------------------------{{{2
def RowSpacer(*a, **k):
    """Empty row of height 16."""
    k['height'] = 16
    return Row(*a, **k)


# RText ------------------------------------------------------------------{{{2
def RText(*a, **k):
    """Text aligned to right (for numbers) added extra padding to the right to
    create a nicer looking report."""
    k['align'] = RIGHT
    k['padding'] = padding(2, 2, 12, 2)
    return AText(*a, **k)


# CIOReport =============================================================={{{1
class CIOReport(SASReport):
    use_utc = False

    def create(self):
        self.crewid = self.arg('CREWID')
        self.r = rv.EvalRoster(self.crewid)

        if self.status == 'ci':
            SASReport.create(self, 'Check-in Report', showPlanData=False)
            self.add(self.report_header("Check-in Verification"))
            self.add(RowSpacer())
            self.add(Isolate(Column(
                Row(
                    Column(H2(self.r.extperkey)),
                    Column(H2(self.r.logname)),
                    Column(H2(self._flight_id(self.r.ci_flight_name, self.r.ci_udor))),
                    Column(H2("STD %02d:%02d" % self.r.ci_std.split()[3:5]))),
                width=int(0.8 * self.pageWidth))))
            if self.r.next_is_passive:
                self.pic_ca1()
            self.crew_info()
            self.expiry_info()
            self.passive_duty()
            self.preliminary_ca1()
            self.special_info()
            self.crew_list()
            self.revised_schedule()

        elif self.status == 'co':
            SASReport.create(self, 'Check-out Report', showPlanData=False)
            self.add(self.report_header("Check-out Verification"))
            self.add(RowSpacer())
            self.add(Isolate(Column(
                Row(
                    Column(H2(self.r.extperkey)),
                    Column(H2(self.r.logname)),
                    Column(H2(self._flight_id(self.r.co_flight_name, self.r.co_udor))),
                    Column(H2("STD %02d:%02d" % self.r.co_std.split()[3:5]))),
                width=int(0.8 * self.pageWidth))))
            self.next_duty()
            self.crew_info()
            self.revised_schedule()

        elif self.status == 'coi':
            SASReport.create(self, 'Check-in/Check-out Report', showPlanData=False)
            self.add(self.report_header("Check-out Verification"))
            self.add(RowSpacer())
            self.add(Isolate(Column(
                Row(
                    Column(H2(self.r.extperkey)),
                    Column(H2(self.r.logname)),
                    Column(H2(self._flight_id(self.r.co_flight_name, self.r.co_udor))),
                    Column(H2("STD %02d:%02d" % self.r.co_std.split()[3:5]))),
                width=int(0.8 * self.pageWidth))))
            self.add(RowSpacer())
            self.add(self.report_header("Check-in Verification"))
            self.add(RowSpacer())
            self.add(Isolate(Column(
                Row(
                    Column(H2(self.r.extperkey)),
                    Column(H2(self.r.logname)),
                    Column(H2(self._flight_id(self.r.ci_flight_name, self.r.ci_udor))),
                    Column(H2("STD %02d:%02d" % self.r.ci_std.split()[3:5]))),
                width=int(0.8 * self.pageWidth))))
            if self.r.next_is_passive:
                self.pic_ca1()
            self.crew_info()
            self.passive_duty()
            self.special_info()
            self.crew_list()
            self.revised_schedule()

        elif self.status in ('early4ci', 'alreadyci', 'alreadyco', 'late4co'):
            SASReport.create(self, 'Check-in/Check-out Report', showPlanData=False)
            self.add(self.report_header("Check-in/Check-out Message"))
            if self.status == 'alreadyci':
                self.add(Isolate(
                    Row("Already checked in.")))
            elif self.status == 'alreadyco':
                self.add(Isolate(
                    Row("Already checked out.")))
            elif self.status == 'early4ci':
                self.add(Isolate(
                    Row("Too early for check-in.")))
            else:
                self.add(Isolate(
                    Row("Too late for check-out.")))
            self.crew_info()
            self.revised_schedule()

        else:
            SASReport.create(self, 'Report creation failure.', showPlanData=False)
            self.add(self.report_header("Failed to create report."))
        self.add(RowSpacer())

    @property
    def status(self):
        return str(self.r.cio_status).split('.')[1]

    def crew_info(self):
        """ Get Office info and Private info for a crew member. """
        ci = db.CrewInfo(self.crewid, self.r.now)
        if ci:
            col = Column()
            col.add(H1("Notification"))
            for msg in ci:
                col.add(I(msg.header))
                for row in msg.fmtList(90):
                    col.add(IndentedRow(AText(row)))
            #if self.update_delivered:
            #    ci.setDelivered()
            self.add(RowSpacer())
            self.add(Isolate(col))

    def crew_list(self):
        """ Get the crew list for next leg. """
        # [acosta:08/290@16:14] WP FAT-Int 17
        if self.r.next_is_active_another_day:
            return
        # [acosta:08/168@16:24] WP Int 198
        cl = rv.CrewList(self.crewid)
        if cl:
            col = Column()
            for c in cl:
                col.add(Isolate(
                    Column(
                        Row(
                            Column(B(c.flight.flight_name)),
                            Column(B(str(c.flight.udor).split()[0])),
                            Column(B("%s - %s" % (c.flight.adep, c.flight.ades))),
                            Column(B("STD %02d:%02d" % (c.flight.std_lt.split()[3:5]))),
                            Column(B("STA %02d:%02d" % (c.flight.sta_lt.split()[3:5]))),
                            Column(B(c.flight.actype))), width=(0.7 * self.pageWidth))))
                table = Column(width=(0.7 * self.pageWidth))
                col.add(table)
                header_row = HeaderRow()
                for cc in c.columns[:-1]:
                    header_row.add(Column(H2(cc)))
                header_row.add(Column(H2(c.columns[-1]), colspan=3))
                table.add(header_row)
                for e in c:
                    table.add(Row(
                        Column(AText(e.rank)),
                        Column(AText(("", "YES")[bool(e.scc)])),
                        Column(AText(e.duty_code)),
                        Column(AText(e.empno)),
                        Column(AText(e.base)), # [acosta:08/168@14:38] WP Cct 937
                        Column(AText(e.logname)),
                        Column(AText(("", "+")[bool(e.checked_in)])), # WP FAT-Int 12
                        Column(AText(e.qual)),
                        Column(RText(e.seniority)),
                        Column(RText(e.prev_activity)),
                        Column(AText("*")),
                        Column(AText(e.next_activity))))
            self.add(RowSpacer())
            self.add(H1(("Crew list", 'Crew list for first active leg')[bool(self.r.next_is_passive)]))
            self.add(Isolate(IndentedRow(col)))

    def expiry_info(self):
        """ Information about documents that are about to expire. """
        ed = db.ExpiryInfo(self.crewid, self.r.now)
        if ed:
            col = Column()
            col.add(H1("Expiry info"))
            for e in ed:
                col.add(IndentedRow(AText(str(e))))
            self.add(RowSpacer())
            self.add(Isolate(col))

    def next_duty(self):
        if self.r.ci_udor is None:
            print "next_duty() - ci_udor was void."
        else:
            self.add(RowSpacer())
            if self.r.next_is_pact:
                datum = self.r.next_std
            else:
                datum = self.r.next_udor
            nd_row = Row()
            nd_row.add(Column(H2("Next duty")))
            nd_row.add(Column(H2(self._flight_id(self.r.next_flight_name, datum))))
            nd_row.add(Column(H2("%02d:%02d" % self.r.next_std.split()[3:5])))
            if self.r.next_req_cio:
                nd_row.add(Column(H2("C/I %02d:%02d" % self.r.next_checkin.split()[3:5])))
            self.add(Isolate(Column(nd_row), width=int(0.8 * self.pageWidth)))

    def passive_duty(self):
        """ Information about coming deadhead legs in the coming duty pass. """
        pl = rv.PassiveLegs(self.crewid)
        if pl:
            col = Column()
            col.add(H1("Passive duty"))
            for leg in pl:
                col.add(IndentedRow(AText("%s" % self._flight_id(leg.flight_name, leg.udor))))
            self.add(RowSpacer())
            self.add(Isolate(col))

    def pic_ca1(self):
        # [acosta:08/168@16:24] WP Int 198
        L = []
        if not self.r.ci_pic_logname is None:
            L.append(Row(Column(H2("PIC")),
                Column(AText(self.r.ci_pic_logname))))
        if not self.r.ci_ca1_logname is None:
            L.append(Row(Column(H2("C/A 1")),
                Column(AText(self.r.ci_ca1_logname))))
        if L:
            self.add(Isolate(
                IndentedRow(
                    Column(*L))))

    def preliminary_ca1(self):
        """ You are preliminary C/A 1 on the following flights. """
        lpc = rv.PrelCA1(self.crewid)
        if lpc:
            col = Column()
            col.add(H1("You are preliminary C/A 1 on the following flight(s)"))
            table = Column()
            col.add(Isolate(table))
            for leg in lpc:
                table.add(IndentedRow(
                    Column(AText(self._flight_id(leg.flight_name, leg.udor))),
                    Column(AText(leg.adep)),
                    Column(AText("-")),
                    Column(AText(leg.ades))))
            self.add(RowSpacer())
            self.add(Isolate(col))

    def report_header(self, message):
        return Isolate(Row(
            Column(H1(message)),
            Column(H1(self.r.now_cph))))

    def revised_schedule(self, from_state=rv.TRACKING_DELIVERED_TYPE, to_state=rv.TRACKING_PUBLISHED_TYPE):
        """ Get a revised schedule. """
        rc = rv.RosterChanges(rv.RosterIterator(self.crewid), from_state, to_state)
        if rc:
            self.add(RowSpacer())
            self.add(H1("Revised Roster"))
            self.add(AText("%-8.8s %s" % (self.r.extperkey, self.r.logname)))
            rc_rows, last_created = rv.revision_info(self.crewid, self.r.now, rc)
            if last_created is not None:
                self.add(IndentedRow(I("Last revision to roster made:  %s" % last_created)))
            for interval, original, revised in rc:
                period_start, period_end = interval
                real_period_end = period_end - RelTime(0, 1)
                self.add(RowSpacer())
                self.add(Row(
                    H2("Period %s - %s" % (str(period_start).split()[0], str(real_period_end).split()[0])),
                    I("Grey background indicates new activity.")))
                self.add(self._rev_roster_table(interval, original, revised, rc.changed_set))
                self.page()

    def special_info(self):
        """ Special messages, targeted for a specific flight. """
        si = db.SpecialInfo(self.crewid, self.r.now)
        if si:
            col = Column()
            col.add(H1("Special Information"))
            ostd = AbsTime(0)
            for s in si:
                if s.leg.std_lt != ostd:
                    # Print flight info for each new leg
                    col.add(RowSpacer())
                    col.add(B(s.legHeader()))
                col.add(B("- %s" % s.messageHeader()))
                ostd = s.leg.std_lt
                for row in s.fmtList(80):
                    col.add(IndentedRow(AText(str(row))))
            self.add(RowSpacer())
            self.add(Isolate(col))

    def _flight_id(self, flight_name, udor):
        return "%s/%s" % (flight_name, str(udor).split()[0])

    def _original_roster(self, dates, d):
        L = []
        o = dates[d].original
        for i in xrange(0, len(o)):
            try:
                if o[i].actcode.endswith('/ -') and o[i].actcode == dates[d - 1].original[-1].actcode:
                    # Don't write "904 / -" both the first and the second day
                    L.append('-')
                else:
                    L.append(o[i].actcode)
            except:
                L.append(o[i].actcode)
        if L and (not o[i].actcode.endswith('/ -') or L[-1] == '-'):
            L.append("/")
        return ' '.join(L)

    def _rev_roster_table(self, interval, original, revised, changed):
        table = Column(width=(0.9 * self.pageWidth))
        date_col = Column(HeaderRow(H2("Day"), rowspan=2), colspan=2)
        rev_col = Column(HeaderRow(H2("Revised Roster")), colspan=9, width=300)
        orig_col = Column(HeaderRow(H2("Original Roster"), rowspan=2), width=150)
        table.add(Row(date_col, rev_col, orig_col))
        dates = {}
        start_date, end_date = interval
        for date in xrange(int(start_date) / 1440, int(end_date) / 1440):
            dates[date] = RevRosterDate(date)
        for x in original:
            start_day, end_day = x.interval()
            for date in xrange(int(start_day) / 1440, int(end_day) / 1440):
                if not date in dates:
                    dates[date] = RevRosterDate(date)
                dates[date].original.append(x)
        for x in revised:
            start_day, end_day = x.interval()
            for date in xrange(int(start_day) / 1440, int(end_day) / 1440):
                if not date in dates:
                    dates[date] = RevRosterDate(date)
                dates[date].revised.append(x)

        rev_col.add(HeaderRow(
            Column(B("C/I")),
            Column(B("Duty")),
            Column(B("Dep")),
            Column(B("STD*")),
            Column(B("STA*")),
            Column(B("Arr")),
            Column(B("A/C")),
            Column(B("Stop")),
            Column(B("MS"))))

        _top = None
        for date in sorted(dates):
            a_date = AbsTime(date * 1440)
            nRevised = 0
            for act in dates[date].revised:
                nRevised += 1
                if self._hasMealActivity(a_date, act):
                    nRevised += 1
            rowspan = max(1, nRevised)
            date_col.add(Row(
                Column(Text(self._weekday(a_date))),
                Column(Text("%02d" % a_date.split()[2], align=RIGHT)),
                rowspan=rowspan,
                border=border(top=_top)))
            orig_col.add(Row(AText(self._original_roster(dates, date), width=150),
                rowspan=rowspan, 
                border=border(top=_top)))
            if not dates[date].revised:
                rev_col.add(ChangedRow(
                    Column(colspan=9), 
                    border=border(top=_top)))
            for e in dates[date].revised:
                actype = stop = meal_stop = ci = ""
                et = "%02d:%02d" % e.sta_lt.split()[3:5]
                et_utc = "%02d:%02d" % e.sta_utc.split()[3:5]
                et_abstime = e.sta_lt
                if e.is_flight:
                    actype = e.actype
                    if e.stop is not None:
                        stop = "%02d:%02d" % e.stop.split()[:2]
                    meal_stop = ('', 'Y')[bool(e.meal_stop)]
                else:
                    # So one day activities won't be seen as two dates
                    if e.sta_lt.split()[3:5] == (0, 0):
                        et = "24:00"
                        et_abstime = e.sta_lt - RelTime(0, 1)
                    
                st = "%02d:%02d" % e.std_lt.split()[3:5]
                st_utc = "%02d:%02d" % e.std_utc.split()[3:5]
                std_date = e.std_lt.split()[:3]
                if e.std_lt.split()[:3] != et_abstime.split()[:3]:
                    if e.has_checkin:
                        ci = "%02d:%02d" % e.ci.split()[3:5]
                    if e.std_lt.split()[:3] == a_date.split()[:3]:
                        rev_col.add((Row, ChangedRow)[e in changed](
                            Column(B(ci)),
                            Column(e.actcode),
                            Column(e.adep),
                            Column((st, st_utc)[bool(self.use_utc)]),
                            Column(colspan=5),
                            border=border(top=_top)))
                    elif et_abstime.split()[:3] == a_date.split()[:3]:
                        rev_col.add((Row, ChangedRow)[e in changed](
                            Column(),
                            Column(e.actcode),
                            Column(colspan=2),
                            Column((et, et_utc)[bool(self.use_utc)]),
                            Column(e.ades),
                            Column(actype),
                            Column(stop),
                            Column(meal_stop),
                            border=border(top=_top)))
                    else:
                        rev_col.add((Row, ChangedRow)[e in changed](
                            Column(),
                            Column(e.actcode),
                            Column('"'),
                            Column('"'),
                            Column('"'),
                            Column('"'),
                            Column(colspan=3),
                            border=border(top=_top)))
                else:
                    if e.has_checkin:
                        ci = "%02d:%02d" % e.ci.split()[3:5]
                    rev_col.add((Row, ChangedRow)[e in changed](
                        Column(B(ci)),
                        Column(e.actcode),
                        Column(e.adep),
                        Column((st, st_utc)[bool(self.use_utc)]),
                        Column((et, et_utc)[bool(self.use_utc)]),
                        Column(e.ades),
                        Column(actype),
                        Column(stop),
                        Column(meal_stop),
                        border=border(top=_top)))

                # Reset border thickness to zero
                _top = None

                # Add 'meal activity' if required
                if self._hasMealActivity(a_date, e):
                    self._addMealActivity(rev_col, _top, changed, e)

                # Reset border thickness to zero
                _top = None
            _top = 0
        if self.use_utc:
            time_text = "* Times are in UTC."
        else:
            time_text = "* Times are in local time."
        table.add(Row(time_text, font=Font(size=6, style=ITALIC)))
        return Isolate(table)

    def _hasMealActivity(self, a_date, leg):
        if (leg.is_flight and leg.meal_code is not None and 
                leg.meal_code.strip(', ') != ''):
            if leg.std_lt.split()[:3] != leg.sta_lt.split()[:3]:
                if leg.sta_lt.split()[:3] == a_date.split()[:3]:
                    return True
            else:
                return True
        return False

    def _addMealActivity(self, col, _top, changed, leg):
        station = leg.adep
        if leg.meal_code in ('X','V'):
            station = leg.ades
        col.add((Row, ChangedRow)[leg in changed](
            Column(),
            Column(leg.meal_code),
            Column(''),
            Column(''),
            Column(''),
            Column(''),
            Column(colspan=3),
            border=border(top=_top)))

    def _weekday(self, atime):
        """Return day of week."""
        how = atime.time_of_week().split()[0]
        return ('MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU')[how // 24]


# RevRosterDate =========================================================={{{1
class RevRosterDate:
    def __init__(self, date):
        self.date = date
        self.original = []
        self.revised = []

    def __str__(self):
        return ("--", str(self.date), 
                '\n', ', '.join([str(x) for x in self.original]), 
                '\n', ', '.join([str(x) for x in self.revised]))


# run_report ============================================================={{{1
def run_report(crewid, force_html=False):
    """Has to run report in HTML format to get the Buttons to work."""
    report = 'CIOReport.py'
    args = 'CREWID=%s' % crewid
    if force_html:
        sf = Crs.CrsGetModuleResource("preferences", Crs.CrsSearchModuleDef,
                "PRTReportFormat")
        Crs.CrsSetModuleResource("preferences", "PRTReportFormat", "HTML", "")
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan',
                report, 0, args)
        Crs.CrsSetModuleResource("preferences", "PRTReportFormat", sf, "")
    else:
        try:
            Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan',
                                           report, 0, args)
        except CancelException:
            Cui.CuiShowPrompt("Cancelled report generation.")


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    import Cui
    crewid, = rave.eval(rave.selected(rave.Level.atom()), 'crew.%id%')
    run_report(crewid)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
