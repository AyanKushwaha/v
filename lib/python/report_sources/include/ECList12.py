"""
List 12 for Employee Central Performed Activities per Crew Member
"""

# Sys import
from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime
import Cui
import Cfh

# User imports
import carmensystems.publisher.api as P
import carmensystems.rave.api as R
import carmstd.rave

from utils.rave import RaveIterator
from utils.selctx import BasicContext
import utils.crewlog as crewlog
import salary.conf as conf
from utils.divtools import default as D
from report_sources.include.SASReport import SASReport
import utils.DisplayReport as display
import salary.ec.ECOvertime as Overtime
from salary.ec.ECOvertime import OvertimeRosterManager as OM
from utils.time_util import Interval
from time import clock
import utils.extiter as extiter
import utils.briefdebrief as briefdebrief

WIDTH = 25

###################################################################################
#
# TO BE CONSIDERED:
#
#  - The report shows all the activities in the month, even those who start in the
#    current month but finishes in the next month
#
#  - INFO CODE must be discussed, not yet totally implemented.
#
#  - Total resume variables are expressed with 2 decimals (Ex: 225.06 hrs.)
#
#  - Activities considered not to be shown completely, only date,station and code:
#       -> those which cover complete days (F7,F99,F7S,IL3,IL12,LA39,LA91,VA,VA1..)
#
#####################################################################################

def Col30(*a, **k):
    """A column of width 30"""
    k['width'] = 30
    return P.Column(*a, **k)


def Col20(*a, **k):
    """A column of width 20"""
    k['width'] = 20
    return P.Column(*a, **k)


def ColSAS(*a, **k):
    """A column with background color SASReport
    and font from SASReport"""
    k['font'] = P.Font(size=8, weight=P.BOLD)
    k['background'] = '#cdcdcd'
    return P.Column(*a, **k)


def Text30(*a, **k):
    """A text of width 30"""
    k['width'] = 30
    return P.Text(*a, **k)


def CellText(*a, **k):
    k["align"] = P.RIGHT
    return P.Text(*a, **k)


def ConditionalHighlight(isBold=False, *a, **k):
    """A text which is bold if isBold=True"""
    if isBold:
        k['font'] = P.Font(weight=P.BOLD)
        k["border"] = P.border(bottom=1)
    return CellText(*a, **k)


