#

#
"""
BCS Report
"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as r
from report_sources.include.SASReport import SASReport
import report_sources.include.LegalityInfo as LegalityInfo
from AbsDate import AbsDate

class BCS(SASReport):
    def create(self, scope, context='default_context', showPlanData=True, showFailures=True):
        # scope is one of trip_general, trip_object, crew_object, and assignment_object
        
        # Basic setup
        SASReport.create(self, 'BCS', orientation=LANDSCAPE, showPlanData=showPlanData, usePlanningPeriod=True)

        iteratorString = "iterators."
        tripGeneral = False
        tripObject = False
        crewObject = False
        assignmentObject = False
        if (scope == "trip_general"):
            tripGeneral = True
            iteratorString += "compressed_"
        elif (scope == "trip_object"):
            tripObject = True
        elif (scope == "crew_object"):
            crewObject = True
        elif (scope == "assignment_object"):
            assignmentObject = True
        else:
            raise Exception("Called with illegal scope")

        # This report should always use UTC time
        # Therefore make sure that the time mode parameter is set accordingly
        # Also save the previous value so that it can be reset
        tm_old, = r.eval('crg_trip.time_mode')
        tm_utc, = r.eval('crg_basic.timemode_UTC')
        r.param('crg_trip.time_mode').setvalue(tm_utc)
        
        # Getting plandata, for displaying operating date
        planData, = r.eval('default_context',
                           r.foreach('iterators.chain_set',
                                     'is_dated_mode',
                                     'crg_basic.%is_daily_plan%',
                                     'crg_trip.%show_violated_rules%'))
        (index, datedMode, dailyPlan, showFailuresParam)  = planData[0]

        showFailures = showFailures and showFailuresParam

        # For crew object report
        if crewObject:
            crewData, = r.eval('default_context',
                               r.foreach('iterators.chain_set',
                                         'report_common.%crew_string%',
                                         ))
            (ix,crewString) = crewData[0]
            self.add(Row(Text(crewString, font=Font(size=10, weight=BOLD))))
            self.add(Row(' '))

        T_VALUES = ['trip.%name%',
                    'trip.%homebase%',
                    'trip.%days%',
                    'crg_crew_pos.%trip_assigned_vector%(crg_crew_pos.Cockpit, crg_crew_pos.SingleTrip)',
                    'crg_crew_pos.%trip_assigned_vector%(crg_crew_pos.Cabin, crg_crew_pos.SingleTrip)',
                    'crg_date.%print_reltime%(report_common.%trip_duty_time%)',
                    'crg_date.%print_reltime%(report_common.%trip_duty_time_no_night_upg%)',
                    'crg_date.%print_reltime%(trip.%block_time%)',
                    'crg_date.%print_reltime%(trip.%time%)',
                    'crg_trip.%frequency%',
                    'crg_trip.%only_one_trip%',
                    'crg_date.%print_weekday%(crg_trip.%trip_start%)',
                    'crg_date.%print_date%(crg_trip.%trip_start%)',
                    'crg_trip.%first_trip_start%',
                    'crg_trip.%last_trip_start%',
                    'crg_trip.%count_trips%',
                    'crg_trip.%unique_weekday%',
                    'report_common.%num_req_freedays_BCS%',
                    ]
        
        T_DETAILS = ['crg_date.%print_date%(crg_trip.%first_trip_start%)',
                     'crg_date.%print_date%(crg_trip.%last_trip_start%)',
                     'crg_trip.%frequency%',
                     'crg_trip.%count_trips%',]
        
        D_VALUES = ['format_time(crg_trip.%duty_start%, "%a %02d%02b%02y")',
                    'crg_date.%print_time%(crg_trip.%duty_start%)',
                    'crg_date.%print_time%(crg_trip.%duty_end%)',
                    'crg_date.%print_reltime%(report_common.%duty_duty_time%)',
                    'crg_date.%print_reltime%(report_common.%duty_duty_time_no_night_upg%)',
                    'crg_date.%print_reltime%(duty.%block_time%)',
                    'crg_date.%print_reltime%(duty.%rest_time%)',
                    'crg_basic.%duty_is_last_in_trip%',
                    ]
        
        L_VALUES = ['crg_trip.%leg_day_number%',
                    'crg_trip.%weekday_info%',
                    'crg_trip.%weekday%',
                    'crg_basic.%dh_mark%',
                    #'leg.%flight_carrier%',
                    #'crg_basic.%flight_nr_string%',
                    'leg.%flight_name%',
                    'crg_basic.%flight_suffix%',
                    'leg.%ac_type%',
                    'leg.%is_ac_change%',
                    'leg.%start_station%',
                    'leg.%end_station%',
                    'leg.%block_time%',
                    'crg_date.%print_reltime%(leg.%block_time%)',
                    'crg_date.%print_time%(crg_trip.%leg_start%)',
                    'crg_date.%print_time%(crg_trip.%leg_end%)',
                    'crg_date.%print_reltime%(leg.%ground_time%)',
                    'crg_basic.%leg_is_last_in_duty%',
                    'report_meal.%meal_code%',
                    'duty_code.%leg_code%',
                    ]

        # Building rave expression and collecting data
        leg_expr = r.foreach(iteratorString + 'leg_set',*L_VALUES)
                
        D_VALUES.append(leg_expr)
        duty_expr = r.foreach(iteratorString + 'duty_set',*D_VALUES)
        
        tripDetails_expr = r.foreach(
            r.iter('actual_chain_period',
                   ('is_dated_mode','not crg_trip.%above_only_one_trip%')),
            *T_DETAILS)
        T_VALUES.append(tripDetails_expr)
        T_VALUES.append(duty_expr)
        if showFailures:
            legality_expr = r.foreach('iterators.trip_set','trip.%start_day%',r.foreach(r.rulefailure()))
        else:
            legality_expr = 'void_string'
        T_VALUES.append(legality_expr)
        trip_expr = r.foreach(r.iter(iteratorString + 'trip_set', where='trip.%is_on_duty%'),*T_VALUES)
        print iteratorString + 'trip_set'
        trips, = r.eval(context, trip_expr)

        # Reset time mode so other reports are not disturbed
        r.param('crg_trip.time_mode').setvalue(tm_old)

        noOfTrips = len(trips)
        # Looping through trip sets
        for (ix,tripName,tripHomebase,tripDays,flightCrew,cabinCrew,tripDutyTime,tripDutyTimeNoNU,
             tripBlockTime,tripTime,tripFrequency,onlyOneTrip,tripStartWeekday,
             tripStartDate,firstTripStart,lastTripStart,tripCount,uniqueWeekday,
             reqFreedays,tripDetails,duties,failedTrips) in trips:
        
            oneTripBox = Column(border=None, width=(self.pageWidth-5))

            # Trip header
            tripBoxHeader = self.getTableHeader((), vertical=False)
                       
            oneTripBox.add(tripBoxHeader)

            dutiesBox = Row(border=None)
            legFirstInDuty = True
            dutyNo = 0

            # For each duty
            for (ix,dutyStartDate,dutyStart,dutyEnd,dutyTime,dutyTimeNoNU,dutyBlockTime,dutyRestTime,dutyLastInTrip,legs) in duties:
                if dutyLastInTrip:
                    dutyRestTime = '-'

                dutyNo +=1
                if datedMode:
                    tripBoxHeader.add(Text('Duty %s, %s' %(dutyNo,dutyStartDate[:-2]), colspan=2))
                else:
                    tripBoxHeader.add(Text('Duty %s, %s' %(dutyNo,dutyStartDate[:3]), colspan=2))
              
                headerColumn = Column()
                dataColumn = Column()
                legBorder = border(top=0)
                
                # For each leg in duty
                for (ix,legDay,legWeekdayInfo,legWeekday,legDH,legName,legFlightSuffix,
                     legACType,legACChange,legStartStation,legEndStation,
                     legBlockTime,legBlockTimeFmt,legDeparture,legArrival,
                     legGroundTime,legLastInDuty,legMealCode,dutyCode) in legs:

                    if not legBlockTime:
                        legBlockTimeFmt = ' - '
                    if legACChange:
                        legACType += '*'
                    if legLastInDuty:
                        legGroundTime = ''

                    if (not dutyCode is None) and dutyCode != "":
                        dutyCode += " "

                    if uniqueWeekday:
                        legWeekdayInfo = legWeekday

                    legHeaders = self.getTableHeader(('Flight','AC type',''),vertical=True)    
                    headerColumn.add(legHeaders)
                    
                    dataColumn.add(Text('%s%s%s' % (dutyCode, legName, legFlightSuffix)))
                    dataColumn.add(Text(legACType))
                    #Add space to separate flights in duty
                    dataColumn.add(Text(''))

                dutySummaryHeaders = self.getTableHeader(('Check-in','Check-out','Duty','Rest'),
                                                         vertical=True)
                headerColumn.add(dutySummaryHeaders)
                
                dataColumn.add(Text(dutyStart))    
                dataColumn.add(Text(dutyEnd)) 
                dataColumn.add(Text('%s (%s)' % (dutyTime, dutyTimeNoNU)))
                dataColumn.add(Text(dutyRestTime))
                

                dutySummary = Column(Row(headerColumn,dataColumn))

                dutiesBox.add(Column(dutySummary))

            # Trip summary
            tripBoxHeader.add(Text('Trip Summary', colspan=2, border=border(left=1, colour='#ffffff')))
            
            tripSummaryHeaders = self.getTableHeader(
                ('Flight Crew','Cabin Crew','Trip length','Required freedays'),
                vertical=True)

            tripSumData = (
                flightCrew,
                cabinCrew,
                tripDays,
                reqFreedays
                )
            tripSummaryData = Column(border=None)
            for item in tripSumData:
                tripSummaryData.add(item)            
            
            tripSummaryBox = Column(
                Row(
                tripSummaryHeaders,
                tripSummaryData)
                )

            oneTripBox.add(Row(dutiesBox, tripSummaryBox,border=None))

            self.add(oneTripBox)
            if noOfTrips > 1:
                self.add(Row(' '))
                self.add(Row(' '))
                self.add(Row(' '))
            self.page0()

# End of file
