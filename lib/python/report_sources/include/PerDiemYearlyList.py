
# coding=ISO-8859-1

"""
Per Diem Yearly List (IC218) Report.
Only used in Norway
"""

import Cui
import Cfh
import time

import carmensystems.rave.api as R
import carmstd.rave

import salary.PerDiem as pd
import salary.conf as conf

from carmensystems.publisher.api import *
from AbsTime import AbsTime
from RelTime import RelTime

from SASReport import SASReport
import utils.DisplayReport as display

from tm import TM

REPORT_TITLE = "IC218 - Norsk Beskatning - Opgitt lønns og trekkopgavene"

WIDTH_EMPNO = 70
WIDTH_PERIOD = 70
WIDTH_PERDIEM = 60
WIDTH_DAYS = 60

class PerDiemYearlyList(SASReport):
    """
    Arguments to report:

    'starttime' - Real start time of report generation.
    'firstdate' - First day of period requested.
    'lastdate'  - Last day of period requested (time point not included in
                  interval).
    'admcode'   - Optional. Type of run ('N' = Normal, 'T' = Test Run, 'R' =
                  'Retro', 'C' = 'Cancelled').
    'note'      - Optional. Comment to the run.
    'extsys'    - Optional. Salary system to use ('DK', 'NO', 'SE', ...)
    'CONTEXT'   - Optional. Context to use when iterating.
                  ('default_context', 'sp_crew') When not set, 'sp_crew'
                  will be used.
    'surname'   - Optional. Crew surname alphabet group
    """
    def create(self):
        starttime = AbsTime(int(self.arg('starttime')))
        firstdate = AbsTime(int(self.arg('firstdate')))
        lastdate = AbsTime(int(self.arg('lastdate')))
        fromStudio = (self.arg('fromStudio') == 'TRUE')
        self.crewlist = None
        self.homebase = ''
        self.extsys = 'NO'
        self.admcode = 'N'
        self.useCurrentRoster = False
        
        title = REPORT_TITLE

        context = self.arg('CONTEXT')
        if context is None:
            print "** Report server"
            # Called from report server
            if self.arg('admcode') == 'T': self.admcode = 'T' 
            note = self.arg('note')
            extsys = self.arg('extsys')
            if extsys <> self.extsys:
                raise Exception("Only 'NO' is supported as extsys")

            L = ['report_common.%%crew_salary_system_salary%% = "%s"' % (extsys)]
            L.append('not salary.%crew_excluded%')
            
            rank = self.arg('rank')
            if rank:
                L.append('salary.%%main_rank%% = "%s"' % rank)
                title += " (%s)" % rank

            homebase = self.arg('homebase')
            if homebase:
                L.append('report_common.%%crew_homebase_salary%% = "%s"' % (homebase))
                title += " (%s)" % homebase
                self.homebase = homebase

            surname = self.arg('surname')
            if surname:
                if surname[2] == "Z": 
                    L.append('crew.%%surname%% >= "%s"' % surname[0])
                    title += " (%s-)" % (surname[0])
                else:
                    L.append('crew.%%surname%% >= "%s"' % surname[0])
                    L.append('crew.%%surname%% <= "%s"' % surname[2])
                    title += " (%s-%s)" % (surname[0], surname[2])
            print "I AM SELECTING \n" + '\n'.join(L)
            retrofile = self.arg('retrofile')
            if retrofile is not None:
                # Only include crew affected by 'retro' for retro runs.
                self.crewlist = []
                f = open(retrofile, "r")
                for line in f:
                    self.crewlist.append(line.strip())
                f.close()
                title += " -- REVISED"
            iterator = R.iter('iterators.roster_set', where=tuple(L), sort_by=('crew.%surname%', 'crew.%firstname%'))
            context = 'sp_crew'
        else:
            print "** Interactive"
            note = "Interactive"
            extsys = None
            iterator = 'iterators.roster_set'
            context = global_context

        R.param('salary.%salary_month_start_p%').setvalue(firstdate)
        R.param('salary.%salary_month_end_p%').setvalue(lastdate)
        
        headerItemsDict = {}
        if fromStudio: 
            self.useCurrentRoster = True
            try:
                user = R.eval('user')[0]
            except:
                # [acosta:08/094@16:28] Non-Studio env
                import utils.Names as Names
                user = Names.username()
            nowTime, = R.eval('fundamental.%now%')
            headerItemsDict = {'By user: ':user, 'Manually created: ':nowTime, 'Type: ':'draft report'}

        print title
        SASReport.create(self, title, showPlanData=False, headers=True, headerItems=headerItemsDict)
        self.set(font=Font(size=7))
        self.generateRosterReport(context, iterator, starttime, firstdate, lastdate)
        
    def generateRosterReport(self, context, iterator, starttime, firstdate, lastdate):
        isFirst = True
        print "Crewlist is",self.crewlist
        rosters, perDiem = pd.getAggregatedPerDiemTax(context, iterator, firstdate, lastdate, self.useCurrentRoster, self.admcode, self.extsys, self.homebase, self.crewlist)

        for roster in rosters:
            if isFirst:
                isFirst = False
            else:
                self.page0()
                
            headerRow = Row(font=Font(style=ITALIC, weight=BOLD))
            headerRow.add(Column(Row(
                Text('%s, %s' % (roster['last'], roster['first']),
                     colspan=3,
                     width=200))))
            
            headerRow.add(Column(Row(
                Text('Base: %s' % (roster['base']), width=70))))
            
            
            colHeader0 = Row(font=Font(weight=BOLD))
            colHeader0.add(Column(Row(
                Text('', width=WIDTH_EMPNO+WIDTH_PERIOD+WIDTH_PERDIEM, colspan=3))))
            colHeader0.add(Column(Row(
                Text('Trekkpliktig', align=RIGHT, width=WIDTH_PERDIEM))))
            colHeader0.add(Column(Row(
                Text('Kode 610 (med overnatning)', align=RIGHT, width=2*WIDTH_PERDIEM, colspan=2))))
            colHeaders = Row(font=Font(weight=BOLD))
            colHeaders.add(Column(Row(
                Text('Ans.nr', width=WIDTH_EMPNO))))
            colHeaders.add(Column(Row(
                Text('År,måned', width=WIDTH_PERIOD))))
            colHeaders.add(Column(Row(
                Text('Per Diem', align=RIGHT, width=WIDTH_PERDIEM))))
            colHeaders.add(Column(Row(
                Text('Per Diem', align=RIGHT, width=WIDTH_PERDIEM))))
            colHeaders.add(Column(Row(
                Text('Per Diem', align=RIGHT, width=WIDTH_PERDIEM))))
            colHeaders.add(Column(Row(
                Text('Antall Døgn', align=RIGHT, width=WIDTH_DAYS))))
            #header = self.getDefaultHeader(570)
            #header.add(
            #    Isolate(Column(headerRow, colHeader0,
            #                   colHeaders)))
            #self.setHeader(header)
            first = True
            def fmt(blp):
                try:
                    # Only work with integers
                    blp = int(blp)
                except:
                    return blp
                s = str(blp)
                if len(s) < 3:
                    return "0,%02d" % int(s)
                elif len(s) >= 6:
                    return s[:-5] + "." + s[-5:-2] + "," + s[-2:]
                else:
                    return s[:-2] + "," + s[-2:]
            itemCol = Column()
            itemCol.add(headerRow)
            itemCol.add(colHeader0)
            itemCol.add(colHeaders)
            for pdr in perDiem[roster['id']]:
                month = pdr.period
                if pdr.fromRoster: month += '*'
                pdTotal = int(pdr.perDiemTotal*100)
                pdTax = int(pdr.perDiemForTaxation*100)
                pdNoTax = int(pdr.perDiemWithoutTax*100)
                pdTaxDays = pdr.perDiemDays
                dummyRow = Row()
                cval = ''
                if first:
                    cval = roster['empno']
                    first = False
                dummyRow.add(Column(Row(Text(cval, width=WIDTH_EMPNO))))
                dummyRow.add(Column(Row(Text(month, width=WIDTH_PERIOD))))
                dummyRow.add(Column(Row(Text(fmt(pdTotal), align=RIGHT, width=WIDTH_PERDIEM))))
                dummyRow.add(Column(Row(Text(fmt(pdTax), align=RIGHT, width=WIDTH_PERDIEM))))
                dummyRow.add(Column(Row(Text(fmt(pdNoTax), align=RIGHT, width=WIDTH_PERDIEM))))
                dummyRow.add(Column(Row(Text(str(pdTaxDays), align=RIGHT, width=WIDTH_DAYS))))
                itemCol.add(dummyRow)
            itemCol.add(Row(height=20))
            self.add(Isolate(itemCol))
            self.page0()
            