# List12 ================================================================={{{1
class ECList12(SASReport):
    """
    Creates a List 12 report
    """
    def create(self, context=None, reportType='roster'):

        if self.arg('scheduled') == 'yes':
            # Monthly run through report server
            # Make report for previous month
            bc = BasicContext()
            context = bc.getGenericContext()
            monthsBack = -1*int(self.arg('monthsBack'))
            (now, startDate, endDate) = R.eval(
                   'fundamental.%now%',
                   'add_months(report_common.%%month_start%%, %s)' % monthsBack,
                   'add_months(report_common.%%month_start%%, %s)' % (monthsBack + 1))
        elif not context:
            context = global_context
            startDate = AbsTime(int(self.arg('startDate')))
            endDate = AbsTime(int(self.arg('endDate')))
        else:
            (startDate, endDate) = R.eval('calendar.%month_start%',
                                          'calendar.%month_end%')
            
        # check if report is generated from Studio or from the scheduler
        fromStudio = not (self.arg('scheduled') == 'yes')
        
        ranks = []
        ranksExcl = []
        # if not from Studio, check selected base, company and main rank
        if not fromStudio:
            base = self.arg('base')
            company = self.arg('company')
            mainRank = self.arg('mainRank')
            if self.arg('ranks') is not None:
                ranks = [self.arg('ranks')]
            if self.arg('ranksExcl') is not None:
                ranksExcl =  [self.arg('ranksExcl')]
        
        now, = R.eval('fundamental.%now%')
        R.param(conf.startparam).setvalue(startDate)
        R.param(conf.endparam).setvalue(endDate)
        
        ms, = R.eval('salary.%salary_month_start_p%')
        me, = R.eval('salary.%salary_month_end_p%')
        
        lastDayMonthAbs, = R.eval('report_common.%last_day_salary_month% + 23:59')
        lastDayMonthStr = abs_to_str(lastDayMonthAbs)
        lastDayMonth = int(lastDayMonthStr[0:2])
        
        if fromStudio:
            whereStatement = 'fundamental.%is_roster%'
        else:
            if mainRank == "CA": isCabinCrew = True
            elif mainRank == "FD": isCabinCrew = False
            
            whereStatement = 'report_common.%%crew_homebase_at_date%%(%s) = \"%s\"' % (startDate,base) 
            whereStatement += ' and crew.%%is_cabin%% = %s' % isCabinCrew 
            whereStatement += ' and crew.%%company_at_date%%(%s) = \"%s\"' % (startDate,company)
            for rank in ranks:
                whereStatement += ' and crew.%%crewrank_at_date%%(%s) = \"%s\"' % (startDate,rank)
            for rank in ranksExcl:
                whereStatement += ' and crew.%%crewrank_at_date%%(%s) <> \"%s\"' % (startDate,rank)
            
        rosterIterator = RaveIterator.iter('iterators.roster_set', where=whereStatement)
        crewIterator = RaveIterator(          
            rosterIterator,
            {'crewNumber': 'report_common.%%employee_number_at_date%%(%s)' % startDate,
             'base': 'report_common.%%crew_homebase_at_date%%(%s)' % startDate,
             'company': 'crew.%%company_at_date%%(%s)' % startDate,
             'region': 'salary_overtime.%region%',
             'crewId': 'crew.%id%',
             'isCabin': 'crew.%is_cabin%',
             'categoryStart': 'crew.%rank%',
             'categoryEnd': 'crew.%rank_end%',
             'restrictions': 'concat(crew.%%restrs_type_at_date%%(\"MEDICAL\",%s),' % startDate +
                     'crew.%%restrs_type_at_date%%(\"TRAINING\",%s),' % startDate +
                     'crew.%%restrs_type_at_date%%(\"NEW\",%s))' % startDate,
             'qualns': 'concat(crew.%%qlns_type_at_date%%(\"LCP\",%s),' % startDate +
                     'crew.%%qlns_type_at_date%%(\"INSTRUCTOR\",%s),' % startDate +
                     'crew.%%qlns_type_at_date%%(\"POSITION\",%s))' % startDate,
             'lastName': 'report_common.%crew_surname%',
             'firstName': 'report_common.%crew_firstname%',
             'acQuals': 'report_common.%%ac_quals_at_date%%(%s)' % startDate,
             'station': 'crew.%%station_at_date%%(%s)' % startDate,
             'groupType': 'crew.%%group_at_date%%(%s)' % startDate,
             'cycleStart': 'crew.%%cycle_start_at_day%%(%s)' % startDate,
             'monthYear':'report_overtime.%month_start%',
             'isTemporary':'report_overtime.%is_temporary%',
             'isConvertible':'report_overtime.%is_convertible%',
             'isShortHaul':'crew.%is_short_haul_pp_start%',
             'blockTime6Months': 'report_common.%%block_time_6_months%%(%s)' % endDate,
             'blockTime12Months': 'report_common.%%block_time_12_months%%(%s)' % endDate,
             'hasFirstLossRestHigh': 'report_common.%is_first_loss_of_rest_high%',
             'firstLossRestHighStr': 'report_common.%first_loss_of_rest_high_str%',
             'hasFirstLossRestLow': 'report_common.%is_first_loss_of_rest_low%',
             'firstLossRestLowStr': 'report_common.%first_loss_of_rest_low_str%',
             'blockTimeInMonthSalary': 'roster.%%block_time_in_period%%(%s, %s)' % (startDate, endDate),
             'totalDutyTimeHB': 'report_common.%%roster_duty_time_in_period_hb%%(%s, %s)' % (startDate, endDate),
             'totalDutyTimeUTC': 'report_common.%%roster_duty_time_in_period%%(%s, %s)' % (startDate, endDate),
             'is4ExngFCOtValid':     'report_overtime.%4exng_fc_ot_valid%',
       })
        wopIterator = RaveIterator(
            RaveIterator.iter('iterators.wop_set',
                              where='report_common.%wop_in_month% or ' + \
                                    'studio_select.%%wop_is_touching%%(%s,%s)' % \
                                     (startDate,endDate)),
            {'dutyTime7x24':'report_overtime.%duty_time_wop_7x24%',
             'inPeriod':'salary_overtime.%wop_in_period%'})
        dutyIterator = extiter.ExtRaveIterator(
            RaveIterator.iter('iterators.duty_set',
                              where='report_common.%duty_in_month% or ' + \
                                    'studio_select.%%duty_is_touching%%(%s,%s)' % \
                                     (startDate,endDate)),
            {'dutyTime': 'report_common.%duty_duty_time_list_twelve%',
             'dutyTimeNoNight':'report_common.%duty_duty_time_list_twelve_no_night_upg%',
             'dutyTime7x24': 'report_overtime.%overtime_7x24_fwd_duty%',
             'dutyTime7CalendarDays': 'report_overtime.%overtime_7_calendar_days_duty%',
             'touchesSunday':'report_common.%%duty_is_touching_sunday%%(%s)' % startDate,
             'isLastInMonth': 'report_common.%duty_is_last_in_calendar_month%',
             'calendarWeek': 'report_overtime.%overtime_calendar_week_duty%',
             'followedByMinRest': 'report_common.%duty_followed_by_minimum_rest%',
             'isLossRestHigh':'report_common.%is_loss_of_rest_high%',
             'isLossRestLow':'report_common.%is_loss_of_rest_low%',
             'lossOfRestHigh':'report_common.%loss_of_rest_high_str%',
             'lossOfRestLow':'report_common.%loss_of_rest_low_str%',
             }, modifier=SimBriefDebriefExtender)
        legIterator = RaveIterator(
            RaveIterator.iter('iterators.leg_set',
                              where='report_common.%leg_in_month% or ' + \
                                     'studio_select.%%leg_is_touching%%(%s,%s)' % \
                                      (startDate,endDate)),
            {'startDate':'leg.%start_utc%',
             'startDateHb':'leg.%start_hb%',
             'endDate':'leg.%end_utc%',
             'nextLegStart':'report_common.%next_activity_start_UTC%',
             'deadhead':'leg.%is_deadhead%',
             'dutyCode':'report_common.%duty_code%',
             'mealCode':'report_common.%meal_code%',
             'tempIllCode': 'report_common.%temp_ill_code%',
             'boughtDayCode': 'report_common.%bought_day_code%',
             'baseBreakCode': 'report_common.%base_break_code%',
             'privateTradeCode' : 'report_common.%private_trade_code%', 
             'activity':'report_common.%leg_code%',
             'acType':'report_common.%ac_type%',
             'depStn':'report_common.%start_stn%',
             'arrStn':'report_common.%end_stn%',
             'scheduledStart':'leg.%activity_scheduled_start_time_utc%',
             'scheduledEnd':'leg.%activity_scheduled_end_time_utc%',
             'isBreak':'leg.%is_standby_with_break%',
             'time':'report_common.%leg_time%',
             'dutyPass':'report_overtime.%overtime_dutypass_duty%',
             'mdc':'default(salary_overtime.%maitre_de_cabin_long_haul_leg%,0:00) + default(salary_overtime.%maitre_de_cabin_short_haul_leg%,0:00)',
             'scc':'salary_overtime.%senior_cc_allowance_leg%',
             'restEnd':'report_common.%rest_end_str%',
             'isLastInDuty':'leg.%is_last_in_duty%',
             'isShortHaul' :'leg.%is_short_haul%',
             'isFlight':'leg.%is_flight_duty%',
             'isOnDuty':'leg.%is_on_duty%',
             'is24hActivity':'leg.%is_whole_day_activity%',
             'isTouchingHb':'report_common.%%leg_is_touching_hb%%(%s,%s)' % (
                 startDate + RelTime(0,1),lastDayMonthAbs),
             'isTouching':'report_common.%%leg_is_touching%%(%s,%s)' % (
                 startDate + RelTime(0,1),lastDayMonthAbs),
             'is_simulator': 'report_crewlists.%leg_is_simulator%',
             'leg_checkin': 'report_crewlists.%leg_check_in%',
             'leg_checkout': 'report_crewlists.%leg_check_out%',
             })

        dutyIterator.link({'legs':legIterator})
        wopIterator.link({'duties':dutyIterator})
        crewIterator.link({'wops':wopIterator})

        crewMembers = crewIterator.eval(context)

        # now the overtime manager module will be used, as there are some
        #  values calculated there (flight crew overtime, mainly)
        crewOtMembers = OM(context, iterator=rosterIterator)
        otDict = {}
        mertidDict = {}
        lrhDict = {}
        lrlDict = {}
        tempHDict = {}
        tempIDict = {}
        tempDDict = {}
        mdcSHDict = {}
        mdcLHDict = {}
        mdcDict = {}
        sccDict = {}
        otBalanced = {}
        otReschedDict = {}
        mertidParttimeCcDict = {}
        mertidParttimeCcLongDict = {}
        overtimeParttimeCcDict = {}
        overtimeParttimeCcLongDict = {}
        for r in crewOtMembers.getOvertimeRosters():
            overtime = r.getOvertime()
            if not overtime:
                overtime = RelTime(0)
            otDict[r.crewId] = overtime
            lrhDict[r.crewId] = r.getLossRestHigh()
            lrlDict[r.crewId] = r.getLossRestLow()
            tempHDict[r.crewId] = r.getTempCrewHours()
            tempIDict[r.crewId] = r.getIllTempCrewHours()
            tempDDict[r.crewId] = r.getTempCrewDays()
            sccDict[r.crewId] = r.getSCC()
            mertidDict[r.crewId] = r.getCalendarMonthPartTimeExtra()
            mdcSHDict[r.crewId] = r.getMDCShortHaul()
            mdcLHDict[r.crewId] = r.getMDCLongHaul()
            mdcDict[r.crewId] = r.getMDC()
            otBalanced[r.crewId] = D(r.getOtContributors(), [])
            otBalanced[r.crewId].sort()
            otReschedDict[r.crewId] = r.getContributingPart(Overtime.OT_PART_LATE_CHECKOUT, False)
            mertidParttimeCcDict[r.crewId] = r.getMertidParttimeCc()
            mertidParttimeCcLongDict[r.crewId] = r.getMertidParttimeCcLong()
            overtimeParttimeCcDict[r.crewId] = r.getOvertimeParttimeCc()
            overtimeParttimeCcLongDict[r.crewId] = r.getOvertimeParttimeCcLong()
            
        totals = [otDict, lrhDict, lrlDict, tempHDict, tempIDict, tempDDict,
                  sccDict, mdcSHDict, mdcLHDict, mdcDict, otReschedDict, mertidDict, mertidParttimeCcDict,
                  mertidParttimeCcLongDict, overtimeParttimeCcDict, overtimeParttimeCcLongDict]

        thisMonth = str(startDate)[2:9].capitalize()
        
        if fromStudio:
            try:
                user = R.eval('user')[0]
            except:
                # [acosta:08/094@16:28] Non-Studio env
                import utils.Names as Names
                user = Names.username()
            headerItems = {"Month: ": thisMonth,
                           "Manually created: ": str(now)[0:9],
                           "By user: ":user, 
                           'Type: ':'draft report'}
        else:
            headerItems={"Month: ": thisMonth,
                         "Company: ": company,
                         "Base: ": base,
                         "Main Rank: ": mainRank,
                         "Run Date: ": str(now)[0:9]}

        SASReport.create(self,
                         'EC List 12 - Performed Activities per Crew Member',
                         #orientation=P.LANDSCAPE,
                         showPlanData=False,
                         headers=True,
                         headerItems=headerItems)

        #now it's checked if the company is BU and the base is not OSL, SVG or TRD,
        # which is a combination not possible by the moment
        if not fromStudio:
            if company == "BU" and not (base in ["OSL","SVG","TRD"]):
                self.add(P.Isolate(
                    P.Row(P.Row(height=50),
                          P.Row(P.Column(),
                                P.Column(P.Text("- Combination not possible:  ",
                                                padding=P.padding(30,20,0,0),
                                                font=P.Font(size=12)),
                                                P.Text("Company = %s and Base = %s" % (company,base),
                                                       padding=P.padding(45,5,0,0),
                                                       font=P.Font(weight=P.BOLD,size=13)),
                                                P.Text("- BU only matches with OSL, SVG or TRD",
                                                       padding=P.padding(30,15,0,0),
                                                       font=P.Font(size=12)))),
                          P.Row(P.Column(P.Text())))))

        
        firstCrew = True
        crew_n = 0
        crew_ct = len(crewMembers)
        for crew in crewMembers:
            otRolling = otBalanced[crew.crewId]

            legActualDay = abs_to_str(startDate)
            currentDayAbsTime = startDate
            lastDay = abs_to_str(endDate - RelTime('24:00'))
            numDays = 1
            numHours = 0
            is4ExngFCOtValid =crew.is4ExngFCOtValid
            
            crew_n += 1
            if not firstCrew:
                self.newpage()
            else:
                firstCrew = False
            
            header = self.getDefaultHeader()
            
            #Perkey, crew number
            crewRow = P.Row(P.Text('%s   ' % crew.crewNumber,
                                   font=self.HEADERFONT))
            #category
            if crew.categoryStart == crew.categoryEnd:
                crewRow.add(P.Text('%s   ' % crew.categoryStart, font=self.HEADERFONT))
            else:
                crewRow.add(P.Text('%s - %s' % (crew.categoryStart, crew.categoryEnd),
                               font=self.HEADERFONT))
            #restriction subtype
            if not crew.restrictions == "":
                crewRow.add(P.Text('Restrs:', font=P.Font(size=9)))
                crewRow.add(P.Text('%s ' % crew.restrictions,
                                   font=self.HEADERFONT))
            #qualification subtype
            if not crew.qualns == "":
                crewRow.add(P.Text('Quals:', font=P.Font(size=9)))
                crewRow.add(P.Text('%s ' % crew.qualns, font=self.HEADERFONT))
            #last name
            crewRow.add(P.Text('%s,' % crew.lastName, font=self.HEADERFONT))
            #first name
            firstNameStr = crew.firstName
            if len(crew.lastName + crew.firstName) >= 32:
                n = 32 - len(crew.lastName) + 1
                firstNameStr = crew.firstName[:n]
            crewRow.add(P.Text('%s   ' % firstNameStr, font=self.HEADERFONT))
            crewRow.add(P.Text('Acqual:',font=P.Font(size=9)))
            crewRow.add(P.Text('%s ' % crew.acQuals, font=self.HEADERFONT))
            crewRow.add(P.Text('Station:',font=P.Font(size=9)))
            crewRow.add(P.Text('%s ' % crew.station, font=self.HEADERFONT))
            crewRow.add(P.Text('Group Type:',font=P.Font(size=9)))
            crewRow.add(P.Text('%s ' % crew.groupType, font=self.HEADERFONT))
            crewRow.add(P.Text('Cycle Start:',font=P.Font(size=9)))
            crewRow.add(P.Text('%s ' % crew.cycleStart, font=self.HEADERFONT))

            
            header.add(P.Isolate(crewRow))
            header.add(P.Row(P.Text(" ", font=P.Font(size=4))))
            self.setHeader(header)

            #checking if there are activities for the selected crew
            wopLen = len(crew.chain('wops'))
            
            #body = P.Column()

            if not wopLen == 0:
                subheader = self.create_subheader(crew.isCabin, is4ExngFCOtValid, crew.region, 
                                                  crew.categoryStart, crew.categoryEnd)
                self.add(subheader)
            else:
                self.add(P.Row(P.Text("No activities for crew number %s" %
                                      crew.crewNumber,
                                      font=P.Font(size=10,weight=P.BOLD),
                                      colour="#0000ff", height=50)))
                
            bgColor = '#ffffff'

            #this is used for calculation of totals
            wopLoop = 0
            
            totalDutyTime = RelTime(0)
            totalBlockTime = RelTime(0)
            calendarMonth = ''
            legPreviousDay = abs_to_str(startDate)
            activityOnFirstDay = False
            activityOnLastDay = False
            highlight = False
            
            dutiesLossRestHigh = []
            dutiesLossRestLow = []
            
            for wop in crew.chain('wops'):
                wopLoop += 1
                dutyLoop = 0
                dutyLen = len(wop.chain('duties'))
    
                # duty time 7x24 is only displayed on last leg in wop
                dutyTime7x24 = ''
                dutyTime7x24Rolling = ''
                
                for duty in wop.chain('duties'):
                    dutyLoop += 1
                    legLoop = 0
                    legLen = len(duty.chain('legs'))

                    # dutyTime, overtime 1x24 and calendar Week 
                    # are only displayed on last leg in duty
                    dutyTime = ''
                    overtime1x24 = ''
                    calendarWeek = ''
                    sundayMark = ''
                    dutyTime7CalendarDays = ''
                    
                    # append all loss of rest strings to be shown in the total part of the report
                    if duty.isLossRestHigh: dutiesLossRestHigh.append(duty.lossOfRestHigh)
                    if duty.isLossRestLow: dutiesLossRestLow.append(duty.lossOfRestLow)
                        
                    for leg in duty.chain('legs'):
                        highlightRolling1x24 = False
                        highlightRolling7x24 = False
                        highlightDutyPass = False
                       
                        # dutyPass is only displayed in the last leg of the duty pass
                        dutyPass = ''
                        
                        # Don't count those legs which are not included in the month
                        if leg.is24hActivity:
                            (legStart, legIsTouching) = (leg.startDateHb, leg.isTouchingHb)
                        else:
                            (legStart, legIsTouching) = (leg.startDate, leg.isTouching)
                        if not legIsTouching:
                            break

                        # check if there is a page break, and create a header if so
                        legPreviousDay = legActualDay
                        legLoop += 1
                        strDate = "%s%s" % (str(leg.startDate)[:2],str(leg.startDate)[2:5].capitalize())
                        
                        if legLoop == legLen and duty.touchesSunday:
                            calendarWeek = str(D(duty.calendarWeek,''))
                            sundayMark = '*'
                        else:
                            calendarWeek = ''
                            sundayMark = ''
                        
                        if leg.isOnDuty:
                            if leg.isFlight and not leg.deadhead:
                                totalBlockTime += leg.time
                                    
                            if legLoop == legLen:
                                if (crew.isCabin and crew.region == 'SKD'):
                                    dutyTime = str(D(duty.dutyTimeNoNight,""))
                                else:
                                    dutyTime = str(D(duty.dutyTime,""))

                                if (crew.isCabin and (crew.region == 'SKD')) or \
                                   (crew.region == 'SKS') or (not crew.isCabin):
                                    totalDutyTime += RelTime(duty.dutyTimeNoNight)
                                else:
                                    totalDutyTime += RelTime(duty.dutyTime)
                                
                                # duty pass is all time in consecutive duties without 
                                # minimum rest satisfied. Otherwise, is normal duty time.
                                if not duty.followedByMinRest: 
                                    dutyPass = ''
                                else: 
                                    dutyPass = str(D(leg.dutyPass,''))
                            
                                if dutyLoop == dutyLen:
                                    dutyTime7x24 = wop.dutyTime7x24

                                dutyTime7CalendarDays = str(D(duty.dutyTime7CalendarDays,""))
                                if len(dutyTime7CalendarDays) > 0:
                                    dutyTime7CalendarDays = ConditionalHighlight(False, D(dutyTime7CalendarDays), border=P.border(bottom=1))
                                else:
                                    dutyTime7CalendarDays = ConditionalHighlight(False, '', border=P.border(bottom=0))
                    
                        if (legLoop == legLen):
                            if otRolling and int(leg.nextLegStart) > int(otRolling[0][0]):
                                if (otRolling[0][2] == Overtime.OT_PART_7x24_FWD or otRolling[0][2] == Overtime.OT_PART_7x24_BWD):
                                    highlightRolling7x24 = True
                                    dutyTime7x24Rolling = str(otRolling[0][1])
                                elif otRolling[0][2] == Overtime.OT_PART_1x24_FWD or otRolling[0][2] == Overtime.OT_PART_1x24_BWD:
                                    highlightRolling1x24 = True
                                    overtime1x24 = str(otRolling[0][1])
                                elif otRolling[0][2] == Overtime.OT_PART_MONTH:
                                    calendarMonth = str(otRolling[0][1])
                                elif otRolling[0][2] == Overtime.OT_PART_DUTYPASS or otRolling[0][2] == Overtime.OT_PART_LATE_CHECKOUT:
                                    highlightDutyPass = True
                                else:
                                    print "no, not handling at all"
                                del otRolling[0]
                        else:
                            dutyTime7x24Rolling = ""
                        
                        #if the activity is a ground activity, it should be considered as
                        # homebase time instead of UTC time
                        if leg.is24hActivity:
                            if leg.startDateHb < startDate:
                                legActualDay = abs_to_str(startDate)
                            else:
                                legActualDay = abs_to_str(leg.startDateHb)
                                currentDayAbsTime = leg.startDateHb
                        else:
                            legActualDay = abs_to_str(leg.startDate)
                            currentDayAbsTime = leg.startDate

                        currentDay = int(legActualDay[0:2])
                        
                        #construction of the basic column of the activity/leg
                        columnBasicRow = P.Row()
                        columnBasicRow.add(P.Text(sundayMark,
                                                  font=P.Font(size=8, weight=P.BOLD)))
                        columnBasicRow.add(P.Text(legActualDay,
                                                  padding=P.padding(10,2,2,0),
                                                  align=P.RIGHT))

                        isOneDayActivity = (int(leg.endDate - leg.startDate) \
                                            / int(RelTime('24:00')) <= 1)

                        #if the activity occurs in a period, this period should be showed
                        if leg.isFlight or currentDay == lastDayMonth or isOneDayActivity:
                            columnBasicRow.add(P.Text("",align=P.LEFT))
                        else:
                            if leg.endDate > endDate:
                                finalDay = endDate - RelTime(1, 0, 0)
                            else:
                                finalDay = leg.endDate
                            columnBasicRow.add(P.Text("- " + abs_to_str(finalDay),align=P.LEFT))
                            legActualDay = abs_to_str(finalDay)
                            currentDayAbsTime = finalDay

                        columnBasicRow.add(P.Text(leg.dutyCode))
                        
                        #info codes: only meal codes, temp ill and bought days are implemented
                        code = ''
                        if not D(leg.tempIllCode) == ("ID00" or ''): 
                            code = D(leg.tempIllCode)
                        if not D(leg.boughtDayCode) == '':
                            code += ' ' + D(leg.boughtDayCode)
                        if not D(leg.mealCode) == '':
                            code += ' ' + D(leg.mealCode)
                        if not D(leg.baseBreakCode) == '':
                            code += ' ' + D(leg.baseBreakCode)
                        columnBasicRow.add(P.Text(code))
                        
                        code = ''
                        if not D(leg.privateTradeCode) == '':
                            code = D(leg.privateTradeCode)
                            code += ' ' + leg.activity
                        if code:
                            columnBasicRow.add(P.Text(code))
                        elif leg.isFlight:
                            columnBasicRow.add(P.Text(leg.activity, padding=P.padding(12,2,0,0)))
                        else:
                            columnBasicRow.add(P.Text(leg.activity))
                        
                        columnBasicRow.add(P.Text(leg.depStn))
                        columnBasicRow.add(P.Text(leg.arrStn))
                            
                        if leg.is24hActivity:
                            columnBasicRow.add(P.Text("", colspan=7))
                        else:
                            columnBasicRow.add(P.Text(leg.scheduledStart.time_of_day(), align=P.RIGHT))
                            if leg.isFlight:
                                columnBasicRow.add(P.Text(leg.startDate.time_of_day(), align=P.RIGHT))
                            else:
                                columnBasicRow.add(P.Text())
                            columnBasicRow.add(P.Text(leg.scheduledEnd.time_of_day(), align=P.RIGHT))
                            if leg.isFlight:
                                columnBasicRow.add(P.Text(leg.endDate.time_of_day(), align=P.RIGHT))
                            else:
                                columnBasicRow.add(P.Text())
                            if leg.isBreak == "True": isBreak = "B"
                            else: isBreak = ""
                            columnBasicRow.add(P.Text(isBreak))
                            if str(dutyTime) == "0:00": dutyTime = ''
                            if leg.isOnDuty:
                                columnBasicRow.add(P.Text(dutyTime, align=P.RIGHT))
                                if leg.isFlight and not leg.deadhead:
                                    columnBasicRow.add(P.Text(D(leg.time,""), align=P.RIGHT))
                                else:
                                    columnBasicRow.add(P.Text())
                            else:
                                columnBasicRow.add(P.Text())
                                columnBasicRow.add(P.Text())

                        columnBasic = P.Column(columnBasicRow)
                        
                        if leg.mdc and int(leg.mdc) > 0:
                            mdc = leg.mdc
                        else:
                            mdc = None
                        if leg.scc and int(leg.scc) > 0:
                            scc = leg.scc
                        else:
                            scc = None
                        
                        crewTemporarySKD = crew.isTemporary and crew.region == "SKD"

                        if overtime1x24 == "0:00" or crewTemporarySKD:
                            overtime1x24 = None
                        if dutyTime7x24Rolling == "0:00" or crewTemporarySKD:
                            dutyTime7x24Rolling = ""
                        if dutyPass == "0:00" or crewTemporarySKD:
                            dutyPass = None
                        if calendarWeek == "0:00" or crewTemporarySKD:
                            calendarWeek = None
                        if calendarMonth == "0:00" or crew.isTemporary:
                            calendarMonth = None
                        
                        if crew.region == "SKD":
                            if crew.isCabin:
                                if not (crew.categoryStart == "AP" and crew.categoryEnd == "AP"):
                                    columnXtra = P.Column(P.Row(ConditionalHighlight(highlightRolling1x24, D(overtime1x24)),
                                                                dutyTime7CalendarDays,
                                                                ConditionalHighlight(highlightDutyPass, D(dutyPass)),
                                                                CellText(D(mdc)),
                                                                CellText(D(scc))))
                                else:
                                    columnXtra = P.Column(P.Row(ConditionalHighlight(highlightRolling1x24, D(overtime1x24)),
                                                                dutyTime7CalendarDays,
                                                                ConditionalHighlight(highlightDutyPass, D(dutyPass)),
                                                                CellText(D(scc))))
                            elif is4ExngFCOtValid:
                                columnXtra = P.Column(P.Row(dutyTime7CalendarDays))
                            else: #mainRank == "FD"
                                columnXtra = P.Column(P.Row(ConditionalHighlight(highlightRolling7x24, D(dutyTime7x24Rolling))))
                        elif crew.region == "SKS":
                            if crew.isCabin:
                                if not (crew.categoryStart == "AP" and crew.categoryEnd == "AP"):
                                    columnXtra = P.Column(P.Row(P.Text(D(calendarWeek)),
                                                                dutyTime7CalendarDays,
                                                                ConditionalHighlight(highlightDutyPass, D(dutyPass)),
                                                                CellText(D(scc)),
                                                                CellText(D(calendarMonth))))
                                else:
                                    columnXtra = P.Column(P.Row(P.Text(D(calendarWeek)),
                                                                dutyTime7CalendarDays,
                                                                ConditionalHighlight(highlightDutyPass, D(dutyPass)),
                                                                CellText(D(scc)),
                                                                CellText(D(calendarMonth))))
                            elif is4ExngFCOtValid:
                                columnXtra = P.Column(P.Row(dutyTime7CalendarDays, P.Text(D(calendarMonth))))
                            else: #mainRank == "FD"
                                columnXtra = P.Column(P.Row(ConditionalHighlight(highlight, D(dutyTime7x24Rolling)),
                                                            P.Text(D(calendarMonth))))
                        elif crew.region == "SKN":
                            if crew.isCabin:
                                if not (crew.categoryStart == "AP" and crew.categoryEnd == "AP"):
                                    columnXtra = P.Column(P.Row(dutyTime7CalendarDays,
                                                                ConditionalHighlight(highlightDutyPass, D(dutyPass)),
                                                                CellText(D(scc)),
                                                                CellText(D(calendarMonth))))
                                else:
                                    columnXtra = P.Column(P.Row(dutyTime7CalendarDays,
                                                                ConditionalHighlight(highlightDutyPass, D(dutyPass)),
                                                                CellText(D(scc)),
                                                                CellText(D(calendarMonth))))
                            elif is4ExngFCOtValid:
                                columnXtra = P.Column(P.Row(dutyTime7CalendarDays))
                            else: #mainRank == "FD"
                                columnXtra = P.Column(P.Row(ConditionalHighlight(highlightRolling7x24, D(dutyTime7x24Rolling))))
                        else: columnXtra = P.Column()
                        if bgColor == '#ffffff':
                            bgColor = '#eeeeee'
                        else:
                            bgColor = '#ffffff'
                        self.add(P.Row(columnBasic,
                                       columnXtra,
                                       background=bgColor))
                        self.page0()
            self.page0()
            
            if crew.hasFirstLossRestHigh:
                dutiesLossRestHigh.append(crew.firstLossRestHighStr)
            if crew.hasFirstLossRestLow:
                dutiesLossRestLow.append(crew.firstLossRestLowStr)
            
            if not (crew.company == "BU" and not crew.base in ["OSL","SVG","TRD"]):
                self.create_totals(crew.isCabin, crew, startDate, endDate, totalBlockTime, fromStudio,
                                   totalDutyTime, dutiesLossRestLow, dutiesLossRestHigh, totals)

