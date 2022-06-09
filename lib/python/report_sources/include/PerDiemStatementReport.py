# [acosta:08/109@15:52] Modified the report for CR 88 + removed lots of lint.

"""
Per Diem Statement Report.
"""

import Cui
import Cfh
import time

from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime

import carmensystems.rave.api as R
import carmstd.rave

import salary.PerDiem as pd
import salary.conf as conf

def subreport(box, name, *args, **kwargs): print "Creating subreport %s" % name
old_subreport = subreport
from carmensystems.publisher.api import *
from AbsTime import AbsTime

from SASReport import SASReport
import utils.DisplayReport as display


TIME_WIDTH = 70
FLIGHT_WIDTH = 40
MEAL_WIDTH = 50
ROUTE_WIDTH = 90
PER_DIEM_WIDTH = 50
STOP_TIME_WIDTH = 50
AMOUNT_WIDTH = 40
CURRENCY_WIDTH = 50
EXCHANGE_WIDTH = 60
AMOUNT_CONV_WIDTH = 60
TAX_DEDUCT_WIDTH = 80
TAX_WIDTH = 85

TO_WIDTH = TIME_WIDTH
RANK_WIDTH = FLIGHT_WIDTH
ID_WIDTH = MEAL_WIDTH + ROUTE_WIDTH
NAME_WIDTH = PER_DIEM_WIDTH + STOP_TIME_WIDTH + AMOUNT_WIDTH
AC_QUAL_WIDTH = CURRENCY_WIDTH
BASE_WIDTH = EXCHANGE_WIDTH
ISSUED_BY_WIDTH = AMOUNT_CONV_WIDTH
ISSUED_DATE_WIDTH = TAX_DEDUCT_WIDTH
MONTH_WIDTH = TAX_WIDTH

MEAL_SUM_LABEL_WIDTH = TIME_WIDTH + FLIGHT_WIDTH + 4
SUM_LABEL_WIDTH = (ROUTE_WIDTH + PER_DIEM_WIDTH + STOP_TIME_WIDTH +
        AMOUNT_WIDTH + CURRENCY_WIDTH + EXCHANGE_WIDTH + 24)


