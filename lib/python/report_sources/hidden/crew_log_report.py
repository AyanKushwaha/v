
# [acosta:09/120@10:10] 

"""
Show details from crew log statistics.

This report is primarily for test/verification.
"""

import Cui
import Crs
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import utils.crewlog as crewlog

from AbsTime import AbsTime, PREV_VALID_DAY
from tm import TM
from report_sources.include.SASReport import SASReport
from utils.dave import EC
from utils.time_util import Interval


MAXROWS = 55


class Report(SASReport):
    """Simple report with details from crew_log_acc, crew_log_acc_mod and database plan."""
    def create(self):
        SASReport.create(self, "Pilot's Log - Details", showPlanData=False)
        self.crewid = self.arg('CREWID')
        self.typ = self.arg('TYP')
        self.add(self.report_header())

        self._rowno = 0
        try:
            ec = EC(TM.getConnStr(), TM.getSchemaStr())
            intervals = MonthIntervals()
            this_morning = now().day_floor()
            minus2 = this_morning.month_floor().addmonths(-2, PREV_VALID_DAY)
            minus90d = this_morning.month_floor().adddays(-90)
            
            accu = AccuTable(ec, self.crewid, self.typ, intervals, hi=minus2)
            if accu:
                self._add(self.table_caption(accu.caption()))
                self._add(accu.header_row())
                for row in accu:
                    self._add(row, accu)
                self._newpage()

            plan = PlanTable(ec, self.crewid, self.typ, intervals,
                    hi=this_morning, lo=minus2)
            if plan:
                self._add(self.table_caption(plan.caption()))
                self._add(plan.header_row())
                for row in plan:
                    self._add(row, plan)
                self._newpage()

            manu = ManuTable(ec, self.crewid, self.typ, intervals)
            if manu:
                self._add(self.table_caption(manu.caption()))
                self._add(manu.header_row())
                for row in manu:
                    self._add(row, manu)
                self._newpage()

            totals = TotalsTable(self.typ, intervals, accu, manu, plan)
            if totals:
                self._add(self.table_caption(totals.caption()))
                self._add(totals.header_row())
                for row in totals:
                    self._add(row, totals)
                self._newpage()

            intervals90 = NinetyDaysInterval(hi=this_morning, lo=this_morning.addmonths(-4, PREV_VALID_DAY))
            ninetydays = PlanTable(ec, self.crewid, self.typ, intervals90,
                    hi=this_morning, lo=minus90d)
            if ninetydays:
                self._add(self.table_caption("Ninety days statistics from %s to %s" % (minus90d, this_morning)))
                self._add(ninetydays.header_row())
                for row in ninetydays:
                    self._add(row, ninetydays)

        finally:
            ec.close()

    def _add(self, row, table=None):
        self._rowno += 1
        if self._rowno > MAXROWS:
            self._newpage()
            if table is not None:
                self.add(table.header_row())
                self._rowno += 1
        self.add(row)

    def _newpage(self):
        self.newpage()
        self._rowno = 0

    def table_caption(self, s):
        return prt.Isolate(prt.Row(s, height=24, font=prt.Font(weight=prt.BOLD)))

    def report_header(self):
        return prt.Isolate(prt.Row("Crew %s" % self.crewid, height=24, font=prt.Font(weight=prt.BOLD)))


# Help classes ==========================================================={{{1
class MonthIntervals(list):
    """List of limiting intervals."""
    def __init__(self):
        hi = now().day_floor()
        this_start = hi.month_floor()
        list.__init__(self, [
            (self.int_interval(this_start, hi.month_ceil()), "This Month"),
            (self.int_interval(this_start.addmonths(-1), this_start), "Last Month"),
            (self.int_interval(this_start.addmonths(-6), this_start), "Last 6m"),
            (self.int_interval(this_start.addmonths(-12), this_start), "Last 12m"),
            (self.int_interval(0, hi), "Lifetime"),
        ])

    def int_interval(self, a, b):
        return Interval(int(a), int(b))


