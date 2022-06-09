
# changelog {{{2
# [acosta:07/078@14:06] First version
# [acosta:07/095@12:00] Refactoring...
# }}}

"""
This is report 32.17 Vacation Balance Report.
"""

# imports ================================================================{{{1
import crewlists.html as HTML
import crewlists.status as status
import utils.exception
import utils.TimeServerUtils

from tm import TM
from crewlists.replybody import Reply, ReplyError, getReportReply
from AbsTime import AbsTime
from RelTime import RelTime
from salary.accounts import CrewAccountDict, CrewAccountList
from salary.reasoncodes import REASONCODES
from utils.xmlutil import XMLElement


# We had some different opionions on which method would be best:
# S_PUBLISHED     -> balances based on sum of all future entries that are published
# S_VAYEAR        -> balance at end of vacation year (see SASCMS-1279)
# To shift method: change 'summary_mode'/'details_mode' below.
summary_modes = (S_PUBLISHED, S_VAYEAR) = xrange(2)
summary_mode = S_VAYEAR
details_modes = (D_CALENDAR_YEAR, D_VAYEAR) = xrange(2)
details_mode = D_VAYEAR


# constants =============================================================={{{1
report_name = 'VACATION'
title = "Vacation Balances and Postings"
vac_accounts = ['VA', 'VA SAVED', 'VA1', 'F7']


# VacYearError ==========================================================={{{1
class VacYearError(Exception):
    """ No vacation year found. """
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


# VacationBalanceDict ===================================================={{{1
class VacationBalanceDict(dict):
    """Dictionary with balances for each VA account."""

    all_accounts = vac_accounts + ['VA_SAVED1', 'VA_SAVED2', 'VA_SAVED3', 'VA_SAVED4', 'VA_SAVED5']

    def __init__(self, i):
        # Use account balance with all published activities
        dict.__init__(self)
        cad = CrewAccountDict(i.crewid, filter=(lambda x: x in
            self.all_accounts), published=True)

        # F7 is special, since not all crew have F7
        if i.f7_end is None: 
            self['F7'] = 0
        else:
            if summary_mode == S_PUBLISHED:
                self['F7'] = sum(cad.get('F7', 0))
            else:
                self['F7'] = sum([x for x in cad.get('F7', []) if x.tim < i.f7_end])

        self.must_be_taken = sum([x for x in cad.get('VA_SAVED5', []) if x.tim < i.va_start])

        # VA days
        if summary_mode == S_PUBLISHED:
            self['VA SAVED'] = sum(cad.get('VA_SAVED1', []),
                    cad.get('VA_SAVED2', []), cad.get('VA_SAVED3', []),
                    cad.get('VA_SAVED4', []), cad.get('VA_SAVED5', []))
            self['VA1'] = sum(cad.get('VA1', []))
            self['VA'] = sum(cad.get('VA', []))
        else:
            self['VA SAVED'] = sum([x for x in (cad.get('VA_SAVED1', []) +
                    cad.get('VA_SAVED2', []) + cad.get('VA_SAVED3', []) + 
                    cad.get('VA_SAVED4', []) + cad.get('VA_SAVED5', []))
                    if x.tim < i.va_end])
            self['VA1'] = sum([x for x in cad.get('VA1', []) if x.tim < i.va_end])
            self['VA'] = sum([x for x in cad.get('VA', []) if x.tim < i.va_end])


# VacationDetailsList ===================================================={{{1
class VacationDetailsList(list):
    """List with details for an account."""
    def __init__(self, i):
        list.__init__(self)
        if details_mode == D_CALENDAR_YEAR:
            start, end = i.year_start, i.year_end
        else:
            if i.account == 'F7':
                start, end = i.f7_start, i.f7_end
            else:
                start, end = i.va_start, i.va_end
        D = CrewAccountList(i.crewid, i.account, published=True)
        # Add running balance
        if not (i.account == 'F7' and i.f7_end is None):
            balance = 0
            for e in D:
                balance += int(e)
                if start <= e.tim < end:
                    e.balance = balance
                    self.append(e)



# XMLElement classes ====================================================={{{1

