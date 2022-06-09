"""
Swedish salary system.
Absence run.
"""

import os

import carmensystems.rave.api as rave

import salary.api as api
import salary.conf as conf
import salary.run as run

from tempfile import mkstemp
from salary.Absence import AbsenceManager
from utils.fmt import NVL
from tm import TM
from operator import attrgetter


class AbsenceRun(run.GenericRun):
    def get_codes(self):
        self.articleCodes['ABSENCE_HOURS'] = '42' # Place holder

    def save_run(self, rosters):
        for crew in rosters:
            for intartid in self.articles:
                func = getattr(self, intartid)
                value = func(crew)
                for extartid in value:
                    total = 0
                    for (offset, amount) in value[extartid]:
                        if amount is not None and int(amount) != 0:
                            self.save_extra(crew, extartid, amount, offset)
                            total = total + amount
                    self.save(crew, extartid, total)

    def rosters(self):
        # part of the "interface"
        where_expr=('salary.%%salary_system%%(%s) = "%s"' % (self.rundata.firstdate, self.rundata.extsys_for_rave()),
                    'not salary.%crew_excluded%')
        salary_iterator = rave.iter('iterators.roster_set', where=where_expr)

        # Set parameter to limit search for records within start -> end
        old_salary_month_start = rave.param(conf.startparam).value()
        rave.param(conf.startparam).setvalue(self.rundata.firstdate)
        old_salary_month_end = rave.param(conf.endparam).value()
        rave.param(conf.endparam).setvalue(self.rundata.lastdate)
        try:
            rosters = AbsenceManager(self.rundata, conf.context, salary_iterator).getAbsenceRosters()
        finally:
            rave.param(conf.startparam).setvalue(old_salary_month_start)
            rave.param(conf.endparam).setvalue(old_salary_month_end)
        if len(rosters) == 0:
            raise api.SalaryException("No matching rosters found.")
        return rosters

    def save(self, rec, article, value):
        # part of the "interface"
        self.data.append(rec.crewId, rec.empNo, article, value)

    def save_extra(self, rec, article, value, offset):
        # part of the "interface"
        self.extradata.append(rec.crewId, article + "%02d" % offset, value)

class S3(AbsenceRun):
    def __init__(self, record):
        articles = ['ABSENCE_HOURS']
        AbsenceRun.__init__(self, record, articles)

    def ABSENCE_HOURS(self, rec):
        return rec.getAbsenceHours()

    def __str__(self):
        return 'Swedish Absence Transactions'