############################################################################################

    def create_totals(self, isCabin, crew, startDate, endDate, totalBlockTime, fromStudio,
                      totalDutyTime, dutiesLossRestLow, dutiesLossRestHigh, totals):
        """
        Create the last part of the report, with the sum of a few values in a monthly basis
        (duty time, block time, a/c time, block time last 6 months..)
        """
        (year, month) = startDate.split()[0:2]
        thisMonth = str(startDate)[2:9].capitalize()

        otDict = totals[0]
        lrhDict = totals[1]
        lrlDict = totals[2]
        tempHDict = totals[3]
        tempIDict = totals[4]
        tempDDict = totals[5]
        sccDict = totals[6]
        mdcSHDict = totals[7]
        mdcLHDict = totals[8]
        mdcDict = totals[9]
        otReschedDict = totals[10]
        mertidDict = totals[11]
        mertidParttimeCcDict = totals[12]
        mertidParttimeCcLongDict = totals[13]
        overtimeParttimeCcDict = totals[14]
        overtimeParttimeCcLongDict = totals[15]
        
        totalSCC = D(sccDict[crew.crewId], RelTime(0,0))
        totalMDC_SH = D(mdcSHDict[crew.crewId], RelTime(0,0))
        totalMDC_LH = D(mdcLHDict[crew.crewId], RelTime(0,0))
        totalMDC = D(mdcDict[crew.crewId], RelTime(0,0))
        totalOvertime = D(otDict[crew.crewId], RelTime(0,0))
        totalTempH = D(tempHDict[crew.crewId], RelTime(0,0))
        totalTempI = D(tempIDict[crew.crewId], RelTime(0,0))
        totalTempD = D(tempDDict[crew.crewId], RelTime(0,0))
        totalMertid = D(mertidDict[crew.crewId], RelTime(0,0))
        totalMertidParttimeCc = D(mertidParttimeCcDict[crew.crewId], RelTime(0,0))
        totalMertidParttimeCcLong = D(mertidParttimeCcLongDict[crew.crewId], RelTime(0,0))
        totalOvertimeParttimeCc = D(overtimeParttimeCcDict[crew.crewId], RelTime(0,0))
        totalOvertimeParttimeCcLong = D(overtimeParttimeCcLongDict[crew.crewId], RelTime(0,0))
        totalLRH = D(lrhDict[crew.crewId], 0)
        totalLRL = D(lrlDict[crew.crewId], 0)
        reschedOvertime = D(otReschedDict[crew.crewId], RelTime(0,0))

        region = crew.region
        categoryStart = crew.categoryStart
        categoryEnd = crew.categoryEnd
        
        # now the resume of a few values are showed

        self.add(P.Row(height=20))

        dashedLineText = "- - - - - - - - - - - - - - - - - " + \
                         "- - - - - - - - - - - - - - - - - " + \
                         "- - - - - - - - - - - - - - - - - " + \
                         "- - - - - - - - - - - - - - - - - " + \
                         "- - - - - - - - - - - - - - - -"

        columnXtra1 = P.Column(colour="#414141")
        columnXtra2 = P.Column()
        
        isSKN = region == "SKN"
        
        if not isCabin:
            columnXtra1.add(P.Text("Overtime:  ", colour="#414141"))
            columnXtra2.add(P.Text(self.toStr(totalOvertime), align=P.RIGHT))
        else:
            dashedLineText = "- - - - - - - - - - - - - - - - - " + \
                             "- - - - - - - - - - - - - - - - - "
        
        if isCabin and not region == "SKI":
            if region == "SKS":
                if totalMDC > RelTime('0:00'):
                    columnXtra1.add(P.Text("Payable MDC:   "))
                    columnXtra2.add(P.Text(self.toStr(totalMDC), align=P.RIGHT))
            else:
                if totalMDC_LH > RelTime('0:00'):
                    columnXtra1.add(P.Text("Payable MDC High:   "))
                    columnXtra2.add(P.Text(self.toStr(totalMDC_LH), align=P.RIGHT))
                if totalMDC_SH > RelTime('0:00'):
                    columnXtra1.add(P.Text("Payable MDC Low:   "))
                    columnXtra2.add(P.Text(self.toStr(totalMDC_SH), align=P.RIGHT))
            if not (categoryStart == "AP" and categoryEnd == "AP"):
                columnXtra1.add(P.Text("SCC hours:   "))
                columnXtra2.add(P.Text(self.toStr(totalSCC), align=P.RIGHT))
            if region == "SKN" and crew.isTemporary:
                columnXtra1.add(P.Text("Temporary crew days:   "))
                columnXtra2.add(P.Text(D(totalTempD), align=P.RIGHT))
            if (region == "SKD" or region == "SKS" or region == "SKN") and crew.isTemporary:
                columnXtra1.add(P.Text("Temporary crew hours:   "))
                columnXtra2.add(P.Text(self.toStr(totalTempH), align=P.RIGHT))   
            if (region == "SKD") and crew.isTemporary and totalTempI > RelTime('0:00'):
                columnXtra1.add(P.Text("Temporary crew hours ill:   "))
                columnXtra2.add(P.Text(self.toStr(totalTempI), align=P.RIGHT))   
            if (region == "SKD" or region == "SKS" or region == "SKN"):
                columnXtra1.add(P.Text("Part time cabin crew mertid:   "))
                columnXtra2.add(P.Text(self.toStr(totalMertidParttimeCc), align=P.RIGHT))   
            if (region == "SKD" or region == "SKS" or region == "SKN"):
                columnXtra1.add(P.Text("Part time cabin crew mertid for three months:   "))
                columnXtra2.add(P.Text(self.toStr(totalMertidParttimeCcLong), align=P.RIGHT))   
            if (region == "SKD" or region == "SKS" or region == "SKN"):
                columnXtra1.add(P.Text("Part time cabin crew overtime:   "))
                columnXtra2.add(P.Text(self.toStr(totalOvertimeParttimeCc), align=P.RIGHT))   
            if (region == "SKD" or region == "SKS" or region == "SKN"):
                columnXtra1.add(P.Text("Part time cabin crew overtime for three months:   "))
                columnXtra2.add(P.Text(self.toStr(totalOvertimeParttimeCcLong), align=P.RIGHT))   
            if region == "SKD" and crew.isConvertible:
                columnXtra1.add(P.Text("Convertible overtime:   "))
                columnXtra2.add(P.Text(self.toStr(totalOvertime), align=P.RIGHT))
            columnXtra1.add(P.Text("Overtime:   "))
            columnXtra2.add(P.Text(self.toStr(totalOvertime), align=P.RIGHT))

        if int(totalMertid):
            columnXtra1.add(P.Text("Mertid:   "))
            columnXtra2.add(P.Text(self.toStr(totalMertid), align=P.RIGHT))
        
        self.page0()

        columnTotals = P.Column(
            P.Row(
                P.Column(width=10), 
                P.Row(
                    P.Column(width=10),
                    P.Column(
                        P.Text("Total duty time, month (UTC):  "),
                        P.Text("Total duty time, month (local):  "),                       
                        P.Text("Total block time:  "),
                        P.Text("Total block time for last 6 months:  "),
                        P.Text("Total block time for last 12 months:  "),
                        colour="#414141"),
                    P.Column(
                        P.Text(self.toStr(crew.totalDutyTimeUTC), align=P.RIGHT),
                        P.Text(self.toStr(crew.totalDutyTimeHB), align=P.RIGHT),
                        P.Text(self.toStr(crew.blockTimeInMonthSalary), align=P.RIGHT),
                        P.Text(self.toStr(crew.blockTime6Months), align=P.RIGHT),
                        P.Text(self.toStr(crew.blockTime12Months), align=P.RIGHT)),                   
                    P.Column(width=60),
                    columnXtra1,
                    columnXtra2,
                    P.Column(width=3))))

        if True:
            pass
        elif not fromStudio:
            for row in self.block_hours_stat(crew.crewId, endDate, dashedLineText):
                columnTotals.add(row)
        else:
            columnTotals.add(P.Row(
                P.Column(),
                P.Row(dashedLineText, colour="#a4a4a4")))
            columnTotals.add(P.Row(
                P.Column(),
                P.Isolate(P.Row(P.Text("No Total block time per AC-type in the List12 draft report",
                                       padding=P.padding(10,10,8,2),
                                       font=P.Font(size=8, style=P.ITALIC))))))
            columnTotals.add(P.Row(
                P.Column(),
                P.Isolate(P.Row(P.Text("Please look at the real one in the SALARY_EXPORT folder",
                                       padding=P.padding(10,2,8,10),
                                       font=P.Font(size=8, style=P.ITALIC))))))
            
        self.add(P.Isolate(P.Column(P.Row(
            P.Text("Total Values for %s" % thisMonth,
                   padding=P.padding(10,10,8,8),
                   font=P.Font(size=11, style=P.ITALIC, weight=P.BOLD))),
            columnTotals,
            font=P.Font(size=9),
            border=P.border_frame(1, colour="#a4a4a4"),
            background="#f3f3f3")))