class reportFormDatePlan(display.reportFormDate):
    def __init__(self, hdrTitle):
        display.reportFormDate.__init__(self, hdrTitle)
    def setDefaultDates(self):
        st = AbsTime(Cui.CuiCrcEvalAbstime(
            Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%pp_start%"))
        en = AbsTime(Cui.CuiCrcEvalAbstime(
            Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%pp_end%"))
        d1 = int(st)
        d2 = int(en.month_ceil())
        return (d1,d2)
    

def runReport(scope='window'):
    global global_context

    global_context = 'default_context'
    context = global_context

    """Run PRT Report with data found in 'area', setting 'default_context'."""
    if scope == 'plan':
        area = Cui.CuiNoArea
        context = 'sp_crew'
    elif scope == 'object':
        area = Cui.CuiGetCurrentArea(Cui.gpc_info)
        crewId = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "crew.%id%")
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode, Cui.CrewMode, [crewId], 0)
        global_context = carmstd.rave.Context("window", Cui.CuiScriptBuffer)
        area = Cui.CuiNoArea
        scope = 'plan'
    else:
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, scope)
        context = 'default_context'
    
    rptForm = reportFormDatePlan('Per Diem List')
    rptForm.show(1)

    if rptForm.loop() == Cfh.CfhOk:
        nowTime, = R.eval('fundamental.%now%')
        
        args = ' '.join((
            'firstdate=%s' % rptForm.getStartDate(),
            'lastdate=%s' % rptForm.getEndDate(),
            'CONTEXT=%s' % context,
            'starttime=%s' % int(nowTime),
            'fromStudio=TRUE',
        ))
        
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope,
                                       '../lib/python/report_sources/include/PerDiemYearlyList.py', 
                                       0, args)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
