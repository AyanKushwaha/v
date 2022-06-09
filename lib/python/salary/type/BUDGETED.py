"""
Bluegarden schedule / budgeted time
"""

import os

import carmensystems.rave.api as rave

import salary.api as api
import salary.conf as conf
import salary.run as run

from tempfile import mkstemp
from salary.Budgeted import BudgetedManager
from utils.fmt import NVL


class BudgetedRun(run.GenericRun):
    def get_codes(self):
        self.articleCodes['BUDGETED_HOURS'] = '000'

    def save_run(self, rosters):
        for crew in rosters:
            for a in self.articles:
                func = getattr(self, a)
                value = func(crew)
                total = 0
                for offset in range(len(value)):
                    if value[offset] is not None and int(value[offset]) != 0:
                        self.save_extra(crew, a, value[offset], offset)
                        total = total + value[offset]
                self.save(crew, a, total)

    def rosters(self):
        # part of the "interface"
        where_expr=('salary.%%salary_system%%(%s) = "%s"' % (self.rundata.firstdate, self.rundata.extsys_for_rave()),
                    'not salary.%crew_excluded%',
                    'not crew.%%is_retired_at_date%%(%s)' % self.rundata.firstdate)
        salary_iterator = rave.iter('iterators.roster_set', where=where_expr)

        # Set parameter to limit search for records within start -> end
        old_salary_month_start = rave.param(conf.startparam).value()
        rave.param(conf.startparam).setvalue(self.rundata.firstdate)
        old_salary_month_end = rave.param(conf.endparam).value()
        rave.param(conf.endparam).setvalue(self.rundata.lastdate)
        try:
            rosters = BudgetedManager(self.rundata, conf.context, salary_iterator).getBudgetedRosters()
        finally:
            rave.param(conf.startparam).setvalue(old_salary_month_start)
            rave.param(conf.endparam).setvalue(old_salary_month_end)
        if len(rosters) == 0:
            raise api.SalaryException("No matching rosters found.")
        return rosters

    def save(self, rec, article, value):
        # part of the "interface"
        self.data.append(rec.crewId, rec.empNo, self.articleCodes[article], value)

    def save_extra(self, rec, article, value, offset):
        # part of the "interface"
        self.extradata.append(rec.crewId, self.articleCodes[article] + "%02d" % offset, value)


class S2(BudgetedRun):
    def __init__(self, record):
        articles = ['BUDGETED_HOURS']
        BudgetedRun.__init__(self, record, articles)

    def BUDGETED_HOURS(self, rec):
        return [ self.hours100(x) for x in rec.getBudgetedHours() ]

    def __str__(self):
        return 'Swedish Budgeted Time / Schedule'


class S3(BudgetedRun):
    def __init__(self, record):
        articles = ['BUDGETED_HOURS']
        BudgetedRun.__init__(self, record, articles)

    def BUDGETED_HOURS(self, rec):
        return [ self.hours100(x) for x in rec.getBudgetedHours() ]

    def __str__(self):
        return 'Swedish Budgeted Time / Schedule'
