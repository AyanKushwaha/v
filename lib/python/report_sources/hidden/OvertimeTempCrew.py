

"""
Overtime Statement
"""

import carmensystems.rave.api as R
import salary.api as SALARY
import salary.conf as conf
import salary.Overtime as OT
import Cfh
import Cui

from AbsTime import AbsTime
from RelTime import RelTime
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
import utils.DisplayReport as display

EMP_NO_WIDTH = 50
NAME_WIDTH = 200
TYPE_WIDTH = 100
VALUE_WIDTH = 200

def ColW(*a, **k):
    """Column with width = VALUE_WIDTH"""
    k['width'] = VALUE_WIDTH
    return Column(*a, **k)

def TextL(*a, **k):
    """Text aligned to the left"""
    k['align'] = LEFT
    return Text(*a, **k)

class OvertimeTempCrew(SASReport):
    """
    Creates an OvertimeStatement for temporary crew for the month of current planning
    period, if created from the salary module, or for the previous month, if created 
    from the batch job (report server).

    Arguments to report:

    'starttime' - Real start time of report generation.
    'firstdate' - First day of period requested.
    'lastdate'  - Last day of period requested (time point not included in
                  interval).
    'admcode'   - Optional. Type of run ('N' = Normal, 'T' = Test Run). Note: 'retro'
                  runs do not create statement (maybe this is wrong?).
    'note'      - Optional. Comment to the run.
    'extsys'    - Optional. Salary system to use ('DK', 'NO', 'SE', ...)
    'CONTEXT'   - Optional. Context to use when iterating.
                  ('default_context', 'sp_crew') When not set, 'sp_crew'
                  will be used.
    """

    def create(self):
        starttime = AbsTime(int(self.arg('starttime')))
        firstdate = AbsTime(int(self.arg('firstdate')))
        lastdate = AbsTime(int(self.arg('lastdate')))
        crewlist = None

        title = 'Temporary Crew Statement'

        context = self.arg('CONTEXT')
        
        if context is None:
            # Called from report server
            admcode = self.arg('admcode')
            note = self.arg('note')
            extsys = self.arg('extsys')
            rosterIterator = R.iter(
                'iterators.roster_set',
                where='salary.%%salary_system%%(%s) = "%s" and crew.%%is_active_at_date%%(%s)' % (firstdate, extsys, firstdate),
                sort_by=('report_common.%crew_rank%',
                         'report_common.%employee_number%',
                         'report_common.%crew_surname%'))
            retrofile = self.arg('retrofile')
            if retrofile is not None:
                # Only include crew affected by 'retro' for retro runs.
                crewlist = []
                f = open(retrofile, "r")
                for line in f:
                    crewlist.append(line.strip())
                f.close()
                title = 'Revised Temporary Crew Statement'
            context = 'sp_crew'
        else:
            admcode = None
            note = "Interactive"
            extsys = None
            rosterIterator = 'iterators.roster_set'

        y, m = firstdate.split()[:2]
        if m == 1:
            y -= 1
            m = 12
        else:
            m -= 1
        prevStart = AbsTime(y, m, 1, 0, 0)
        prevEnd = firstdate

        rosterManager = OT.OvertimeManager(context, rosterIterator, crewlist)
        
        old_salary_month_start = R.param(conf.startparam).value()
        old_salary_month_end = R.param(conf.endparam).value()
        
        try:
            R.param(conf.startparam).setvalue(firstdate)
            R.param(conf.endparam).setvalue(lastdate)
            
            rosters = rosterManager.getOvertimeRosters()
        finally:
            R.param(conf.startparam).setvalue(old_salary_month_start)
            R.param(conf.endparam).setvalue(old_salary_month_end)

        curMonthStr, = R.eval('format_time(%s, "%%b %%Y")' % firstdate)
        
        #title = 'Overtime Statement'
        SASReport.create(self, title, showPlanData=False)

        header = self.getDefaultHeader()
        header.add(self.getTableHeader(
            items=('Emp. No', 'Name', 'Type', '%s (Corr)' % curMonthStr),
            widths=(EMP_NO_WIDTH, NAME_WIDTH, TYPE_WIDTH, VALUE_WIDTH),
            aligns=(LEFT, LEFT, LEFT, RIGHT)))
        self.setHeader(header)
        
        #look at last TEMP run
        lastTempRunIdSKD = SALARY.getLastOvertimeRunId(
            firstdate=prevStart, lastdate=lastdate, region='DK', type='TEMP_CREW')
        lastTempRunIdSKN = SALARY.getLastOvertimeRunId(
            firstdate=prevStart, lastdate=lastdate, region='NO', type='TEMP_CREW')
        lastTempRunIdSKS = SALARY.getLastOvertimeRunId(
            firstdate=prevStart, lastdate=lastdate, region='SE', type='TEMP_CREW')
        
        for roster in rosters:
            if not roster.isTemporaryTwoMonths: continue

            if roster.isSKN: lastRunId = lastTempRunIdSKN
            elif roster.isSKS: lastRunId = lastTempRunIdSKS
            else: lastRunId = lastTempRunIdSKD
            
            for row in SALARY.getRecordsForCrewId(
                roster.crewId, runid=lastRunId, firstdate=prevStart, lastdate=lastdate):
                crewId = row.crewid.id
                salaryId = row.extartid
                amount = row.amount
                
                #Ignore test runs
                if (row.runid.admcode.admcode == 'T'):
                    continue

                salarySystem = row.runid.extsys
                varStr = 'report_per_diem.%internal_article_id%'
                paramStr = '("%s", "%s", %s)' %\
                           (salaryId, salarySystem, lastdate)
                salaryType, = R.eval(varStr + paramStr)
                
                #Check if there was a run in period
                if row.runid.firstdate >= firstdate:
                    if salaryType in ('OT', 'OTPT', 'OTFC'):
                        tmpTime = RelTime((amount*60.0)/100.0)
                        isOldRun = True
                        oldOvertime = tmpTime
                else:
                    if salaryType in ('OT', 'OTPT', 'OTFC'):
                        tmpTime = RelTime((amount*60.0)/100.0)
                        isOldPrevRun = True
                        oldPrevOvertime = tmpTime
            
            self.add(Row(
                Column(Text('%s' % roster.empNo), width=EMP_NO_WIDTH),
                Column(Text('%s, %s' % (roster.lastName, roster.firstName)),
                        width=NAME_WIDTH),
                Column(width=TYPE_WIDTH),
                Column(width=VALUE_WIDTH)))
            
            if roster.isSKS:
                self.printRow('Overtime (Temp crew)',
                          roster.getOvertime(),
                          type='TEMP_HOURS')
                            
            self.printRow('Ill Temp Crew Hours',
                          roster.getIllTempCrewHours(),
                          type='TEMP_HOURS')
            
            self.printRow('Temp Crew Hours',
                          roster.getTempCrewHours(),
                          type='TEMP_HOURS')
            
            self.printRow('Temp Crew Days',
                          roster.getTempCrewDays(),
                          type='TEMP_DAYS')

            self.add(Row(Text(''),
                         Text(''),
                         Text(''),
                         Text(''),
                         border=border(bottom=0)))
            self.page()

    #@OT.debugPrint      
    def printRow(self, description, value, f=Font(), type='OT'):
        """Adds one row to the report. Zero values are removed.
        """
        printValue = (value) and (
            (type in ('TEMP_HOURS') and isinstance(value, RelTime) and not(value == RelTime(0,0)) \
            or (type in ('TEMP_DAYS') and isinstance(value, int) and not(value == 0))))
        if not(printValue): 
            return
        rowContent = []
        rowContent.append(Text(''))
        rowContent.append(Text(''))
        rowContent.append(TextL(description, font=f))
        textCol = Text('')
        if printValue: textCol = Text('%s' % value, font=f, align=LEFT)
        rowContent.append(textCol)
        self.add(Row(*rowContent))

        
def runReport():
    """Run PRT Report with data found in 'area', setting 'default_context'."""
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    try: del rptForm
    except: pass
    rptForm = display.reportFormDate('Temp Crew Statement')
    rptForm.show(1)
    if rptForm.loop() == Cfh.CfhOk:
        startDate = rptForm.getStartDate()
        endDate = rptForm.getEndDate()
        nowTime, = R.eval('fundamental.%now%')
        args = 'firstdate=%s lastdate=%s fromStudio=TRUE ' % (startDate, endDate)
        args += 'CONTEXT=default_context starttime=%d' % int(nowTime)
        
    try:
        Cui.CuiSetCurrentArea(Cui.gpc_info, area)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'WINDOW')
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, 'window',
            '../lib/python/report_sources/hidden/OvertimeTempCrew.py', 0, args)
    except Exception, e:
        print e
    return
        
# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
