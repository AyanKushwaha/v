#

#
"""
Trip Info Report
"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as r
from report_sources.include.SASReport import SASReport
import report_sources.include.LegalityInfo as LegalityInfo
from AbsDate import AbsDate

class TripInfo(SASReport):
    def create(self, scope, context='default_context', showPlanData=True, showFailures=True):
        # scope is one of trip_general, trip_object, crew_object, and assignment_object

        # Basic setup
        SASReport.create(self, 'Trip Info', orientation=PORTRAIT, showPlanData=showPlanData,
                         usePlanningPeriod=True, margins=padding(10,15,10,15))

        time_mode = str(r.eval('crg_trip.%time_mode%'))
        time_mode = time_mode[time_mode.find("'")+1:time_mode.rfind("'")]
        if time_mode == 'crg_basic.timemode_lt':
            time_mode = 'Local'
            time_zone_string = '(trip.%start_lt%-trip.%start_utc%)/1:00'
        elif time_mode == 'crg_basic.timemode_utc':
            time_mode = 'UTC'
            time_zone_string = '(trip.%start_utc%-trip.%start_utc%)/1:00'
        elif time_mode == 'crg_basic.timemode_hb':
            time_mode = 'Home base time'
            time_zone_string = '(trip.%start_hb%-trip.%start_utc%)/1:00'
        common_head_time = ''
        if time_mode <> 'UTC':
            common_head_time = "; All times for Start/End are in %s" % time_mode
        common_head = "(*) AC change; (**) No duty night upgrade" + common_head_time;
        items = SASReport.getTableHeader(self,[common_head], vertical=True, widths=None, aligns=None)
        SASReport.getHeader(self).add(items)
        SASReport.getHeader(self).add(Text(""))
        SASReport.getHeader(self).set(border=border(bottom=0))

        iteratorString = "iterators."
        self.tripGeneral = False
        self.tripObject = False
        self.crewObject = False
        self.assignmentObject = False
        if (scope == "trip_general"):
            self.tripGeneral = True
            iteratorString += "compressed_"
        elif (scope == "trip_object"):
            self.tripObject = True
        elif (scope == "crew_object"):
            self.crewObject = True
        elif (scope == "assignment_object"):
            self.assignmentObject = True
        else:
            raise Exception("Called with illegal scope")

        # Getting plandata, for displaying operating date
        planData, = r.eval('default_context',
                           r.foreach('iterators.chain_set',
                                     'is_dated_mode',
                                     'crg_basic.%is_daily_plan%',
                                     'crg_trip.%show_violated_rules%'))

        if len(planData) == 0:
            print "No data"
            return

        (index, self.datedMode, self.dailyPlan, showFailuresParam)  = planData[0]

        self.showFailures = showFailures and showFailuresParam

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
                    'crg_date.%print_weekday%(crg_trip.%trip_end%)',
                    'crg_date.%print_date%(crg_trip.%trip_end%)',
                    'crg_trip.%first_trip_start%',
                    'crg_trip.%last_trip_start%',
                    'crg_trip.%count_trips%',
                    'crg_trip.%unique_weekday%',
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
                    'report_meal.%consumption_code%',
                    'report_meal.%consumption_corr_is_effective%',
                    'report_meal.%consumption_corr_type%',
                    'report_meal.%load_flight_nr%',
                    'report_meal.%correction_flt_and_stn_prev_in_rotation%',
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
        if self.showFailures:
            legality_expr = r.foreach('iterators.trip_set','trip.%start_day%',time_zone_string,
                                      r.foreach(r.rulefailure()))
        else:
            legality_expr = 'void_string'
        T_VALUES.append(legality_expr)
        if self.assignmentObject:
            crew_info_expr = r.foreach('iterators.trip_set',
                                       'crew.%rank_trip_start%',
                                       'crew.%employee_number%',
                                       'crew.%login_name_at_date%(trip.%start_utc%)')
        else:
            crew_info_expr = 'void_string'
        T_VALUES.append(crew_info_expr)
        trip_expr = r.foreach(r.iter(iteratorString + 'trip_set', where='trip.%is_on_duty%'),*T_VALUES)
        print iteratorString + 'trip_set'

        # For crew object report, iterate this through all crew
        if self.crewObject:
            roster_expr = r.foreach(
                r.iter('iterators.chain_set'),
                'report_common.%crew_string%',
                trip_expr)
            rosters, = r.eval(context, roster_expr)
            for roster in rosters:
                (ix, crewString, trips) = roster
                self.add(Row(Text(crewString, font=Font(size=10, weight=BOLD))))
                self.add(Row(' '))
                self.outputTrips(trips)
                self.newpage()
        else:
            trips, = r.eval(context, trip_expr)
            self.outputTrips(trips)

    def outputTrips(self, trips):
        noOfTrips = len(trips)
        # Looping through trip sets
        for (ix,tripName,tripHomebase,tripDays,flightCrew,cabinCrew,tripDutyTime,tripDutyTimeNoNU,
             tripBlockTime,tripTime,tripFrequency,onlyOneTrip,tripStartWeekday,
             tripStartDate,tripEndWeekday,tripEndDate,firstTripStart,lastTripStart,tripCount,
             uniqueWeekday,tripDetails,duties,failedTrips, crewInfo) in trips:

            oneTripBox = Column(border=None, width=(self.pageWidth-5))

            # Trip header
            tripHeader = Row(font=self.HEADERFONT)
            tripHeader.set(font=Font(style=ITALIC))
            if self.tripObject:
                tripHeader.add(Text('%s %s' % (tripStartWeekday, tripStartDate)))
            else:
                if self.dailyPlan:
                    assert self.dailyPlan == True
                    tripHeader.add(Text('Daily'))
                elif not self.datedMode:
                    assert self.datedMode == False
                    tripHeader.add(Text('%s' % tripFrequency))
                elif onlyOneTrip:
                    assert onlyOneTrip == True
                    tripHeader.add(Text('Operates %s %s - %s %s' % (tripStartWeekday, tripStartDate, tripEndWeekday, tripEndDate)))
                else:
                    tripDetailsColumn = Column()
                    for (ix,tdFirstStart,tdLastSTart,tdFreq,tdCount) in tripDetails:
                        s = ''
                        if tdCount > 1:
                            s = 's'
                        tripDetailsColumn.add(Text('%s-%s %s (%s trip%s)' % (tdFirstStart,tdLastSTart,tdFreq,tdCount,s)))
                    tripHeader.add(tripDetailsColumn)
            oneTripBox.add(Isolate(tripHeader))

            tripBoxHeader = self.getTableHeader(
                ('Day','Flight','Sector','Start','End','Meal','Cons','Preload','Block','AC','Cnx',' '),
                vertical=False)
            tripBoxHeader.add(Text('Duty Summary', colspan=2))
            tripBoxHeader.add(Text(' '))
            tripBoxHeader.add(Text('Trip Summary', colspan=2, border=border(left=1, colour='#ffffff')))

            oneTripBox.add(tripBoxHeader)

            dutiesList = []
            dutyFirstInTrip = True

            for (ix,dutyStartDate,dutyStart,dutyEnd,dutyTime,dutyTimeNoNU,dutyBlockTime,dutyRestTime,dutyLastInTrip,
             legs) in duties:
                if dutyLastInTrip:
                    dutyRestTime = '-'

                legsBox = Column()
                if onlyOneTrip:
                    if type(dutyStartDate) == type(None):
                        dutyStartDate = 'UnKnown'
                    dutyDateText = "("+dutyStartDate+")"
                else:
                    dutyDateText = ' '
                legsBox.add(
                    Row(Text(dutyDateText, colspan=2),Text('Duty start'),Text(dutyStart))
                    )

                for (ix,legDay,legWeekdayInfo,legWeekday,legDH,legName,legFlightSuffix,
                     legACType,legACChange,legStartStation,legEndStation,
                     legBlockTime,legBlockTimeFmt,legDeparture,legArrival,
                     legGroundTime,legLastInDuty,
                     legMealCode,legConsumptionCode,legHasConsCorr,legConsCorrCode,mealLoadFlight,legLoadCorrection,dutyCode) in legs:

                    if not legBlockTime:
                        legBlockTimeFmt = ' - '
                    if legACChange:
                        legACType += '*'
                    if legLastInDuty:
                        legGroundTime = ''

                    if (not dutyCode is None) and dutyCode != "":
                        dutyCode += " "
                    else:
                        dutyCode = ""

                    if uniqueWeekday:
                        legWeekdayInfo = legWeekday
                    if legMealCode is None:
                        legMealCode = ""
                    if legConsumptionCode is None:
                        legConsumptionCode = ""
                    if legHasConsCorr:
                        legConsumptionCode = "%s Corr%s"%(legConsumptionCode, legConsCorrCode)
                    elif legConsCorrCode == 'N':
                        legConsumptionCode = 'CorrN'

                    if type(mealLoadFlight) != str:
                        mealLoadFlight = ""
                    else:
                        #Clean SK+leading spaces and zeros
                        mealLoadFlight = mealLoadFlight[2:].strip(" ").lstrip("0")
                        if legConsumptionCode == "" or mealLoadFlight == legName.lstrip(" 0") or legConsCorrCode == 'N':
                            mealLoadFlight = ""
                        elif legLoadCorrection:
                            mealLoadFlight += 'Corr'

                    legsBox.add(Row(
                        Text('%s %s' % (legDay, legWeekdayInfo)),
                        Text('%s%s%s' % (dutyCode, legName, legFlightSuffix)),
                        Text('%s-%s' % (legStartStation, legEndStation)),
                        Text(legDeparture),
                        Text(legArrival),
                        Text(legMealCode),
                        Text(legConsumptionCode),
                        Text(mealLoadFlight),
                        Text(legBlockTimeFmt),
                        Text(legACType),
                        Text(legGroundTime)))

                legsBox.add(
                    Row(Text(' ', colspan=2),Text('Duty end'),Text(' '),Text(dutyEnd))
                    )

                dutySummaryHeaders = self.getTableHeader(
                    ('Duty','Block','Rest'),
                    vertical=True)

                dutySummaryData = Column(
                    Text('%s (%s**)' % (dutyTime, dutyTimeNoNU)),
                    Text(dutyBlockTime),
                    Text(dutyRestTime),
                    )

                dutySummary = Column(
                    Row(
                    dutySummaryHeaders,
                    dutySummaryData,
                    ' ')
                    )

                dutyBorder = border(top=0)
                if dutyFirstInTrip:
                    dutyFirstInTrip = False
                    dutyBorder = None

                dutiesList.append(Row(legsBox, ' ', dutySummary,border=dutyBorder))

            # Trip summary
            tripSumData = []
            if self.assignmentObject:
                tripSummaryHeaders = self.getTableHeader(
                                     ('Crew Rank','Emp No','Crew','Trip Id','Home base','Duty time','Block length','Trip length','TAFB'),
                                     vertical=True)
                ix, crewRank, crewId, crewName = crewInfo[0]
                tripSumData = [crewRank, crewId, crewName]
            else:
                tripSummaryHeaders = self.getTableHeader(
                                     ('Flight Crew','Cabin Crew','Trip Id','Home base','Duty time','Block length','Trip length','TAFB'),
                                     vertical=True)

            (fc, fp, fr, fi) = flightCrew.split('/')
            (ap, _as, ah, ai) = cabinCrew.split('/')
            tripSumList = [
                tripName,
                tripHomebase,
                '%s (%s)' % (tripDutyTime, tripDutyTimeNoNU),
                tripBlockTime,
                tripDays,
                tripTime,
                ]

            if not self.assignmentObject:
                def fmt_flight_crew_complement():
                    if fc != "0": yield "FC:" + fc
                    if fp != "0": yield "FP:" + fp
                    if fr != "0": yield "FR:" + fr
                    if fi != "0": yield "FI:" + fi
                def fmt_cabin_crew_complement():
                    if ap != "0": yield "AP:" + ap
                    if _as != "0": yield "AS:" + _as
                    if ah != "0": yield "AH:" + ah
                    if ai != "0": yield "AI:" + ai
                tripSumList = [', '.join(fmt_flight_crew_complement()), ', '.join(fmt_cabin_crew_complement())] + tripSumList
            tripSumData.extend(tripSumList)
            tripSumData = tuple(tripSumData)
            tripSummaryData = Column(border=None)
            for item in tripSumData:
                tripSummaryData.add(item)

            tripSummaryBox = Column(
                Row(
                tripSummaryHeaders,
                tripSummaryData)
                )

            dutiesBoxes = []
            dutiesBox = None
            idx = 0
            for duty in dutiesList:
                if not idx % 8:
                    dutiesBox = Column(border=None)
                    dutiesBoxes.append(dutiesBox)
                idx += 1
                dutiesBox.add(duty)
            for box in dutiesBoxes:
                if tripSummaryBox:
                    rows = (box, tripSummaryBox)
                else:
                    rows = (box,)
                oneTripBox.add(Row(*rows))
                oneTripBox.page()
                tripSummaryBox = None

            # LegalityBox
            if self.showFailures:
                failBox = Column(border=None, width=self.pageWidth)
                failHeaderRow = self.getTableHeader(
                    LegalityInfo.FAILHEADER,
                    vertical=False)
                failBox.add(failHeaderRow)

                noOfFailures = 0
                noOfFailedTrips = len(failedTrips)
                for (ix,failedTripStart,timeZoneDiff,ruleFailures) in failedTrips:
                    oneFailTrip = Column(border=border(bottom=0))
                    if (noOfFailedTrips > 1):
                        failedTripStart = AbsDate(failedTripStart)
                        oneFailTrip.add(Row(Text("(Trip starting at %s)" %failedTripStart, font=Font(weight=BOLD))))
                    for failure, in ruleFailures:
                        noOfFailures += 1
                        oneFailTrip.add(
                            LegalityInfo.failRow(failure, timezone=timeZoneDiff)
                            )
                    failBox.add(Row(oneFailTrip))
                if (noOfFailures > 0):
                    oneTripBox.add(Row(Isolate(failBox)))
                else:
                    oneTripBox.set(border=border(bottom=0))

            self.add(oneTripBox)

            if noOfTrips > 1:
                self.add(Row(' '))
                self.add(Row(' '))
                self.add(Row(' '))
            self.page0()

# End of file