class NinetyDaysInterval(list):
    def __init__(self, hi, lo):
        list.__init__(self, [
            (Interval(int(lo), int(hi)), "Last 90 days"),
        ])


class Table(list):
    """Base class for different tables."""
    def __init__(self, ec, crewid, typ, intervals, hi=None, lo=None):
        list.__init__(self)
        self.ec = ec
        self.crewid = crewid
        self.typ = typ
        self.intervals = intervals
        self.hi = hi
        self.lo = lo
        self.sums = [0 for x in intervals]
        self.totals = {}
        self.table()

    def conv(self, value):
        if value == 0:
            return ''
        if self.typ == 'landings':
            return value
        else:
            (hours, minutes) = divmod(value, 60)
            return "%02d:%02d" % (hours, minutes)

    def month(self, t):
        return ("%02d%02d" % AbsTime(t).split()[:2])[2:]

    def interval_values(self, tim, value):
        L = []
        for i, h in self.intervals:
            if i.first <= tim < i.last:
                L.append(value)
            else:
                L.append(0)
        return L

    def totals_row(self, acfamily):
        return [TR(TDI(acfamily), '', '', '', TDI('Total'), *[TDI(self.conv(x)) for x in self.sums], 
                **{'height':24})]

    def table(self):
        pass


class AccuTable(Table):
    """Accumulated values."""

    query = crewlog.AccuQuery

    def header_row(self):
        l = ["A/C Family", "-", "-", "Tim", "Value"]
        l.extend([h for _, h in self.intervals])
        return TR(*[TH(x) for x in l])

    def caption(self):
        return "crew_log_acc until %s" % (self.hi,)

    def table(self):
        aco = None
        for row in sorted(self.query(self.ec, crew=self.crewid, typ=self.typ,
                hi=self.hi, lo=self.lo)):
            l = [row.acfamily, "-", "-", self.month(row.tim), self.conv(row.accvalue)]
            ivalues = self.interval_values(row.tim, row.accvalue)
            svalues = [self.conv(x) for x in ivalues]
            l.extend(svalues)
            if aco is not None and aco != row.acfamily:
                self.extend(self.totals_row(aco))
                self.totals[aco] = list(self.sums)
                self.sums = [ivalues[i] for i in xrange(len(self.intervals))]
            else:
                self.sums = [(self.sums[i] + ivalues[i]) for i in xrange(len(self.intervals))]
            self.append(TR(*[TD(x) for x in l]))
            aco = row.acfamily
        if aco is not None:
            self.extend(self.totals_row(aco))
            self.totals[aco] = list(self.sums)


class ManuTable(AccuTable):
    """Manually entered corrections."""

    query = crewlog.ManuQuery

    def caption(self):
        return "Entries from crew_log_acc_mod."


