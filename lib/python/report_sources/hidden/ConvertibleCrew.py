

"""
After the normal overtime calculation job has run, a job to convert overtime
for crew in table salary_convertable_crew is run.  This overtime is converted
into F0-days, every 240min exceeded is one F0 day, and the remaining time is
saved.  This report displays a list of these crew.

The report was updated for CR 435.
"""

import Cui

import carmensystems.rave.api as rave
import carmensystems.publisher.api as prt
import salary.accounts as accounts
import salary.api as api
import salary.conf as conf
import salary.run as run

from report_sources.include.SASReport import SASReport
from tm import TM

from AbsDate import AbsDate


class ConvertibleCrew(dict):
    def __init__(self, runid, context=None):
        dict.__init__(self)
        if runid is None:
            rosters, = rave.eval(context,
                    rave.foreach(rave.iter('iterators.roster_set',
                        where='salary_overtime.%crew_is_convertible%'), 
                'crew.%id%', 'crew.%login_name%', 'crew.%employee_number%'))
            for (ix, crewid, logname, extperkey) in rosters:
                self[crewid] = ConvertibleCrewDataNoRunId(crewid, logname, extperkey)
        else:
            for rec in api.getExtraRecordsFor(runid):
                if rec.intartid == 'X_CONVERTIBLE_OT':
                    ccd = ConvertibleCrewData(rec)
                    self[ccd.crewid] = ccd

    def __iter__(self):
        E = [(self[x].extperkey, self[x].crewid) for x in dict.__iter__(self)]
        E.sort()
        for extperkey, crewid in E:
            yield crewid


class ConvertibleCrewDataNoRunId(dict):
    """Used when no runid is available."""
    def __init__(self, crewid, name, extperkey):
        dict.__init__(self)
        self['crewid'] = crewid
        self['name'] = name
        self['f0'] = self['f0_buffer'] = 0
        self['extperkey'] = extperkey

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        return self[key]


class ConvertibleCrewData(ConvertibleCrewDataNoRunId):
    """Used when we have a runid, where we also will show results from the
    Salary run."""
    def __init__(self, rec):
        extperkey = '??'
        for row in rec.crewid.referers('crew_employment', 'crew'):
            if row.validfrom <= rec.runid.firstdate and row.validto > rec.runid.firstdate:
                extperkey = row.extperkey
        ConvertibleCrewDataNoRunId.__init__(self, rec.crewid.id,
                rec.crewid.logname, extperkey)
        self['amount'] = rec.amount

    @property
    def new_f0(self):
        total = self['amount'] + self['f0_buffer']
        days, minutes = divmod(total, conf.convertible_time)
        return self['f0'] + days

    @property
    def new_f0_buffer(self):
        total = self['amount'] + self['f0_buffer']
        days, minutes = divmod(total, conf.convertible_time)
        return minutes


