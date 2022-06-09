
# changelog {{{2
# [acosta:07/092@11:28] First version.
# }}}

"""
Interface 43.2 AMBI list
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rv
import salary.run as run
import salary.conf as conf

from utils.rave import RaveIterator
from salary.api import SalaryException


# DK ====================================================================={{{1
class DK(run.GenericRun):
    """ AMBI only exists for Danish crew. """
    def __init__(self, rundata, articles=[]):
        run.GenericRun.__init__(self, rundata, articles=['AMBI', 'AMBINORM'])
        # AMBI norm is number of days in month * ambi hours per day
        days = int(self.rundata.lastdate - self.rundata.firstdate) / 1440.0
        norm = int(rv.param(conf.ambiparam).value()) / 60.0
        self.ambinorm = norm * days

    def __str__(self):
        return 'AMBI for Danish crew'

    def rosters(self):
        # part of the "interface"
        contractDate1 = self.rundata.firstdate
        contractDate2 = self.rundata.lastdate
        ri = RaveIterator(
            RaveIterator.iter(
                'iterators.roster_set', 
                where=('salary.%%salary_system%%(%s) = "DK"' % contractDate1,
                       'not void(crew.%region%)',
                       'not salary.%crew_excluded%',
                       'crew.%%is_active_at_date%%(%s) or crew.%%is_active_at_date%%(%s)' % (contractDate1, contractDate2),
                       'not void(crew.%%employment_date_at_date%%(%s)) or not void(crew.%%employment_date_at_date%%(%s))' % (contractDate1, contractDate2))),
                {
                'ambi': 'ambi.%%ambi_time_interval%%(%s, %s)' % (
                    self.rundata.firstdate,
                    self.rundata.lastdate,
                ),
                'crewId': 'crew.%id%',
                'empNo': 'salary.%extperkey%',
            })

        # Set parameter to limit search for records within start -> end
        old_salary_month_start = rv.param(conf.startparam).value()
        rv.param(conf.startparam).setvalue(self.rundata.firstdate)
        old_salary_month_end = rv.param(conf.endparam).value()
        rv.param(conf.endparam).setvalue(self.rundata.lastdate)

        try:
            rosters = ri.eval(conf.context)
        finally:
            rv.param(conf.startparam).setvalue(old_salary_month_start)
            rv.param(conf.endparam).setvalue(old_salary_month_end)
        if len(rosters) == 0:
            raise SalaryException("No matching rosters found.")
        return rosters

    def save(self, rec, type, value):
        # part of the "interface"
        self.data.append(rec.crewId, rec.empNo, self.articleCodes[type], value)

    def AMBI(self, rec):
        return self.hours100(rec.ambi)

    def AMBINORM(self, rec):
        return self.times100(self.ambinorm)


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
