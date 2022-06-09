

"""
Present a quick overview over selected account.

This overview will display one crew per row and their account balances at
'qdate' (query date).
"""


import Cfh
import Cui
import carmensystems.publisher.api as prt
import utils.TimeServerUtils
import utils.cfhtools as cfhtools

from AbsTime import AbsTime
from report_sources.include.SASReport import SASReport
from salary.accounts import AccountBalanceDict
from tm import TM


class SelectAccountForm(cfhtools.BasicBox):
    """Let use select account and date."""
    def __init__(self, title="Account Balances"):
        cfhtools.BasicBox.__init__(self, title)
        self.l1 = self.c_label('Account', loc=(0, 0))
        self.f_account = self.c_string('', maxlength=10, loc=(0, 10))
        L = [a.id for a in TM.account_set]
        self.f_account.setMenuOnly(True)
        self.f_account.setMenuString(';' + ';'.join(L))
        self.l2 = self.c_label('Date', loc=(1, 0))
        self.f_date = self.c_date(int(utils.TimeServerUtils.now()), loc=(1, 10))
        self.done = self.Done(self)
        self.cancel = self.Cancel(self)
        self.build()

    @property
    def account(self):
        return self.f_account.valof()

    @property
    def date(self):
        return self.f_date.valof()


class Report(SASReport):
    rows_per_page = 58

    def create(self):
        account = self.arg('ACCOUNT')
        qdate = AbsTime(int(self.arg('QDATE')))
        SASReport.create(self, '%s Account Overview at %s' % (account, qdate), showPlanData=False)
        balances = self.get_balances(account, qdate) 
        if balances:
            rowno = 1
            first = True
            for extperkey, crewid, logname, rank, balance in balances:
                if first or rowno > self.rows_per_page:
                    if not first:
                        # space for footnote
                        self.newpage()
                    self.add(prt.Row(
                        H2('Extperkey'),
                        H2('Crew ID'), 
                        H2('Logname'),
                        H2('Rank'), 
                        H2('Balance')))
                    first = False
                    rowno = 1
                self.add(prt.Row(
                    extperkey,
                    "(%s)" % crewid,
                    logname,
                    rank,
                    prt.Text("%.1f" % (balance/100.0), align=prt.RIGHT)))
                rowno += 1
            if rowno <= self.rows_per_page:
                # space for footnote
                pass
        else:
            self.add(prt.Row(H2("No balances found for account '%s' at this time '%s'." % (account, qdate))))

    def get_balances(self, account, qdate):
        """Return sorted list of crew and their balances."""
        L = []
        for crewid, balance in AccountBalanceDict(account, qdate).iteritems():
            r_crew = TM.crew[(crewid,)]
            logname = r_crew.logname
            emp_rec = None
            for r_ce in r_crew.referers('crew_employment', 'crew'):
                if r_ce.validto > qdate and r_ce.validfrom < qdate:
                    emp_rec = r_ce
                    break
            if emp_rec is None:
                extperkey = '??'
                rank = '??'
            else:
                extperkey = emp_rec.extperkey
                rank = emp_rec.crewrank.id
            L.append((extperkey, crewid, logname, rank, balance))
        L.sort()
        return L


def H2(*a, **k):
    k['font'] = prt.Font(size=8, weight=prt.BOLD)
    return prt.Text(*a, **k)


def run(account, qdate=None):
    report = 'AccountBalances.py'
    if qdate is None:
        qdate = utils.TimeServerUtils.now()
    else:
        qdate = AbsTime(qdate)
    args = 'ACCOUNT=%s QDATE=%s' % (account, int(qdate))
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan', report,
            0, args)


def run_form():
    f = SelectAccountForm()
    if f.run() == Cfh.CfhOk:
        run(f.account, f.date)


if __name__ == '__main__':
    run_form()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