#######################################################################################    

    def block_hours_stat(self, crew, endDate, dashedLineText):
        rows = []
        # Collect statistics from 1986 and forward
        life_interval = Interval(0, int(endDate))
        try:
            stat = crewlog.stat_intervals(crew, [life_interval], typ="blockhrs", hi=endDate)
            # stat_intervals returns structure: {'blockhrs': {crewid: {actype: {interval: value}}}}
            crew_stat = stat['blockhrs'][crew]
        except:
            crew_stat = {}
        acFamilies = sorted(set([a for a in crew_stat]))
        if acFamilies:
            rows.append(P.Row(
                P.Column(),
                P.Row(dashedLineText, colour="#a4a4a4")))
            rows.append(P.Row(
                P.Column(),
                P.Row(P.Text(), P.Text("Total block time per AC-type:"), P.Text(""), colour="#414141")))
                
        for acFamily in acFamilies:
            try:
                blockhrs_life_ac = crew_stat[acFamily][life_interval]
            except:
                blockhrs_life_ac = 0
            rows.append(P.Row(
                P.Column(),
                P.Row(P.Column(), P.Column("- " + acFamily)),
                P.Column(P.Text(self.min2Str(blockhrs_life_ac), align=P.RIGHT)),
                P.Column()))

        total_block_hours = 0
        for a in crew_stat:
            for i in crew_stat[a]:
                total_block_hours += crew_stat[a][i]

        if total_block_hours != 0:
            rows.append(P.Row(
                P.Column(),
                P.Row(P.Column(), P.Column("TOTAL ALL AC-TYPES:")),
                P.Column(P.Text(self.min2Str(total_block_hours), align=P.RIGHT)),
                P.Column()))
            rows.append(P.Row(""))
            rows.append(P.Row(""))
        return rows

            
    def toStr(self, inRelTime):
        """Returns str from inRelTime formatted.
        """
        if (inRelTime is None) or (not isinstance(inRelTime, RelTime)):
            return "0,00"
        h, m = inRelTime.split()
        return "%d,%02d" % (h,  round(float(m*100.0/60.0)))

        
    def min2Str(self, inMin):
        """Returns str from inMin formatted.
        """
        if inMin is None:
            return ""
        h = inMin / 60
        m = round(float((inMin%60)*100.0/60.0))
        return "%d,%02d" % (h, m)

        
    def sub(self, y1, m1, m2):
        """Remove m2 months from the tuple t1 (y, m, d), return tuple (y, m).
        """
        if m1 - m2 < 1:
            y = y1 - 1
            m = m1 + 12 - m2
        else:
            y = y1
            m = m1 - m2
        return (y, m)
            
    def create_subheader(self, isCabin, is4ExngFCOtValid, region, categoryStart, categoryEnd):
        """
        Create a subheader depending on the region (SKD,SKN,SKS..), 
        rank (CA,FD) and category (AP,AH,AS..)
        """
        columnBasic = ColSAS(P.Row(P.Column(width=2),
                                   Col30(P.Text('Start', 
                                                padding=P.padding(8,2,0,0),
                                                align=P.RIGHT)),
                                   Col30('  End'),
                                   Col20('Duty'),
                                   Col20('Info'), 
                                   Col30('Flight /'),
                                   Col20('Dep'),
                                   Col20('Arr'),
                                   Col20(''),
                                   Col20(''),
                                   Col20(''),
                                   Col20(''),
                                   Col20(''),
                                   Col20('Duty'),
                                   Col20('Block')),
                             P.Row(P.Column(),
                                   Col30(P.Text('Date', 
                                                padding=P.padding(10,2,0,0),
                                                align=P.RIGHT)),
                                   Col30('  Date'),
                                   Col20('Des'),
                                   Col20('Code'),
                                   Col30('Base Act.'),
                                   Col20('Stn'),
                                   Col20('Stn'),
                                   Col20('STD'),
                                   Col20('ATD'),
                                   Col20('STA'),
                                   Col20('ATA'),
                                   Col20('BRK'),
                                   Col20('Time'),
                                   Col20('Time')))
        
        if is4ExngFCOtValid:
            otFCHeader ="7Cdays"
        else:
            otFCHeader ="7x24"
        
        if region == "SKD":
            if isCabin and not (categoryStart == "AP" and categoryEnd == "AP"):
                columnXtra = ColSAS(P.Row(Col20(''),
                                          Col20(''),
                                          Col20(''),
                                          Col20(''),
                                          Col20('')),
                                    P.Row(Col20('1x24'),
                                          Col20('7Cdays'),
                                          Col20('DutyP'),
                                          Col20('MDC'),
                                          Col20('SCC')))
            elif isCabin and categoryStart == "AP" and categoryEnd == "AP":
                columnXtra = ColSAS(P.Row(Col20(''),
                                         Col20(''),
                                         Col20(''),
                                         Col20('')),
                                    P.Row(Col20('1x24'),
                                          Col20('7Cdays'),
                                          Col20('DutyP'),
                                          Col20('SCC')))
            else: #is pilot
                columnXtra = ColSAS(P.Row(Col20('')),
                                    P.Row(Col20(otFCHeader)))
        elif region == "SKS":
            if isCabin and not (categoryStart == "AP" and categoryEnd == "AP"):
                columnXtra = ColSAS(P.Row(Col20(''),
                                          Col20(''),
                                          Col20(''),
                                          Col20(''),
                                          Col20('')),
                                    P.Row(Col20('CalW'),
                                          Col20('7Cdays'),
                                          Col20('DutyP'),
                                          Col20('SCC'),
                                          Col20('CalM')))
            elif isCabin and categoryStart == "AP" and categoryEnd == "AP":
                columnXtra = ColSAS(P.Row(Col20(''),
                                          Col20(''),
                                          Col20(''),
                                          Col20('')),
                                    P.Row(Col20('CalW'),
                                          Col20('7Cdays'),
                                          Col20('DutyP'),
                                          Col20('SCC'),
                                          Col20('CalM')))
            else: #is pilot
                columnXtra = ColSAS(P.Row(Col20(''),
                                          Col20(''),
                                          Col20('')),
                                    P.Row(Col20(otFCHeader),
                                          Col20('CalM')))
        elif region == "SKN":
            if isCabin and not (categoryStart == "AP" and categoryEnd == "AP"):
                columnXtra = ColSAS(P.Row(Col20(''),
                                          Col20(''),
                                          Col20(''),
                                          Col20(''),
                                          Col20('')),
                                    P.Row(Col20('7Cdays'),
                                          Col20('DutyP'),
                                          Col20('SCC'),
                                          Col20('CalM')))
            elif isCabin and categoryStart == "AP" and categoryEnd == "AP":
                columnXtra = ColSAS(P.Row(Col20(''),
                                          Col20(''),
                                          Col20(''),
                                          Col20('')),
                                    P.Row(Col20('7Cdays'),
                                          Col20('DutyP'),
                                          Col20('SCC'),
                                          Col20('CalM')))
            else: #mainRank == "FD"
                columnXtra = ColSAS(P.Row(Col20('')),
                                    P.Row(Col20(otFCHeader)))
        else: columnXtra = P.Column(P.Row(Col20('')))
        subheader=P.Row(columnBasic,
                        columnXtra)
        return subheader


