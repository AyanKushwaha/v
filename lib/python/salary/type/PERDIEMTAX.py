
# changelog {{{2
# [acosta:07/064@09:30] First try with modular run types.
# }}}

"""
Per Diem data for taxation
"""

import os
from sets import Set
import carmensystems.rave.api as rave

import salary.api as api
import salary.conf as conf
import salary.run as run

from tempfile import mkstemp
import salary.PerDiem as PD
from utils.fmt import NVL
from AbsTime import AbsTime
from AbsDate import AbsDate
#reload(PD)


class PerDiemTaxRun(run.GenericRun):
    def run(self):
        """Overriding Base class in order to be able to create
        a monthly and yearly per diem list. The yearly list assumes
        previous months have all been calculated. """

        if self.rundata.lastdate > self.rundata.firstdate:
            runid = run.GenericRun.run(self)
        else:
            print "** No update period specified: Using old data **"
            runid = None

        if self.rundata.admcode == 'R':
            raise "No retro run"
        exist = Set()
        year, month, _ = AbsDate(int(self.rundata.lastdate)-1).split()
        if month < 12:
            firstdate = AbsTime(AbsDate(year-1,12,1))
        else:
            firstdate = AbsTime(AbsDate(year,12,1))
        lastdate = AbsTime(self.rundata.lastdate)
        print "PerDiemTaxRun w/ %s -- %s" % (str(firstdate), str(lastdate))
        if self.rundata.admcode == 'T':
            suffix = "_TEST"
        else:
            suffix = ""
        for homebase, rank, _ in api.getPerDiemGroup(self.rundata.extsys):
            rank = "ALL" # Currently we do not separate CC/FC. If requested/needed we need to add where condition as well
            if (homebase, rank) in exist:
                continue
                        
            exist.add((homebase,rank))
            args = {
                'firstdate': str(int(firstdate)),
                'lastdate': str(int(lastdate)),
                'starttime': str(int(self.rundata.starttime)),
                'extsys': self.rundata.extsys,
                'note': self.rundata.note or '',
                'admcode': self.rundata.admcode,
                'homebase': homebase,
                'fromStudio': 'FALSE',
            }
            
            # Create monthly report
            basename = "PDTAX_LIST_%s_%s_%04d_%02d%s.txt" % (self.rundata.extsys, homebase, year, month, suffix)
            filename = os.path.join(api.reportDirectory(), basename)
            #SKCMS-413 Karin Mattsson, HiQ
            firstdate_monthly=AbsTime(AbsDate(year,month,1))
            self.generateMonthlyListNO(filename, self.rundata.extsys, homebase, firstdate_monthly, lastdate, self.rundata.admcode)
            
            # Create yearly report
            basename = "PDTAX_YEARLY_IC218_%s_%s_%04d_%02d%s.pdf" % (self.rundata.extsys, homebase, year, month, suffix)
            filename = os.path.join(api.reportDirectory(), basename)
            fn = api.runReport('report_sources.include.PerDiemYearlyList', None, args=args, filename=filename)
        
        return runid
    
    def generateMonthlyListNO(self, fileName, extsys, homebase, firstdate, lastdate, admcode):
        L = ['report_common.%%crew_homebase_salary%% = "%s"' % (homebase)]
        iterator = rave.iter('iterators.roster_set', where=tuple(L), sort_by=('crew.%extperkey%'))
        rosters, perDiem = PD.getAggregatedPerDiemTax('sp_crew', iterator, firstdate, lastdate, False, admcode, extsys, homebase)
        
        f = open(fileName, "w")
        print "**** GENERATING MONTHLY LIST hb=%s ****" % (homebase)
        print str(firstdate) , str(lastdate)
        y,m,_,_,_ = lastdate.split()
        if y > 2009 or y == 2009 and m > 9:
            orgno = 961510740
        else:
            orgno = 962308449
        try:
            for crew in rosters:
                id = crew['id']
                empno = crew['empno']
                code = 610
                pd = int(100*sum([x.perDiemWithoutTax for x in perDiem[id]]))
                days = int(sum([x.perDiemDays for x in perDiem[id]]))
                if pd != 0 or days != 0: 
                    f.write("%011d%08d%03d %08d %08d %06d\n" % (orgno, int(empno), code, pd, pd, days))
        finally:
            f.close()
        print "**** DONE MONTHLY LIST ****"

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
            rosters = PD.PerDiemRosterManager(conf.context, salary_iterator).getPerDiemRosters()
        finally:
            rave.param(conf.startparam).setvalue(old_salary_month_start)
            rave.param(conf.endparam).setvalue(old_salary_month_end)
        if len(rosters) == 0:
            raise api.SalaryException("No matching rosters found.")
        return rosters

    def save(self, rec, type, value):
        # part of the "interface"
        self.data.append(rec.crewId, rec.empNo, self.articleCodes[type], value)

class NO(PerDiemTaxRun):
    def __init__(self, record):
        articles = ['PERDIEM_TAX_DAY', 'PERDIEM_SALDO', 'PERDIEM_TAX_DOMESTIC']
        PerDiemTaxRun.__init__(self, record, articles)

    def PERDIEM_TAX_DAY(self, rec):
        # 4084
        return self.times100(rec.getPerDiemDaysTaxNO())

    def PERDIEM_TAX_DOMESTIC(self, rec):
        # 4078
        return self.times100(rec.getPerDiemCompensationForTax())

    def PERDIEM_SALDO(self, rec):
        # 3065, note that the value is negated
        return self.times100(rec.getPerDiemCompensation())
    
    def __str__(self):
        return 'Norwegian Per Diem Tax'



# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