# Report ================================================================={{{1
class Report(SASReport):
    """Create a report with calculations used in the convertible crew
    calculations.  This is run as part of overtime calculations for Danish
    crew."""

    rows_per_page = 58

    def create(self):
        # runid is None means that we are running an interactive report
        # from Studio, which contains less information.
        context = self.arg('context')
        try:
            runid = int(self.arg('runid'))
        except TypeError:
            runid = None

        headerItems = {}
        if runid is None:
            starttime, = rave.eval('fundamental.%now%')
        else:
            rundata = api.getRunIdData(runid)
            starttime = rundata.starttime
            headerItems['Run ID:'] = runid
            headerItems['Period:'] = '%s - %s' % (AbsDate(rundata.firstdate),
                    AbsDate(rundata.lastdate))

        headerItems['Run Time:'] = starttime
        fromStudio = self.arg('fromStudio')
        if fromStudio is not None and bool(fromStudio):
            headerItems['Type:'] = 'Draft Report'
        SASReport.create(self, 'Convertible Overtime Report', showPlanData=False,
                         headerItems=headerItems)

        extradata = ConvertibleCrew(runid, context)
        if extradata:
            f0balances = accounts.AccountBalanceDict('F0', hi=starttime, 
                    filter=(lambda a : a.crew.id in extradata))
            f0_buffer_balances = accounts.AccountBalanceDict('F0_BUFFER',
                    hi=starttime, filter=(lambda a : a.crew.id in extradata))
            for (crew, balance) in f0balances.iteritems():
                if crew in extradata:
                    extradata[crew]['f0'] = balance / 100.0
            for (crew, balance) in f0_buffer_balances.iteritems():
                if crew in extradata:
                    extradata[crew]['f0_buffer'] = int(balance / 100.0)
            rowno = 1
            first = True
            sum_crew = sum_prev_f0 = sum_prev_f0b = sum_ot = sum_f0 = sum_f0b = 0
            for crew in extradata:
                row = extradata[crew]
                if first or rowno > self.rows_per_page:
                    if not first:
                        if not runid is None:
                            self.add_footnote()
                        self.newpage()
                    self.add_header(runid)
                    first = False
                    rowno = 1
                if runid is None:
                    self.add(prt.Row(
                        TXT(row.extperkey),
                        TXT(row.name),
                        RIGHT(TXT)(fmt_num(row.f0)),
                        RIGHT(TXT)(row.f0_buffer),
                        background=bgcolor()))
                else:
                    self.add(prt.Row(
                        TXT(row.extperkey),
                        TXT(row.name),
                        RIGHT(TXT)(fmt_num(row.f0)),
                        RIGHT(TXT)(row.f0_buffer),
                        HSpace(),
                        RIGHT(TXT)(row.amount),
                        RIGHT(TXT)(row.f0_buffer + row.amount),
                        HSpace(),
                        IT(RIGHT(TXT))(fmt_num(row.new_f0)),
                        IT(RIGHT(TXT))(row.new_f0_buffer),
                        background=bgcolor()))
                    sum_ot += row.amount
                    sum_f0 += row.new_f0
                    sum_f0b += row.new_f0_buffer
                sum_crew += 1
                sum_prev_f0 += row.f0
                sum_prev_f0b += row.f0_buffer
                rowno += 1
            if runid is None:
                self.add(prt.Row(
                    H2(TXT)("Sum"),
                    H2(TXT)(sum_crew),
                    H2(RIGHT(TXT))(fmt_num(sum_prev_f0)),
                    H2(RIGHT(TXT))(sum_prev_f0b),
                    border=prt.border(top=2)))
            else:
                self.add(prt.Row(
                    H2(TXT)("Sum"),
                    H2(TXT)(sum_crew),
                    H2(RIGHT(TXT))(fmt_num(sum_prev_f0)),
                    H2(RIGHT(TXT))(sum_prev_f0b),
                    HSpace(),
                    H2(RIGHT(TXT))(sum_ot),
                    H2(RIGHT(TXT))(sum_ot + sum_prev_f0b),
                    HSpace(),
                    H2(IT(RIGHT(TXT)))(fmt_num(sum_f0)),
                    H2(IT(RIGHT(TXT)))(sum_f0b),
                    border=prt.border(top=2)))
                if rowno <= self.rows_per_page:
                    self.add_footnote()
        else:
            if runid is None:
                self.add(prt.Row(H2(TXT)("Crew not eligible for Convertible Overtime.")))
            else:
                self.add(prt.Row(H2(TXT)("No crew eligible for Convertible Overtime found in run with ID = '%s'." % runid)))

    def add_footnote(self):
        self.add(prt.Isolate(VSpace()))
        self.add(prt.Isolate(prt.Column(
            prt.Row(prt.Column('*'),
                prt.Column(FootNoteSize(TXT)('These values are based on the current balances and will be valid first when the run is released.'))))))

    def add_header(self, runid):
        if runid is None:
            self.add(prt.Row(TXT(), TXT(),
                prt.Column(H2(TXT)('Current Values'), colspan=2)))
            self.add(prt.Row(H2(TXT)('Empno'),
                H2(TXT)('Name'),
                H2(TXT)('F0'), 
                H2(TXT)('Conv OT')))
        else:
            self.add(prt.Row(TXT(), TXT(),
                prt.Column(H2(TXT)('Current Values'), colspan=2),
                H2(TXT)(),
                prt.Column(H2(TXT)('Run ID %s' % runid), colspan=2),
                H2(TXT)(),
                prt.Column(H2(IT(TXT))('New Values*'), colspan=2)))
            self.add(prt.Row(H2(TXT)('Empno'),
                H2(TXT)('Name'),
                H2(TXT)('F0'),
                H2(TXT)('Conv OT'),
                H2(TXT)(),
                H2(TXT)('Conv OT'),
                H2(TXT)('Total Conv OT'),
                H2(TXT)(),
                H2(IT(TXT))('F0'),
                H2(IT(TXT))('Conv OT')))


# PRT formatting functions ==============================================={{{1

class BackGroundColor:
    colors = ('#ffffff', '#e5e5e5')
    def __init__(self):
        self.flag = False

    def __call__(self):
        color = self.colors[self.flag]
        self.flag = not self.flag
        return color


bgcolor = BackGroundColor()



def TXT(*a, **k):
    if 'font' in k:
        k['font'] = prt.font(**k['font'])
    return prt.Text(*a, **k)


def FootNoteSize(func):
    """Small sized font."""
    def wrapper(*a, **k):
        k.setdefault('font', {})['size'] = 6
        return func(*a, **k)
    return wrapper


def H2(func):
    """Header text level 2: size 8 bold."""
    def wrapper(*a, **k):
        k.setdefault('font', {})['size'] = 8
        k['font']['weight'] = prt.BOLD
        return func(*a, **k)
    return wrapper


def IT(func):
    """Make font italic."""
    def wrapper(*a, **k):
        k.setdefault('font', {})['style'] = prt.ITALIC
        return func(*a, **k)
    return wrapper


def RIGHT(func):
    """Make text right aligned."""
    def wrapper(*a, **k):
        k['align'] = prt.RIGHT
        return func(*a, **k)
    return wrapper


def fmt_num(n, decimals=1, divide_by=1):
    return "%.*f" % (decimals, n / float(divide_by))


def HSpace(*a, **k):
    """An empty column of width 18."""
    k['width'] = 18
    return prt.Column(*a, **k)


def VSpace(*a, **k):
    """Empty row of height 16."""
    k['height'] = 16
    return prt.Row(*a, **k)


# runReport =============================================================={{{1
def runReport(scope='window'):
    """Run PRT Report with data found in 'area', setting 'default_context'."""
    if scope == 'plan':
        area = Cui.CuiNoArea
        context = 'sp_crew'
    else:
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, scope)
        context = 'default_context'
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope,
            'ConvertibleCrew.py', 0, 'context=%s fromStudio=1' % context)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