# SimBriefDebriefExtender ------------------------------------------------{{{2
class SimBriefDebriefExtender(briefdebrief.BriefDebriefExtender):
    class Briefing:
        def __init__(self, a):
            if not (a.is_simulator and int(a.leg_checkin) > 0):
                raise briefdebrief.BriefDebriefException('No briefing')
            self.__dict__ = a.__dict__.copy()
            self.activity = 'B' + a.activity[1:]
            self.scheduledStart = a.scheduledStart - a.leg_checkin
            self.scheduledEnd = a.scheduledStart

    class Debriefing:
        def __init__(self, a):
            if not (a.is_simulator and int(a.leg_checkout) > 0):
                raise briefdebrief.BriefDebriefException('No debriefing')
            self.__dict__ = a.__dict__.copy()
            self.activity = 'D' + a.activity[1:]
            self.scheduledStart = a.scheduledEnd
            self.scheduledEnd = a.scheduledEnd + a.leg_checkout


def abs_to_str(date):
    return (str(date)[0:3] + str(date)[3:5].lower())


# runReport =============================================================={{{1
def runReport(scope='window'):
    global global_context
    context = global_context = 'default_context'

    """Run PRT Report in scope 'scope'."""
    if scope == 'plan':
        area = Cui.CuiNoArea
        context = global_context = 'sp_crew'
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

    # load previously used start and end dates
    try:
        start_date = R.param('parameters.%list12_report_start_date%').value()
        end_date = R.param('parameters.%list12_report_end_date%').value()
    except:
        start_date = None
        end_date = None
    else:
        if start_date == AbsTime('01JAN1986 0:00') or end_date == AbsTime('01JAN1986 0:00'):
            # the parameters are set to the default values - do not pass them to the form
            start_date = None
            end_date = None

    rptForm = display.reportFormDate('Employee Central List12', start_date=start_date, end_date=end_date)
    rptForm.show(True)
    if rptForm.loop() == Cfh.CfhOk:
        R.param('parameters.%list12_report_start_date%').setvalue(AbsTime(rptForm.getStartDate()))
        R.param('parameters.%list12_report_end_date%').setvalue(AbsTime(rptForm.getEndDate()))
        args = 'startDate=%s endDate=%s context=%s scheduled=no' % (
                rptForm.getStartDate(), rptForm.getEndDate(), context)
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope,
            '../lib/python/report_sources/include/ECList12.py', 0, args)
    

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof