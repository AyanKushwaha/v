"""
Swedish salary system.
Schedule run.
"""

import os

import carmensystems.rave.api as rave

import salary.api as api
import salary.conf as conf
import salary.run as run

from tempfile import mkstemp
from salary.Schedule import ScheduleManager
from utils.fmt import NVL


class ScheduleRun(run.GenericRun):
    def get_codes(self):
        self.articleCodes['SCHEDULE_HOURS'] = '000'

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
                    'not report_overtime.%is_temporary%',
                    'not crew.%%is_retired_at_date%%(%s)' % self.rundata.firstdate)
        salary_iterator = rave.iter('iterators.roster_set', where=where_expr)

        # Set parameter to limit search for records within start -> end
        old_salary_month_start = rave.param(conf.startparam).value()
        rave.param(conf.startparam).setvalue(self.rundata.firstdate)
        old_salary_month_end = rave.param(conf.endparam).value()
        rave.param(conf.endparam).setvalue(self.rundata.lastdate)
        try:
            rosters = ScheduleManager(self.rundata, conf.context, salary_iterator).getScheduleRosters()
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


class S3(ScheduleRun):
    def __init__(self, record):
        articles = ['SCHEDULE_HOURS']
        ScheduleRun.__init__(self, record, articles)

    def SCHEDULE_HOURS(self, rec):
        return [ self.hours100(x) for x in rec.getScheduledHours() ]

    def __str__(self):
        return 'Swedish schedule (S3)'