class PlanTable(Table):
    """Query plan to get latest figures (in details)."""

    def caption(self):
        return "Database queries using interval %s - %s" % (self.lo, self.hi)

    def header_row(self):
        l = ["A/C Family"]
        if self.typ in ('blockhrs', 'logblkhrs'):
            l.extend(["Flight", "ADEP"]) 
        elif self.typ == 'simblkhrs':
            l.extend(["Activity", "Start"])
        elif self.typ == 'landings':
            l.extend(["Landings", "Landed"])
        l.extend(["Tim", "Value"])
        l.extend([h for _, h in self.intervals])
        return TR(*[TH(x) for x in l])

    def table(self):
        aco = None
        for row in sorted(crewlog.SchemaQuery(self.ec, crew=self.crewid, typ=self.typ,
                hi=self.hi, lo=self.lo)):
            l = [row.acfamily]
            try:
                l1 = row.l1rec
                if self.typ in ('blockhrs', 'logblkhrs'):
                    try:
                        y, m, d = AbsTime(l1.udor).split()[:3]
                    except:
                        y, m, d = 0, 0, 0
                    flight = "%s/%02d%02d%02d" % (l1.fd, y, m, d)
                    l.extend([flight, l1.adep])
                elif self.typ == 'simblkhrs':
                    try:
                        y, m, d = AbsTime(l1.st).split()[:3]
                    except:
                        y, m, d = 0, 0, 0
                    act = "%s/%02d%02d%02d" % (l1.activity, y, m, d)
                    l.extend([act, l1.grp])
                elif self.typ == 'landings':
                    t = l1.aibt
                    if t is None:
                        t = l1.eibt
                        if t is None:
                            t = l1.sibt
                    date = "%02d%02d%02d" % AbsTime(t).split()[:3]
                    l.extend([l1.landings, date])
            except:
                raise
                pass
            l.extend([self.month(row.tim), self.conv(row.accvalue)])
            ivalues = self.interval_values(row.tim, row.accvalue)
            svalues = [self.conv(x) for x in ivalues]
            l.extend(svalues)
            if aco is not None and aco != row.acfamily:
                self.extend(self.totals_row(aco))
                self.totals[aco] = list(self.sums)
                self.sums = [ivalues[i] for i in xrange(len(self.intervals))]
            else:
                self.sums = [(self.sums[i] + ivalues[i]) for i in xrange(len(self.intervals))]
            self.append(TR(*[TD(x) for x in l]))
            aco = row.acfamily
        if aco is not None:
            self.extend(self.totals_row(aco))
            self.totals[aco] = list(self.sums)


class TotalsTable(Table):
    """Create grand totals of all values."""

    def __init__(self, typ, intervals, *tables):
        Table.__init__(self, None, None, typ, intervals)
        acmap = {'ZZZALL': [0 for x in intervals]}
        for t in tables:
            for acfam in t.totals:
                x = t.totals[acfam]
                if acfam in acmap:
                    for i in xrange(len(intervals)):
                        acmap[acfam][i] += x[i]
                else:
                    acmap[acfam] = list(x)
                for i in xrange(len(intervals)):
                    acmap['ZZZALL'][i] += x[i]
        for acfam in sorted(acmap):
            if acfam == 'ZZZALL':
                self.append(TR(TDI('ALL'), '', '', '', '', *[TDI(self.conv(x)) for x in acmap[acfam]]))
            else:
                self.append(TR(TD(acfam), '', '', '', '', *[TD(self.conv(x)) for x in acmap[acfam]]))

    def header_row(self):
        l = ["A/C Family", '', '', '', '']
        l.extend([h for _, h in self.intervals])
        return TR(*[TH(x) for x in l])

    def caption(self):
        return "Summary"


# PRT formatting ========================================================={{{1
def TR(*a, **k):
    return prt.Row(*a, **k)


def TD(*a, **k):
    k['align'] = prt.RIGHT
    return prt.Text(*a, **k)


def TDI(*a, **k):
    k['font'] = prt.Font(style=prt.ITALIC, weight=prt.BOLD)
    k['align'] = prt.RIGHT
    return prt.Text(*a, **k)


def TH(*a, **k):
    k['font'] = prt.Font(weight=prt.BOLD)
    k['align'] = prt.RIGHT
    return prt.Text(*a, **k)


# now ===================================================================={{{1
def now():
    now, = rave.eval('fundamental.%now%')
    return now


# run_report ============================================================={{{1
def run_report(crewid, typ='blockhrs', force_html=False):
    """Has to run report in HTML format to get the Buttons to work."""
    report = 'crew_log_report.py'
    args = 'CREWID=%s TYP=%s' % (crewid, typ)
    if force_html:
        sf = Crs.CrsGetModuleResource("preferences", Crs.CrsSearchModuleDef,
                "PRTReportFormat")
        Crs.CrsSetModuleResource("preferences", "PRTReportFormat", "HTML", "")
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan',
                report, 0, args)
        Crs.CrsSetModuleResource("preferences", "PRTReportFormat", sf, "")
    else:
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan',
                report, 0, args)


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    import Cui
    crewid, = rave.eval(rave.selected(rave.Level.atom()), 'crew.%id%')
    run_report(crewid)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