# infoTable --------------------------------------------------------------{{{2
class infoTable(HTML.table):
    """
    Create a table with crew information.
    """
    def __init__(self, i):
        """ <table>...</table> for crew information.  """
        HTML.table.__init__(self,
            'Employee no',
            'Name',
            'Requested Year'
        )
        self['id'] = "basics"
        self.append(
            i.extperkey,
            i.logname,
            "%02d" % (i.year)
        )


# vacInfoTable -----------------------------------------------------------{{{2
class vacInfoTable(XMLElement):
    """
    Create a table with vacation year start and end information.
    """
    def __init__(self, i):
        """ <table>...</table> for vacation periods.  """
        XMLElement.__init__(self)
        self.tag = 'table'
        self['id'] = "vacinfo"

        va_row = XMLElement('tr')
        va_row.append(XMLElement('th', 'Actual Vacation Period:'))
        va_row.append(XMLElement('td', '%s - %s' % (fmt_date(i.va_start), fmt_date(i.va_end))))
        self.append(va_row)

        if not (i.f7_start is None or i.f7_end is None):
            f7_row = XMLElement('tr')
            f7_row.append(XMLElement('th', 'Actual F7 Period:'))
            f7_row.append(XMLElement('td', '%s - %s' % (fmt_date(i.f7_start), fmt_date(i.f7_end))))
            self.append(f7_row)


# summaryTable -----------------------------------------------------------{{{2
class summaryTable(HTML.table):
    """
    Creates a compday summary table.
    """
    def __init__(self, s, i):
        """ <table>...</table> for crew information.  """
        HTML.table.__init__(self,
            'Account',
            'Actual Balance per %s' % fmt_date(i.now),
            'Must be taken this period',
        )
        self['id'] = "overview"
        for account in vac_accounts:
            if account == 'VA SAVED':
                must = HTML.span_right("%.0f" % (s.must_be_taken / 100.0))
            else:
                must = ''
                
            self.append(
                account, 
                HTML.span_right("%.0f" % (s.get(account, 0) / 100.0)),
                must
            )


# detailsTable -----------------------------------------------------------{{{2
class detailsTable(XMLElement):
    """
    Create a table with vacation details.
    """
    def __init__(self, d, i):
        """ <table>...</table> where activities are listed. """
        XMLElement.__init__(self)
        self.tag = 'table'
        self['id'] = 'detinfo'

        self.append(XMLElement('tr',
            XMLElement('th', 'Postings'),
            XMLElement('th', '%s' % i.account),
            XMLElement('th', 'Year: %s' % i.year),
            XMLElement('th', ''),
            XMLElement('th', '')))
        self.append(XMLElement('tr',
            XMLElement('th', 'From date'),
            XMLElement('th', 'To date'),
            XMLElement('th', 'Reason'),
            XMLElement('th', 'Posting'),
            XMLElement('th', 'Balance')))

        self['id'] = "details"
        self['border'] = "1"
        for e in d:
            from_date = fmt_date(e.tim)
            to_date = ''
            if e.is_baseline:
                reason = 'BASELINE'
            else:
                reason = e.reasoncode
                if reason == REASONCODES['OUT_ROSTER']:
                    # Add number of days, int(e) is negative
                    to_date = fmt_date(e.tim - RelTime(int(e)/100.0 + 1, 0, 0))

            is_danish_cc = i.base == "CPH" and i.cat == "C"
            f_str = "%.2f" if is_danish_cc else "%.0f"
            posting = f_str % (int(e) / 100.0)
            balance = f_str % (e.balance / 100.0)
            detRow = XMLElement('tr')
            detRow.append(XMLElement('td', from_date))
            detRow.append(XMLElement('td', to_date))
            detRow.append(XMLElement('td', reason))
            detRow.append(XMLElement('td', HTML.span_right(posting)))
            detRow.append(XMLElement('td', HTML.span_right(balance)))
            self.append(detRow)


