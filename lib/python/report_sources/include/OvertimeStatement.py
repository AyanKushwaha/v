

"""
Overtime Statement
"""

import carmensystems.rave.api as R
import carmstd.rave
import salary.api as SALARY
import salary.conf as conf
import salary.Overtime as OT
import Cfh
import Cui

from AbsTime import AbsTime
from RelTime import RelTime

from AbsDate import AbsDate

from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
import utils.DisplayReport as display

EMP_NO_WIDTH = 40
NAME_WIDTH = 200
TYPE_WIDTH = 120
VALUE_WIDTH = 50
LINE_WIDTH = 10

def ColW(*a, **k):
    """Column with width = VALUE_WIDTH"""
    k['width'] = VALUE_WIDTH
    return Column(*a, **k)

def TextL(*a, **k):
    """Text aligned to the left"""
    k['align'] = LEFT
    return Text(*a, **k)

class OvertimeStatement(SASReport):
    """
    Creates an OvertimeStatement for the month of current planning period, if created
    from Studio or the salary module, or for three months back if created from
    the batch job (report server).
    The report also includes the previous month.

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
    'fromStudio' - Optional. True if the report is created from Studio
    """

    def create(self):
        starttime = AbsTime(int(self.arg('starttime')))
        firstdate = AbsTime(int(self.arg('firstdate')))
        lastdate = AbsTime(int(self.arg('lastdate')))
        fromStudio = (self.arg('fromStudio') == 'TRUE')
        crewlist = None
        
        global global_context
        if not global_context:
            global_context = self.arg('CONTEXT')

        title = "Overtime Statement"
        
        if global_context is None:
            # Called from report server
            admcode = self.arg('admcode')
            note = self.arg('note')
            extsys = self.arg('extsys')
            rosterIterator = R.iter(
                'iterators.roster_set',
                where='not salary.%%crew_excluded%% and salary.%%salary_system%%(%s) = "%s" and crew.%%is_active_at_date%%(%s)' % (firstdate, extsys, firstdate),
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
                title = 'Revised Overtime Statement'
            global_context = 'sp_crew'
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

        rosterManager = OT.OvertimeManager(global_context, rosterIterator, crewlist)
        
        old_salary_month_start = R.param(conf.startparam).value()
        old_salary_month_end = R.param(conf.endparam).value()
        
        try:
            R.param(conf.startparam).setvalue(prevStart)
            R.param(conf.endparam).setvalue(prevEnd)
            
            prevRosters = rosterManager.getOvertimeRosters()
                
            R.param(conf.startparam).setvalue(firstdate)
            R.param(conf.endparam).setvalue(lastdate)
            
            rosters = rosterManager.getOvertimeRosters()
        finally:
            R.param(conf.startparam).setvalue(old_salary_month_start)
            R.param(conf.endparam).setvalue(old_salary_month_end)

        curMonthStr, = R.eval('format_time(%s, "%%b %%Y")' % firstdate)
        prevMonthStr, = R.eval('format_time(%s, "%%b %%Y")' % prevStart)

        #title = 'Overtime Statement'
        headerItemsDict = {}
        if fromStudio: 
            try:
                user = R.eval('user')[0]
            except:
                # [acosta:08/094@16:28] Non-Studio env
                import utils.Names as Names
                user = Names.username()
            nowTime, = R.eval('fundamental.%now%')
            headerItemsDict = {'By user: ':user, 'Manually created: ':nowTime, 'Type: ':'draft report'}
        
        SASReport.create(self, title, showPlanData=False, orientation=LANDSCAPE, headerItems=headerItemsDict)

        header = self.getDefaultHeader()
        
        
        
        header.add(self.getTableHeader(
            items=('Emp. No', 'Name', 'Type', '%s (Corr)' % curMonthStr,
                   '','%s (Corr)' % prevMonthStr, ''),
            # The widths must add the page width, otherwise it will not look good.                                       
            widths=(EMP_NO_WIDTH, NAME_WIDTH, TYPE_WIDTH, 3*VALUE_WIDTH, 
                    LINE_WIDTH, 3*VALUE_WIDTH, 
                    self.pageWidth - EMP_NO_WIDTH - NAME_WIDTH - TYPE_WIDTH - 
                    3*VALUE_WIDTH - LINE_WIDTH - 3*VALUE_WIDTH), 
            aligns=(LEFT, LEFT, LEFT, LEFT, LEFT, LEFT, LEFT)))
        self.setHeader(header)
        
        #look at last OT/TEMP run
        #lastOTRunIdSKD = SALARY.getLastOvertimeRunId(
            #firstdate=prevStart, lastdate=lastdate, region='DK', type='OVERTIME')
        #lastOTRunIdSKS = SALARY.getLastOvertimeRunId(
            #firstdate=prevStart, lastdate=lastdate, region='SE', type='OVERTIME')
        #lastOTRunIdSKN = SALARY.getLastOvertimeRunId(
            #firstdate=prevStart, lastdate=lastdate, region='NO', type='OVERTIME')
        #lastTempRunIdSKD = SALARY.getLastOvertimeRunId(
            #firstdate=prevStart, lastdate=lastdate, region='DK', type='TEMP_CREW')
        #lastTempRunIdSKN = SALARY.getLastOvertimeRunId(
            #firstdate=prevStart, lastdate=lastdate, region='NO', type='TEMP_CREW')
        
        # Store in dictionary for better performance
        prevRosterDict = {}
        for roster in prevRosters:
            prevRosterDict[roster.crewId] = roster

        for roster in rosters:
            #Find crew in prev roster
            if not prevRosterDict.has_key(roster.crewId):
                print "Crew", roster.crewId, "has no prevRoster"
                continue
            prevRoster = prevRosterDict[roster.crewId]
            
            #This SHOULD and has to be the same value
            assert roster.crewId == prevRoster.crewId
            
            #if roster.isSKS: lastRunId = lastOTRunIdSKD
            #elif roster.isSKN: lastRunId = lastOTRunIdSKN
            #elif roster.isSKS: lastRunId = lastOTRunIdSKS
            #else: lastRunId = None
            
            oldPrevOvertime = RelTime(0)
            oldOvertime = RelTime(0)
            isOldRun = False
            isOldPrevRun = False
            for row in SALARY.getRecordsForCrewId(#runId=lastRunId,
                roster.crewId, firstdate=prevStart, lastdate=lastdate):
                crewId = row.crewid.id
                salaryId = row.extartid
                amount = row.amount
                
                #Ignore test runs
                try:
                    if (row.runid.admcode.admcode == 'T'):
                        continue
                except:
                    pass

                salarySystem = row.runid.extsys
                varStr = 'report_per_diem.%internal_article_id%'
                paramStr = '("%s", "%s", %s)' %\
                           (salaryId, salarySystem, prevEnd)
                typeOld, = R.eval(varStr + paramStr)
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
            
            overtime = roster.getOvertime()            
            if not overtime:
                overtime = RelTime(0, 0)
                
            prevOvertime = prevRoster.getOvertime()
            if not prevOvertime:
                prevOvertime = RelTime(0, 0)

            overtimeDiff = RelTime(0, 0)
            prevOvertimeDiff = RelTime(0, 0)
            if isOldRun:
                overtimeDiff = overtime - oldOvertime
            if isOldPrevRun:
                prevOvertimeDiff = prevOvertime - oldPrevOvertime
                
            showOvertime = True
            if not roster.isFlightCrew:
                showOvertime = False
                
            textOt = ""
            QA_str = " (QA)" if roster.apply_QA_CC_CJ else ""

            if roster.isConvertible:
                otText = 'Convertible Overtime' + QA_str
            elif roster.isFlightCrew:
                otText = 'Overtime (Flight Crew)' + QA_str
            elif roster.isPartTime and roster.isSKS:
                otText = 'Overtime (Part Time Crew)' + QA_str
            else:
                otText = 'Overtime' + QA_str
                
            if not showOvertime or overtime == RelTime(0, 0) and overtimeDiff == RelTime(0, 0):
                textOt = '  '
            else:
                textOt = '%s (%s)' % (overtime, overtimeDiff)
            
            ColOT = ColW(Text(textOt))
                
            if not showOvertime or prevOvertime == RelTime(0, 0) and prevOvertimeDiff == RelTime(0, 0):
                ColPrevOT = ColW(Text('  '))
            else:
                ColPrevOT = ColW(Text('%s (%s)' % (prevOvertime, prevOvertimeDiff)))
            

            self.add(Row(
                Column(Text('%s' % roster.empNo), width=EMP_NO_WIDTH),
                Column(Text('%s, %s' % (roster.lastName, roster.firstName)),
                       width=NAME_WIDTH),
                Column(Text(otText), width=TYPE_WIDTH),
                ColOT,
                ColW(Text(' ')),
                ColW(Text(' ')),
                Column(Text('||'), colour=self.HEADERBGCOLOUR, width=LINE_WIDTH),
                ColPrevOT,
                ColW(Text(' ')),
                ColW(Text(' '))))
            
            
            self.printRow('Loss of Rest (Low)', 
                          roster.getLossRestLow(),
                          prevRoster.getLossRestLow(), 
                          f=Font(weight=BOLD),
                          type='LOR')

            self.printRow('Loss of Rest (High)', 
                          roster.getLossRestHigh(),
                          prevRoster.getLossRestHigh(), 
                          f=Font(weight=BOLD),
                          type='LOR')

            if roster.getCalendarMonthPartTimeExtra() \
                    and int(roster.getCalendarMonthPartTimeExtra()) \
                    or prevRoster.getCalendarMonthPartTimeExtra() \
                            and int(prevRoster.getCalendarMonthPartTimeExtra()):
                self.printRow('Mertid', 
                          roster.getCalendarMonthPartTimeExtra(),
                          prevRoster.getCalendarMonthPartTimeExtra())
            if not roster.isSKS:
                self.printRow('Maitre de Cabin (Short Haul)',
                              roster.getMDCShortHaul(),
                              prevRoster.getMDCShortHaul(),
                              type='MDC')
                    
                self.printRow('Maitre de Cabin (Long Haul)',
                              roster.getMDCLongHaul(),
                              prevRoster.getMDCLongHaul(),
                              type='MDC')
                
                self.printRow('Senior Cabin Crew',
                              roster.getSCC(),
                              prevRoster.getSCC(),
                              type='MDC')
                
                self.printRow('Senior Cabin Crew (No Purser Planned)',
                              roster.getSCCNOP(),
                              prevRoster.getSCCNOP(),
                              type='MDC')

                self.printRow('Senior Cabin Crew (QA)',
                              roster.getSCCQA(),
                              prevRoster.getSCCQA(),
                              type='TEMP_SKN')

            else:            
                self.printRow('Maitre de Cabin',
                              roster.getMDC(),
                              prevRoster.getMDC(),
                              type='MDC')
                
                self.printRow('Senior Cabin Crew',
                              roster.getSCCAll(),
                              prevRoster.getSCCAll(),
                              type='MDC')

 
            self.printRow('Check-out on Free Day',
                           roster.getLateCheckout(),
                           prevRoster.getLateCheckout(),
                           type='OT')
            if fromStudio:
                self.printRow('Ill Temp Crew Hours',
                              roster.getIllTempCrewHours(),
                              prevRoster.getIllTempCrewHours(),
                              type='OT')
            
                self.printRow('Temp Crew Hours',
                              roster.getTempCrewHours(),
                              prevRoster.getTempCrewHours(),
                              type='OT')
                
                self.printRow('Temp Crew Days',
                              roster.getTempCrewDays(),
                              prevRoster.getTempCrewDays(),
                              type='TEMP_SKN')

            self.add(Row(Text(' '),
                         Text(' '),
                         Text(' '),
                         Text(' '),
                         Text(' '),
                         Text(' '),
                         Text('||', colour=self.HEADERBGCOLOUR),
                         Text(' '),
                         Text(' '),
                         Text(' '),
                         border=border(bottom=0)))
            self.page()

    #@OT.debugPrint      
    def printRow(self, description, value1, value2, f=Font(), type='OT',crewid='1234'):
        """Adds one row to the report. Zero values are removed.
        """
        printValue1 = (value1) and (
            (type in ('OT','MDC') and isinstance(value1, RelTime) and not(value1 == RelTime(0,0)) \
            or (type in ('LOR','TEMP_SKN') and isinstance(value1, int) and not(value1 == 0))))
        printValue2 = (value2) and (
            (type in ('OT','MDC') and isinstance(value2, RelTime) and not(value2 == RelTime(0,0)) \
            or (type in ('LOR','TEMP_SKN') and isinstance(value2, int) and not(value2 == 0))))
        if not(printValue1) and not(printValue2):
            return
        rowContent = []
        rowContent.append(Text(' '))
        rowContent.append(Text(' '))
        rowContent.append(TextL(description, font=f))
        textCol1 = Text(' ')
        textCol2 = Text(' ')
        textCol3 = Text(' ')
        if printValue1:
            if type == 'OT' or type == 'TEMP_SKN':
                textCol1 = TextL('%s' % value1, font=f)
            if type == 'MDC':
                textCol2 = TextL('%s' % value1, font=f)
            if type == 'LOR':
                textCol3 = TextL('%s' % value1, font=f)
        textPrevCol1 = Text(' ')
        textPrevCol2 = Text(' ')
        textPrevCol3 = Text(' ')
        if printValue2:
            if type == 'OT' or type == 'TEMP_SKN':
                textPrevCol1 = TextL('%s' % value2, font=f)
            if type == 'MDC':
                textPrevCol2 = TextL('%s' % value2, font=f)
            if type == 'LOR':
                textPrevCol3 = TextL('%s' % value2, font=f)
        rowContent.append(textCol1)
        rowContent.append(textCol2)
        rowContent.append(textCol3)
        rowContent.append(Text('||', colour=self.HEADERBGCOLOUR))
        rowContent.append(textPrevCol1)
        rowContent.append(textPrevCol2)
        rowContent.append(textPrevCol3)
        self.add(Row(*rowContent))
        
def setContext(scope='window'):
    global global_context

    global_context = 'default_context'
    context = global_context

    """Run PRT Report in scope 'scope'."""
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
    return (context,area)

def runReport(scope='window'):
    (context,area) = setContext(scope)
    
    # load previously used start and end dates
    try:
        start_date = R.param('parameters.%overtime_report_start_date%').value()
        end_date = R.param('parameters.%overtime_report_end_date%').value()
    except:
        start_date = None
        end_date = None
    else:
        if start_date == AbsTime('01JAN1986 0:00') or end_date == AbsTime('01JAN1986 0:00'):
            # the parameters are set to the default values - do not pass them to the form
            start_date = None
            end_date = None

    rptForm = display.reportFormDate('Overtime Statement', start_date=start_date, end_date=end_date)
    rptForm.show(True)
    if rptForm.loop() == Cfh.CfhOk:
        nowTime, = R.eval('fundamental.%now%')
        R.param('parameters.%overtime_report_start_date%').setvalue(AbsTime(rptForm.getStartDate()))
        R.param('parameters.%overtime_report_end_date%').setvalue(AbsTime(rptForm.getEndDate()))
        args = 'firstdate=%s lastdate=%s CONTEXT=%s fromStudio=TRUE starttime=%d' % (
                rptForm.getStartDate(), rptForm.getEndDate(), context, int(nowTime))
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope,
            '../lib/python/report_sources/include/OvertimeStatement.py', 0, args)
global_context = None
# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
