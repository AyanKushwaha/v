
# changelog {{{2
# [acosta:07/064@09:30] First try with modular run types.
# }}}

"""
Interface 44.1 Per Diem
"""

import os

import carmensystems.rave.api as rave

import salary.api as api
import salary.conf as conf
import salary.run as run

from tempfile import mkstemp
from salary.PerDiem import PerDiemRosterManager
from salary.Budgeted import BudgetedRunDataHandler
from utils.fmt import NVL


class PerDiemRun(run.GenericRun):
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

        for homebase, rank, alph_group in api.getPerDiemGroup(self.rundata.extsys_for_rave(), retrofile=retro_fn):
            args = {
                'firstdate': str(int(self.rundata.firstdate)),
                'lastdate': str(int(self.rundata.lastdate)),
                'starttime': str(int(self.rundata.starttime)),
                'extsys': self.rundata.extsys_for_rave(),
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
        where_expr=('salary.%%salary_system%%(%s) = "%s"' % \
            (self.rundata.firstdate, self.rundata.extsys_for_rave()), \
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
        # Enable reports when no entitled crew exist
        # if len(rosters) == 0:
        #     raise api.SalaryException("No matching rosters found.")
        return rosters


class DK(PerDiemRun):
    def __init__(self, record):
        articles = ['MEAL_C', 'MEAL_F', 'PERDIEM_SALDO', 'PERDIEM_TAX', 'PERDIEM_NO_TAX']
        PerDiemRun.__init__(self, record, articles)

    def MEAL_C(self, rec):
        # 1540, positive in normal cases
        if rec.mainFunc == 'C':
            return self.times100(rec.getMealReduction())
        return 0

    def MEAL_F(self, rec):
        # 1530, positive in normal cases
        if rec.mainFunc == 'F':
            return self.times100(rec.getMealReduction())
        return 0

    def PERDIEM_TAX(self, rec):
        # 2989
        return self.times100(rec.getPerDiemCompensationForTax())

    def PERDIEM_NO_TAX(self, rec):
        # 1548
        return self.times100(rec.getPerDiemCompensationWithoutTax())

    def PERDIEM_SALDO(self, rec):
        # 1550
        return self.times100(rec.getPerDiemCompensation())

    def __str__(self):
        return 'Danish Per Diem'


class NO(PerDiemRun):
    def __init__(self, record):
        articles = ['MEAL_C', 'MEAL_F', 'PERDIEM_SALDO', 'PERDIEM_TAX_DAY', 'PERDIEM_TAX_DOMESTIC']
        PerDiemRun.__init__(self, record, articles)

    def MEAL_C(self, rec):
        # 3705, positive in normal cases
        if rec.mainFunc == 'C':
            return self.times100(rec.getMealReduction())
        return 0

    def MEAL_F(self, rec):
        # 3700, positive in normal cases
        if rec.mainFunc == 'F':
            return self.times100(rec.getMealReduction())
        return 0

    def PERDIEM_TAX_DAY(self, rec):
        # 4084
        return self.times100(rec.getPerDiemForTaxOneDayNO())

    def PERDIEM_TAX_DOMESTIC(self, rec):
        # 4078
        return self.times100(rec.getPerDiemForTaxDomesticNO())

    def PERDIEM_SALDO(self, rec):
        # 3065, note that the value is negated
        return -self.times100(rec.getPerDiemCompensation())
    
    def __str__(self):
        return 'Norwegian Per Diem'


class SE(PerDiemRun):
    def __init__(self, record):
        articles = ['MEAL', 'PERDIEM_SALDO', 'PERDIEM_NEG_SALDO', 'PERDIEM_TAX_DAY', 'PERDIEM_TAX_DOMESTIC', 'PERDIEM_TAX_INTER']
        PerDiemRun.__init__(self, record, articles)

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


class S3(PerDiemRun):
    def __init__(self, record):
        articles = ['MEAL', 'PERDIEM_SALDO', 'PERDIEM_TAX_DAY', 'PERDIEM_TAX_DOMESTIC', 'PERDIEM_TAX_INTER']
        PerDiemRun.__init__(self, record, articles)

    def PERDIEM_SALDO(self, rec):
        # 713 saldo - it can be positive or negative
        saldo = self.times100(rec.getPerDiemCompensation())
        return saldo

    def MEAL(self, rec):
        # 841, negative in normal cases
        return -self.times100(rec.getMealReduction())

    def PERDIEM_TAX_DAY(self, rec):
        # 395
        return self.times100(rec.getPerDiemForTaxOneDaySKS())

    def PERDIEM_TAX_DOMESTIC(self, rec):
        # 396
        return self.times100(rec.getPerDiemForTaxDomesticSKS())

    def PERDIEM_TAX_INTER(self, rec):
        # 397
        return self.times100(rec.getPerDiemForTaxInternationalSKS())

    def __str__(self):
        return 'Swedish Per Diem'
    

class S2(PerDiemRun):
    def __init__(self, record):
        articleTypes = { 'MEAL'                : 'amount',
                         'PERDIEM_SALDO'       : 'amount',
                         'PERDIEM_TAX_DAY'     : 'amount',
                         'PERDIEM_TAX_DOMESTIC': 'amount',
                         'PERDIEM_TAX_INTER'   : 'amount' }
        PerDiemRun.__init__(self, record, articleTypes.keys(), article_types=articleTypes)

    def _normal_test(self):
        self.budgeted_run_data_handler = BudgetedRunDataHandler(self.rundata)
        PerDiemRun._normal_test(self)

    normal = _normal_test
    test = _normal_test

    def save_run(self, rosters):
        for crew in rosters:
            for a in self.articles:
                func = getattr(self, a)
                total = 0
                for (offset, value) in func(crew):
                    if value is not None and int(value) != 0:
                        self.save_extra(crew, a, value, offset)
                        total = total + value
                self.save(crew, a, total)

    def makeDayList(self, rec, value):
        last_scheduled_day = self.budgeted_run_data_handler.getLastScheduledDay(rec.crewId)
        offset = int(last_scheduled_day - self.rundata.firstdate) / (24 * 60)
        return [(offset, value)]

    def MEAL(self, rec):
        # 841, negative in normal cases
        return self.makeDayList(rec, -self.times100(rec.getMealReduction()))

    def PERDIEM_TAX_DAY(self, rec):
        # 391
        return self.makeDayList(rec, self.times100(rec.getPerDiemForTaxOneDaySKS()))

    def PERDIEM_TAX_DOMESTIC(self, rec):
        # 396
        return self.makeDayList(rec, self.times100(rec.getPerDiemForTaxDomesticSKS()))

    def PERDIEM_TAX_INTER(self, rec):
        # 397
        return self.makeDayList(rec, self.times100(rec.getPerDiemForTaxInternationalSKS()))
    
    def PERDIEM_SALDO(self, rec):
        return self.makeDayList(rec, self.times100(rec.getPerDiemCompensation()))

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


class CN(PerDiemRun):
    def __init__(self, record):
        articles = ['PERDIEM_SALDO']
        PerDiemRun.__init__(self, record, articles)
    
    def PERDIEM_SALDO(self, rec):
        return self.times100(rec.getPerDiemCompensation())

    def __str__(self):
        return 'Chinese Per Diem'


class JP(PerDiemRun):
    def __init__(self, record):
        articles = ['PERDIEM_SALDO']
        PerDiemRun.__init__(self, record, articles)
    
    def PERDIEM_SALDO(self, rec):
        return self.times100(rec.getPerDiemCompensation())

    def __str__(self):
        return 'Japanese Per Diem'

class HK(PerDiemRun):
    def __init__(self, record):
        articles = ['PERDIEM_SALDO']
        PerDiemRun.__init__(self, record, articles)

    def PERDIEM_SALDO(self, rec):
        return self.times100(rec.getPerDiemCompensation())

    def __str__(self):
        return 'Hong Kong Per Diem'


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