# InputData =============================================================={{{1
class InputData:
    def __init__(self, parameters):
        self.parameters = parameters
        try:
            (noParameters, self.extperkey, self.account, year) = parameters
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Wrong number of arguments.", payload=getReportReply(report_name, parameters))
        try:
            # date in format 'YYYY'
            self.year = int(year)
            self.year_start = AbsTime(self.year, 1, 1, 0, 0)
            self.year_end = AbsTime(self.year + 1, 1, 1, 0, 0)
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Date not usable.", payload=getReportReply(report_name, parameters))

        self.crewid = None
        for x in TM.crew_employment.search('(&(extperkey=%s)(validto>%s)(validfrom<%s))' % (self.extperkey, self.year_start, self.year_end)):
            self.crewid = x.crew.id
            self.company = x.company.id
            self.base = x.base.id
            self.cat = x.titlerank.maincat.id
        if self.crewid is None:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND, "Crew with extperkey '%s' not found.." % (self.extperkey), payload=getReportReply(report_name, parameters))

        try:
            c = TM.crew[(self.crewid,)]
            self.logname = c.logname
        except:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND, "Crew logname not found for crew with extperkey '%s'." % (self.extperkey), payload=getReportReply(report_name, parameters))

        self.now = utils.TimeServerUtils.now()
        #for basic tests
        #import carmensystems.rave.api as rave
        #self.now, = rave.eval('fundamental.%now%')
        try:
            self.va_start, self.va_end = self.get_start_end('VA', self.year)
        except VacYearError, v:
            raise ReplyError('GetReport', status.DATA_ERROR, "Cannot get vacation year of type '%s' for crew '%s'. Add values to leave_entitlement." % (v, i.crewid), payload=getReportReply(report_name, i.parameters))
        try:
            self.f7_start, self.f7_end = self.get_start_end('F7', self.year)
        except VacYearError, v:
            # NOTE: Not all crew have F7!
            self.f7_start, self.f7_end = None, None

    def __str__(self):
        """ for basic tests only """
        L = ["--- !InputData"]
        L.extend(["%s : %s" % (str(x), self.__dict__[x]) for x in self.__dict__])
        return "\n".join(L)

    def get_start_end(self, account, year):
        start = year, 1, 1
        end = year + 1, 1, 1
        if(self.company=="SK" and account=="VA" and self.cat=="C"):
            if self.base == "NRT":
                start = year, 4, 1
                end = year + 1, 4, 1
            elif self.base == "HKG":
                start = year, 7, 1
                end = year + 1, 7, 1
            elif self.base == "STO":
                start = year, 6, 1
                end = year + 1, 6, 1
            elif self.base == "CPH":
                start = year, 9, 1
                end = year + 1, 9, 1
            else:
                start = year, 1, 1
                end = year + 1, 1, 1
        return AbsTime(*(start + (0, 0))), AbsTime(*(end + (0, 0)))


# fmt_date ==============================================================={{{1
def fmt_date(abstime):
    """Return date component of abstime."""
    return str(abstime).split()[0]


"""
# Run the following in Studio:

import crewlists.getreport as getrep
f = open("/home/terjeda/zzz.html","w")
f.write(getrep.report('GetReport', 'VACATION', 2, '22071', 'VA','201607'))
f.close()
"""

# run ===================================================================={{{1
def run(*a):
    """ Here is where the report gets generated. """
    try:
        assert summary_mode in summary_modes, "Internal error 'summary_mode' has a faulty value."
        assert details_mode in details_modes, "Internal error 'details_mode' has a faulty value."
        i = InputData(a)
        summary = VacationBalanceDict(i)
        details = VacationDetailsList(i)
        html = HTML.html(title="%s (%s)" % (title, i.extperkey), report=report_name)
        html.append(XMLElement('h1', title))
        html.append(XMLElement('h2', 'BASICS'))
        html.append(infoTable(i))
        html.append(vacInfoTable(i))
        html.append(XMLElement('h2', 'OVERVIEW'))
        html.append(summaryTable(summary, i))
        html.append(XMLElement('h2', i.account + " DETAILS"))
        html.append(detailsTable(details, i))
        return str(Reply('GetReport', payload=getReportReply(report_name, a, html)))

    except ReplyError, e:
        # Anticipated errors
        return str(e)

    except:
        import traceback
        traceback.print_exc
        return str(Reply('GetReport', status.UNEXPECTED_ERROR, utils.exception.getCause(), payload=getReportReply(report_name, a)))


# main ==================================================================={{{1
# for basic tests
if __name__ == '__main__':
    #print run('18194', 'VA', '2007')
    print run(3, '34225', 'VA', '2019')


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