class PerDiemStatementReport(SASReport):
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
    'TYPE'      - Optional. Can be one of 'roster' or 'trip'.
    'surname'   - Optional. Crew surname alphabet group (e.g. A-E)
    """

    def create(self):

        # Report type
        rtype = self.arg('TYPE')
        if rtype is None:
            rtype = 'roster'

        starttime = AbsTime(int(self.arg('starttime')))
        firstdate = AbsTime(int(self.arg('firstdate')))
        lastdate = AbsTime(int(self.arg('lastdate')))
        fromStudio = (self.arg('fromStudio') == 'TRUE')
        crewlist = None
        
        title = "Per Diem Statement"
        

      

        context = self.arg('CONTEXT')
        if context is None:
            # Called from report server
            admcode = self.arg('admcode')
            note = self.arg('note')
            extsys = self.arg('extsys')
            L = ['salary.%%salary_system%%(%s) = "%s"' % (firstdate, extsys)]
            L.append('(crew.%%is_active_at_date%%(%s) or crew.%%is_active_at_date%%(%s))' % (firstdate, lastdate))
            L.append('not salary.%crew_excluded%')
            rank = self.arg('rank')
            if rank is not None:
                L.append('salary.%%main_rank%% = "%s"' % rank)
            homebase = self.arg('homebase')
            
            #This is a temporary hack to remove QA crew from per diem run
            #L.append('not crew.%%has_agmt_group_qa_at_date%%(%s)'%str(firstdate))
            
            
            if homebase is not None:
                L.append('salary.%%homebase%% = "%s"' % homebase)
            surname = self.arg('surname')
            if surname is not None:
                # 'surname' comes as a pair, e.g. "A-E"
                if surname[2] == "Z": 
                    L.append('crew.%%surname%% >= "%s"' % surname[0])
                else:
                    L.append('crew.%%surname%% >= "%s"' % surname[0])
                    # Less than next letter in the alphabet
                    L.append('crew.%%surname%% < "%s"' % chr(ord(surname[2]) + 1))
            retrofile = self.arg('retrofile')
            if retrofile is not None:
                # Only include crew affected by 'retro' for retro runs.
                crewlist = []
                f = open(retrofile, "r")
                for line in f:
                    crewlist.append(line.strip())
                f.close()
                title = 'Revised Per Diem Statement'
            iterator = R.iter('iterators.roster_set', where=tuple(L), sort_by=('crew.%surname%', 'crew.%firstname%'))
            context = 'sp_crew'
        else:
            admcode = None
            note = "Interactive"
            extsys = None
            iterator = 'iterators.roster_set'
            context = global_context

        R.param('salary.%salary_month_start_p%').setvalue(firstdate)
        R.param('salary.%salary_month_end_p%').setvalue(lastdate)
        
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

        SASReport.create(self, title, showPlanData=False, showPageTotal=False, 
                         orientation=LANDSCAPE, headerItems=headerItemsDict)

        self.set(font=Font(size=7))

        old_salary_month_start = R.param(conf.startparam).value()
        R.param(conf.startparam).setvalue(firstdate)
        old_salary_month_end = R.param(conf.endparam).value()
        R.param(conf.endparam).setvalue(lastdate)
        try:
            if rtype == 'roster':
                rosters = pd.PerDiemRosterManager(context, iterator, crewlist).getPerDiemRosters()
                self.generateRosterReport(rosters, starttime, firstdate)
            elif rtype == 'trip':
                trips = pd.PerDiemTripManager(context).getPerDiemTrips()
                self.generateTripReport(trips)
            else:
                raise ValueError, 'Report does not support type %s' % rtype
        finally:
            R.param(conf.startparam).setvalue(old_salary_month_start)
            R.param(conf.endparam).setvalue(old_salary_month_end)

    def generateRosterReport(self, rosters, starttime, firstdate):
        isFirst = True

        for roster in rosters:
            subreport(self, roster.empNo)
            if not roster.trips:
                continue

            if isFirst:
                isFirst = False
            elif subreport is old_subreport: # If running in genuine PRT, this is true. If running in emulation, this is false
                self.newpage()

            headerRow = Row(font=Font(style=ITALIC, weight=BOLD))

            toCol = Column(Row(
                Text('To: %s' % roster.department, width=TO_WIDTH)))
            rankCol = Column(Row(
                Text('Cat: %s' % roster.rank, width=RANK_WIDTH)))
            idCol = Column(Row(
                Text('Employment no: %s' % roster.empNo, colspan=2,
                     width=ID_WIDTH)))
            nameCol = Column(Row(
                Text('Name: %s, %s' % (roster.lastName, roster.firstName),
                     colspan=3,
                     width=NAME_WIDTH)))
            acQualCol = Column(Row(
                Text('A/C Qual: %s' % (roster.acQuals), width=AC_QUAL_WIDTH)))
            baseCol = Column(Row(
                Text('Base: %s' % (roster.homebase), width=BASE_WIDTH)))
            issuedByCol = Column(Row(
                #Text('Issued by: %s' %  R.eval('user')[0],
                Text('', width=ISSUED_BY_WIDTH)))
            issuedDateCol = Column(Row(
                Text('Issued time: %s' % starttime, width=ISSUED_DATE_WIDTH)))
            # See documentation for time tuple.
            monthCol = Column(Row(
                Text('Roster month: %s' % time.strftime('%b %Y', firstdate.split() + (0, 0, 1, 0)),
                     width=MONTH_WIDTH)))
            headerRow.add(toCol)
            headerRow.add(rankCol)
            headerRow.add(idCol)
            headerRow.add(nameCol)
            headerRow.add(acQualCol)
            headerRow.add(baseCol)
            headerRow.add(issuedByCol)
            headerRow.add(issuedDateCol)
            headerRow.add(monthCol)

            sumBox = Column(font=Font(weight=BOLD),
                            border=border(left=2, right=2, bottom=2))
            sumRow = Row()
            sumBox.add(sumRow)

            sumLabelMealCol = Column()
            sumMealCol = Column()
            sumLabelCol = Column()
            sumPerDiemCol = Column()
            sumWithoutTaxCol = Column()
            sumForTaxCol = Column()
            sumRow.add(sumLabelMealCol)
            sumRow.add(sumMealCol)
            sumRow.add(sumLabelCol)
            sumRow.add(sumPerDiemCol)
            sumRow.add(sumWithoutTaxCol)
            sumRow.add(sumForTaxCol)

            sumLabelMealCol.add(Row(
                Text('Total Meal Reduction:',
                     align=RIGHT, colspan=2, width=MEAL_SUM_LABEL_WIDTH)))
            sumLabelCol.add(Row(
                Text('Saldo Per Diem (To be settled on next month salary):',
                     align=RIGHT, colspan=6, width=SUM_LABEL_WIDTH)))
            sumLabelCol.add(Row(
                Text('Per Diem Without Taxation:',
                     align=RIGHT, colspan=6)))
            sumLabelCol.add(Row(
                Text('Per Diem for Taxation:',
                     align=RIGHT, colspan=6)))

            sumMealCol.add(Row(Text('%.2f' % roster.getMealReduction(),
                                    align=RIGHT,
                                    width=MEAL_WIDTH+2)))
            sumMealCol.add(Row(Text('')))
            sumMealCol.add(Row(Text('')))
            sumPerDiemCol.add(Row(
                Text('%.2f' % roster.getPerDiemCompensation(),
                     align=RIGHT,
                     width=AMOUNT_CONV_WIDTH+2)))
            sumPerDiemCol.add(Row(Text('')))
            sumPerDiemCol.add(Row(Text('')))
            sumWithoutTaxCol.add(Row(Text('')))
            sumWithoutTaxCol.add(Row(
                Text('%.2f' % roster.getPerDiemCompensationWithoutTax(),
                     align=RIGHT,
                     width=TAX_DEDUCT_WIDTH+2)))
            sumWithoutTaxCol.add(Row(Text('')))
            sumForTaxCol.add(Row(Text('')))
            sumForTaxCol.add(Row(Text('')))
            sumForTaxCol.add(Row(
                Text('%.2f' % roster.getPerDiemCompensationForTax(),
                     align=RIGHT,
                     width=TAX_WIDTH+1)))

            contactRow = Row()
            sumBox.add(Isolate(contactRow))
            contactRow.add(Column(Text('Contact:'),
                                  Text('Department:'),
                                  Text('Phone:'),
                                  Text('E-mail:')))
            contactRow.add(Column(Text(roster.contact),
                                  Text(roster.contactDepartment),
                                  Text(roster.contactPhone),
                                  Text(roster.contactEmail)))

            self.generateTripReport(roster.trips, headerRow)
            self.add(Isolate(sumBox))

    def generateTripReport(self, trips, rosterHeader=None):

        headerRow = Row(
            border=border(top=2, inner_wall=1),
            font=Font(style=ITALIC, weight=BOLD))
        
        timeHeader = Column(Row(
            Text('Time (UTC)', width=TIME_WIDTH)))
        flightHeader = Column(Row(
            Text('Activity', width=FLIGHT_WIDTH)))
        mealHeader = Column(Row(
            Text('Meal Red', width=MEAL_WIDTH)))
        routeHeader = Column(Row(
            Text('Route (UTC)', width=ROUTE_WIDTH)))
        perDiemHeader = Column(Row(
            Text('No Per Diem', width=PER_DIEM_WIDTH)))
        stopTimeHeader = Column(Row(
            Text('Stop Time', width=STOP_TIME_WIDTH)))
        amountHeader = Column(Row(
            Text('Amount', width=AMOUNT_WIDTH)))
        currencyHeader = Column(Row(
            Text('Currency', width=CURRENCY_WIDTH)))
        exchangeHeader = Column(Row(
            Text('Rate of Exchange', width=EXCHANGE_WIDTH)))
        amountConvHeader = Column(Row(
            Text('Per Diem per stop', width=AMOUNT_CONV_WIDTH)))
        taxDeductHeader = Column(Row(
            Text('Per Diem without Taxation', width=TAX_DEDUCT_WIDTH)))
        taxHeader = Column(Row(
            Text('Per Diem for Taxation', width=TAX_WIDTH)))
        headerRow.add(timeHeader)
        headerRow.add(flightHeader)
        headerRow.add(mealHeader)
        headerRow.add(routeHeader)
        headerRow.add(perDiemHeader) 
        headerRow.add(stopTimeHeader)
        headerRow.add(amountHeader)
        headerRow.add(currencyHeader)
        headerRow.add(exchangeHeader)
        headerRow.add(amountConvHeader)
        headerRow.add(taxDeductHeader)
        headerRow.add(taxHeader)


        header = self.getDefaultHeader(770)
        header.add(
            Isolate(Column(rosterHeader,
                           headerRow,
                           border=border(left=2, right=2, top=2, bottom=2))))
        self.setHeader(header)
            
        for trip in trips:
            tripRow = Row(
                border=border(left=2, right=2, bottom=2, inner_wall=1))

            timeCol = Column()
            flightCol = Column()
            mealCol = Column()
            routeCol = Column()
            perDiemCol = Column()
            stopTimeCol = Column()
            amountCol = Column()
            currencyCol = Column()
            exchangeCol = Column()
            amountConvCol = Column()
            taxDeductCol = Column()
            taxCol = Column()
            tripRow.add(timeCol)
            tripRow.add(flightCol)
            tripRow.add(mealCol)
            tripRow.add(routeCol)
            tripRow.add(perDiemCol) 
            tripRow.add(stopTimeCol)
            tripRow.add(amountCol)
            tripRow.add(currencyCol)
            tripRow.add(exchangeCol)
            tripRow.add(amountConvCol)
            tripRow.add(taxDeductCol)
            tripRow.add(taxCol)

            isFirst = True
            counter = 1
            
            legs = trip.getAdjustedLegs()

            convMealReductSum = trip.getMealReductionSumHomeCurrency()
            convCompensationSum = trip.getCompensationSumHomeCurrency()
            taxDeduct = trip.getTaxDeduct()

            legsWithPerDiemExtra = trip.getLegsWithPerDiemExtra(legs)

            for leg in legsWithPerDiemExtra:
                if leg.isPerDiemExtra:
                    timeCol.add(Row(Text(str(leg.startUTC).split()[0], width=TIME_WIDTH)))
                    flightCol.add(Row(Text('', width=FLIGHT_WIDTH)))
                    mealCol.add(Row(Text('', width=MEAL_WIDTH)))
                    perDiemCol.add(Row(Text('', width=PER_DIEM_WIDTH)))
                    start = leg.startUTC.split()[-2:]
                    end = leg.endUTC.split()[-2:]
                    start = '%d:%02d' % (start[0], start[1])
                    end = '%d:%02d' % (end[0], end[1])
                    routeCol.add(Row(Text("%s %s - %s"%(leg.startStation,start,end), width=ROUTE_WIDTH)))
                    stopTimeCol.add(Row(Text(leg.perDiemStopTime, width=STOP_TIME_WIDTH)))
                    amountCol.add(Row(Text('%.2f' % float(leg.getCompensation()/100),
                                           align=RIGHT,
                                           width=AMOUNT_WIDTH)))
                    currencyCol.add(Row(Text(leg.currency,
                                             width=CURRENCY_WIDTH)))
                    exchangeCol.add(Row(Text('%.5f' % leg.exchangeRate,
                                             align=RIGHT,
                                             width=EXCHANGE_WIDTH)))
                    amountConvCol.add(Row(
                        Text('%.2f' % float(leg.getCompensationHomeCurrency()/100),
                             align=RIGHT,
                             width=AMOUNT_CONV_WIDTH)))
                    taxDeductCol.add(Row(Text('', width=TAX_DEDUCT_WIDTH)))
                    taxCol.add(Row(Text('', width=TAX_WIDTH)))
                    continue
                if isFirst:
                    timeCol.add(Row(Text(trip.startUTC,
                                         width=TIME_WIDTH)))
                    isFirst = False
                else:
                    if counter < len(legs):
                        timeCol.add(Row(Text('', width=TIME_WIDTH)))
                    else:
                        # End time in last row
                        timeCol.add(Row(Text(trip.endUTC,
                                             width=TIME_WIDTH)))

                flightCol.add(Row(
                    Text('%s' % (leg.flight), width=FLIGHT_WIDTH)))

                if leg.mealReduction:
                    mealCol.add(Row(Text(
                        '%.2f' % float(leg.getMealReductionHomeCurrency()/100),
                        align=RIGHT,
                        width=MEAL_WIDTH)))
                else:
                    mealCol.add(Row(Text('', width=MEAL_WIDTH)))
            
                start = leg.startUTC.split()[-2:]
                end = leg.endUTC.split()[-2:]
                
                start = '%d:%02d' % (start[0], start[1])
                end = '%d:%02d' % (end[0], end[1])
                route = "%s %s - %s %s" %\
                    (leg.startStation,
                    start,
                    end,
                    leg.endStation)
                routeCol.add(Row(Text(route,
                                      width=ROUTE_WIDTH)))
                
                if leg.allocatedPerDiem > 0:
                    perDiemCol.add(Row(Text(leg.allocatedPerDiem,
                                            align=RIGHT,
                                            width=PER_DIEM_WIDTH)))
                else:
                    perDiemCol.add(Row(Text('', width=PER_DIEM_WIDTH)))

                if leg.actualStopTime.getRep() > 0:
                    stopTimeCol.add(Row(Text(leg.actualStopTime,
                                             width=STOP_TIME_WIDTH)))
                else:
                    stopTimeCol.add(Row(Text('', width=STOP_TIME_WIDTH)))
                
                if leg.allocatedPerDiem > 0:

                    #XXYY                                        
                    amountCol.add(Row(Text('%.2f' % float(leg.getCompensation()/100),
                                           align=RIGHT,
                                           width=AMOUNT_WIDTH)))
                    currencyCol.add(Row(Text(leg.currency,
                                             width=CURRENCY_WIDTH)))
                    exchangeCol.add(Row(Text('%.5f' % leg.exchangeRate,
                                             align=RIGHT,
                                             width=EXCHANGE_WIDTH)))
                else:
                    amountCol.add(Row(Text('', width=AMOUNT_WIDTH)))
                    currencyCol.add(Row(Text('', width=CURRENCY_WIDTH)))
                    exchangeCol.add(Row(Text('', width=EXCHANGE_WIDTH)))

                if leg.allocatedPerDiem > 0:
                    amountConvCol.add(Row(
                        Text('%.2f' % float(leg.getCompensationHomeCurrency()/100),
                             align=RIGHT,
                             width=AMOUNT_CONV_WIDTH)))
                else:
                    amountConvCol.add(Row(Text('', width=AMOUNT_CONV_WIDTH)))
                    
                taxDeductCol.add(Row(Text('', width=TAX_DEDUCT_WIDTH)))
                taxCol.add(Row(Text('', width=TAX_WIDTH)))
                
                counter += 1

            timeCol.add(Row(Text('Total time: %s' % trip.tripTime,
                                 font=Font(weight=BOLD),
                                 width=TIME_WIDTH),
                            border=border(top=1)))
            flightCol.add(Row(Text('', width=FLIGHT_WIDTH),
                              border=border(top=1)))
            mealCol.add(Row(Text('%.2f' % float(convMealReductSum/100),
                                 font=Font(weight=BOLD),
                                 align=RIGHT,
                                 width=MEAL_WIDTH),
                            border=border(top=1)))
            if not trip.coursePerDiem:
                routeCol.add(Row(Text('', width=ROUTE_WIDTH),
                                 border=border(top=1)))
            else:
                routeCol.add(Row(
                    Text('Course', font=Font(weight=BOLD), width=ROUTE_WIDTH),
                    border=border(top=1)))
            #XXYY
            if trip.actualPerDiem == 0 :
                perDiemCol.add(Row(Text('', width=PER_DIEM_WIDTH),
                              border=border(top=1)))
            else:    
                perDiemCol.add(Row(Text('%s' % trip.actualPerDiem,
                                    font=Font(weight=BOLD),
                                    align=RIGHT,
                                    width=PER_DIEM_WIDTH),
                               border=border(top=1)))
            stopTimeCol.add(Row(Text('', width=STOP_TIME_WIDTH),
                                border=border(top=1)))
            amountCol.add(Row(Text('', width=AMOUNT_WIDTH),
                              border=border(top=1)))
            currencyCol.add(Row(Text('', width=CURRENCY_WIDTH),
                                border=border(top=1)))
            exchangeCol.add(Row(Text('', width=EXCHANGE_WIDTH),
                                border=border(top=1)))
            amountConvCol.add(Row(Text('%.2f' % float(convCompensationSum/100),
                                       font=Font(weight=BOLD),
                                       align=RIGHT,
                                       width=AMOUNT_CONV_WIDTH),
                                  border=border(top=1)))
            taxDeductCol.add(Row(Text('%.2f' % float(taxDeduct/100),
                                      font=Font(weight=BOLD),
                                      align=RIGHT,
                                      width=TAX_DEDUCT_WIDTH),
                                 border=border(top=1)))
            taxCol.add(
                Row(Text('%.2f' % float(max(convCompensationSum - taxDeduct, 0)/100),
                         font=Font(weight=BOLD),
                         align=RIGHT,
                         width=TAX_WIDTH),
                    border=border(top=1)))
        
            self.add(Isolate(tripRow))
            self.page0()


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

    # load previously used start and end dates
    try:
        start_date = R.param('parameters.%perdiemstatement_report_start_date%').value()
        end_date = R.param('parameters.%perdiemstatement_report_end_date%').value()
    except:
        start_date = None
        end_date = None
    else:
        if start_date == AbsTime('01JAN1986 0:00') or end_date == AbsTime('01JAN1986 0:00'):
            # the parameters are set to the default values - do not pass them to the form
            start_date = None
            end_date = None
    

    rptForm = display.reportFormDate('Per Diem Statement', start_date=start_date, end_date=end_date)
    rptForm.show(True)
    if rptForm.loop() == Cfh.CfhOk:
        nowTime, = R.eval('fundamental.%now%')
        R.param('parameters.%perdiemstatement_report_start_date%').setvalue(AbsTime(rptForm.getStartDate()))
        R.param('parameters.%perdiemstatement_report_end_date%').setvalue(AbsTime(rptForm.getEndDate()))
        args = 'firstdate=%s lastdate=%s CONTEXT=%s starttime=%d fromStudio=TRUE' % (
                rptForm.getStartDate(), rptForm.getEndDate(), context, int(nowTime))
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope,
            '../lib/python/report_sources/include/PerDiemStatementReport.py', 0, args)

# import pydevd
# try:
#     debughost="devapp01"
#     debugport=5678
#
#     print "Trying to connect to debugger on host \"" + debughost + "\" ,port: " + str(debugport)
#
#     pydevd.settrace(stdoutToServer=True, stderrToServer=True, host=debughost, port=debugport)
#
#     print "Connected to debugger."
#     print "Using pydevd version: " + pydevd.__file__
#
# except:
#     print "Failed to connect/attach to debugger. Continuing as normal."


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
