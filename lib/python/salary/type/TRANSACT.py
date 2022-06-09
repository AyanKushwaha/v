"""
Bluegarden deviation transactions
"""

import os

import carmensystems.rave.api as rave

import salary.api as api
import salary.conf as conf
import salary.run as run

from tempfile import mkstemp
from salary.PerDiem import PerDiemRosterManager
from utils.fmt import NVL


class TransactionsRun(run.GenericRun):
    def run(self):
        """Overriding Base class in order to be able to create
        a PerDiemStatement at the same time as the run."""
        # CR 88 - Create PerDiemStatement
        runid = run.GenericRun.run(self)
        # To be able to filter out the crew that had Per Diem in retro run.
        if self.rundata.admcode == 'R':
            fd, retro_fn = mkstemp(dir=os.environ['CARMTMP'], suffix='.tmp')
            tmpfile = os.fdopen(fd, 'w')
            for crewid in set([d.crewid for d in self.data]):
                print >>tmpfile, crewid
            tmpfile.close()
        else:
            retro_fn = None
        ix = run.IndexFile(runid, self.rundata)

        perDiemGroupReports = []
        for homebase, rank, alph_group in api.getPerDiemGroup(self.rundata.extsys, retrofile=retro_fn):
            args = {
                'firstdate': str(int(self.rundata.firstdate)),
                'lastdate': str(int(self.rundata.lastdate)),
                'starttime': str(int(self.rundata.starttime)),
                'extsys': self.rundata.extsys,
                'note': self.rundata.note or '',
                'admcode': self.rundata.admcode,
                'homebase': homebase,
                'rank': rank,
                'surname': alph_group,
                'fromStudio': 'FALSE',
            }
            if not retro_fn is None:
                args['retrofile'] = retro_fn

            basename = "PerDiemStmt_%08d_%s_%s_%s.xml" % (runid, homebase, rank, alph_group)
            perDiemGroupReports.append({'report':'Group report', 'homebase':homebase, 'rank':rank, 'surname':alph_group, 'filename':basename[:-4]+'.pdf'})
            filename = os.path.join(api.reportDirectory(), basename)
            api.runXmlReport('report_sources.include.PerDiemStatementReport',
                    runid, args=args, filename=filename, render=True)
            #ix.add(report='Individual reports', homebase=homebase, rank=rank, surname=alph_group, filename=basename[:-4]+"/index.html")

        for report in perDiemGroupReports:
            ix.add(**report)
        ix.write(api.reportFileName(runid, ext='.html'))
        if not retro_fn is None:
            os.unlink(retro_fn)
        return runid

    def rosters(self):
        # part of the "interface"
        where_expr=('salary.%%salary_system%%(%s) = "%s"' % (self.rundata.firstdate, self.rundata.extsys),
                    'not salary.%crew_excluded%')
        salary_iterator = rave.iter('iterators.roster_set', where=where_expr)

        # Set parameter to limit search for records within start -> end
        old_salary_month_start = rave.param(conf.startparam).value()
        rave.param(conf.startparam).setvalue(self.rundata.firstdate)
        old_salary_month_end = rave.param(conf.endparam).value()
        rave.param(conf.endparam).setvalue(self.rundata.lastdate)
        try:
            rosters = PerDiemRosterManager(conf.context, salary_iterator).getPerDiemRosters()
        finally:
            rave.param(conf.startparam).setvalue(old_salary_month_start)
            rave.param(conf.endparam).setvalue(old_salary_month_end)
        if len(rosters) == 0:
            raise api.SalaryException("No matching rosters found.")
        return rosters

    def save(self, rec, type, value):
        # part of the "interface"
        self.data.append(rec.crewId, rec.empNo, self.articleCodes[type], value)


class SE(TransactionsRun):
    def __init__(self, record):
        articles = ['MEAL', 'PERDIEM_SALDO', 'PERDIEM_NEG_SALDO', 'PERDIEM_TAX_DAY', 'PERDIEM_TAX_DOMESTIC', 'PERDIEM_TAX_INTER']
        TransactionsRun.__init__(self, record, articles)

    def MEAL(self, rec):
        # 841, negative in normal cases
        return -self.times100(rec.getMealReduction())

    def PERDIEM_TAX_DAY(self, rec):
        # 391
        return self.times100(rec.getPerDiemForTaxOneDaySKS())

    def PERDIEM_TAX_DOMESTIC(self, rec):
        # 396
        return self.times100(rec.getPerDiemForTaxDomesticSKS())

    def PERDIEM_TAX_INTER(self, rec):
        # 397
        return self.times100(rec.getPerDiemForTaxInternationalSKS())

    def PERDIEM_SALDO(self, rec):
        # 713 Positive saldo, see below.
        saldo = self.times100(rec.getPerDiemCompensation())
        if saldo >= 0:
            return saldo
        return 0

    def PERDIEM_NEG_SALDO(self, rec):
        # 843 According to J. Buch, 843 should be used for negative values AND
        # have a negative value.
        saldo = self.times100(rec.getPerDiemCompensation())
        if saldo < 0:
            return saldo
        return 0

    def retro(self):
        """Pecularities with Swedish PerDiem (positive values have code 713,
        and negative have 843) forces us to override the whole 'retro'
        method."""

        # First perform a "normal" run
        self._normal_test()

        pos_saldo = api.getExternalArticleId(self.rundata, 'PERDIEM_SALDO')
        neg_saldo = api.getExternalArticleId(self.rundata, 'PERDIEM_NEG_SALDO')
        any_saldo = 'SALDO'

        def cmpkey(x):
            """To be able to compare entries, 843 and 713 are the same thing."""
            if x in (pos_saldo, neg_saldo):
                # arbitrary, but unique string
                return any_saldo
            return x

        def newartid(x, amount):
            if x in (pos_saldo, neg_saldo, any_saldo):
                if amount < 0:
                    return neg_saldo
                else:
                    return pos_saldo
            return x

        # Get run id of run to reverse from 'selector' field.
        r_runid = int(self.rundata.selector)
        r_run = {}
        for rec in api.getRecordsFor(r_runid):
            r_run[(rec.extperkey, cmpkey(rec.extartid), rec.crewid.id)] = rec.amount

        for r in self.data:
            key = (r.extperkey, cmpkey(r.extartid), r.crewid)
            if key in r_run:
                r.amount -= r_run[key]
                del r_run[key]

        # It's always tricky to remove records from a list, so we'll just create a new one.
        # The self.data.append method will remove records with amount == 0.
        odata = self.data
        self.data = run.BasicData()
        for d in odata:
            self.data.append(d.crewid, d.extperkey, newartid(d.extartid, d.amount), d.amount)

        # Now, append all remaining records from r_run (with negative sign)
        for key in r_run:
            extperkey, extartid, crewid = key
            amount = -r_run[key]
            self.data.append(crewid, extperkey, newartid(extartid, amount), amount)

    def __str__(self):
        return 'Swedish Per Diem'
