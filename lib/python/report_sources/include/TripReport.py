#

#
"""
Trip Report
"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as r
from AbsDate import AbsDate
from RelTime import RelTime
from AbsTime import AbsTime
import Dates
import  time
import math

from SASReport import SASReport

TRIP_NAME = 0
TRIP_HOMEBASE = 1
TRIP_DAYS = 2
TRIP_FC = 3
TRIP_CC = 4
TRIP_DUTY_TIME = 5
TRIP_BLOCK_TIME = 6
TRIP_TIME = 7
TRIP_FREQUENCY = 8
TRIP_ONLY_ONE = 9
TRIP_START_WEEKDAY = 10
TRIP_START_DATE = 11
TRIP_FIRST_START = 12
TRIP_LAST_START = 13
TRIP_COUNT = 14
TRIP_VALUES = ('trip.%name%',
               'trip.%homebase%',
               'trip.%days%',
               'crg_crew_pos.%trip_assigned_vector%(\
               crg_crew_pos.Cockpit, crg_crew_pos.SingleTrip)',
               'crg_crew_pos.%trip_assigned_vector%(\
               crg_crew_pos.Cabin, crg_crew_pos.SingleTrip)',
               'report_common.%trip_duty_time%',
               'trip.%block_time%',
               'trip.%time%',
               'crg_trip.%frequency%',
               'crg_trip.%only_one_trip%',
               'crg_date.%print_weekday%(crg_trip.%trip_start%)',
               'crg_date.%print_date%(crg_trip.%trip_start%)',
               'crg_trip.%first_trip_start%',
               'crg_trip.%last_trip_start%',
               'crg_trip.%count_trips%',)

TRIP_DETAILS_FIRST_START = 0
TRIP_DETAILS_LAST_START = 1
TRIP_DETAILS_FREQUENCY = 2
TRIP_DETAILS_COUNT = 3
TRIP_DETAILS = ('crg_date.%print_date%(crg_trip.%first_trip_start%)',
                'crg_date.%print_date%(crg_trip.%last_trip_start%)',
                'crg_trip.%frequency%',
                'crg_trip.%count_trips%',)

DUTY_START = 0
DUTY_END = 1
DUTY_TIME = 2
DUTY_BLOCK_TIME = 3
DUTY_REST_TIME = 4
DUTY_LAST_IN_TRIP = 5
DUTY_VALUES = ('crg_date.%print_time%(crg_trip.%duty_start%)',
               'crg_date.%print_time%(crg_trip.%duty_end%)',
               'crg_date.%print_reltime%(duty.%time%)',
               'crg_date.%print_reltime%(duty.%block_time%)',
               'crg_date.%print_reltime%(duty.%rest_time%)',
               'crg_basic.%duty_is_last_in_trip%',)

LEG_DAY = 0
LEG_WEEKDAY = 1
LEG_DH = 2
LEG_FLIGHT_NR = 3
LEG_FLIGHT_SUFFIX = 4
LEG_AC_TYPE = 5
LEG_AC_CHANGE = 6
LEG_START_STATION = 7
LEG_END_STATION = 8
LEG_BLOCK_TIME = 9
LEG_BLOCK_TIME_FMT = 10
LEG_DEPARTURE = 11
LEG_ARRIVAL = 12
LEG_GROUND_TIME = 13
LEG_POINTS = 14
LEG_LAST_IN_DUTY = 15
LEG_MEAL_CODE = 16
LEG_VALUES = ('crg_trip.%leg_day_number%',
              'crg_trip.%weekday_info%',
              'crg_basic.%dh_mark%',
              'crg_basic.%flight_nr_string%',
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
              'points.%leg_points_block_on_acc%',
              'crg_basic.%leg_is_last_in_duty%',
              'report_meal.%consumption_code%')



class TripReport(SASReport):

    def create(self, context):

        SASReport.create(self, 'Trip Report', True, 790, LANDSCAPE, usePlanningPeriod=True)

        fontSizeHead = 9
        fontSizeBody = 8
        self.set(font=Font(size=fontSizeBody))

        planData, = r.eval('default_context',
                           r.foreach('iterators.chain_set',
                                     'is_dated_mode',
                                     'crg_basic.%is_daily_plan%',))
        (index, datedMode, dailyPlan)  = planData[0]

        tripDetailsItr = r.iter('actual_chain_period',
                                ('is_dated_mode',
                                 'not crg_trip.%above_only_one_trip%'))
        
        tripSequence = r.foreach(
            'iterators.compressed_trip_set',
            TRIP_VALUES[0],
            TRIP_VALUES[1],
            TRIP_VALUES[2],
            TRIP_VALUES[3],
            TRIP_VALUES[4],
            TRIP_VALUES[5],
            TRIP_VALUES[6],
            TRIP_VALUES[7],
            TRIP_VALUES[8],
            TRIP_VALUES[9],
            TRIP_VALUES[10],
            TRIP_VALUES[11],
            TRIP_VALUES[12],
            TRIP_VALUES[13],
            TRIP_VALUES[14],
            r.foreach(tripDetailsItr,
                      *TRIP_DETAILS),
            r.foreach('iterators.compressed_duty_set',
                      DUTY_VALUES[0],
                      DUTY_VALUES[1],
                      DUTY_VALUES[2],
                      DUTY_VALUES[3],
                      DUTY_VALUES[4],
                      DUTY_VALUES[5],
                      r.foreach('iterators.compressed_leg_set',
                                *LEG_VALUES)))
        
        trips, = r.eval(context, tripSequence)

        for trip in trips:
            duties = trip[-1]
            tripDetails = trip[-2]
            trip = trip[1:-2]

            tripName = trip[TRIP_NAME]
            tripHomebase = trip[TRIP_HOMEBASE]
            tripDays = trip[TRIP_DAYS]
            flightCrew = trip[TRIP_FC]
            cabinCrew = trip[TRIP_CC]
            tripDutyTime = trip[TRIP_DUTY_TIME]
            tripBlockTime = trip[TRIP_BLOCK_TIME]
            tripTime = trip[TRIP_TIME]
            tripFrequency = trip[TRIP_FREQUENCY]
            onlyOneTrip = trip[TRIP_ONLY_ONE]
            tripStartWeekday = trip[TRIP_START_WEEKDAY]
            tripStartDate = trip[TRIP_START_DATE]
            firstTripStart = trip[TRIP_FIRST_START]
            lastTripStart = trip[TRIP_LAST_START]
            tripCount = trip[TRIP_COUNT]

            tripBox = Column()

            if dailyPlan:
                assert dailyPlan == True
                tripHeader = Row(Text('Daily',
                                      align=LEFT,
                                      font=Font(size=fontSizeHead, weight=BOLD),
                                      colspan=6))
                tripBox.add(tripHeader)
            elif not datedMode:
                assert datedMode == False
                tripHeader = Row(Text('%s' % tripFrequency,
                                      align=LEFT,
                                      font=Font(size=fontSizeHead, weight=BOLD),
                                      colspan=6))
                tripBox.add(tripHeader)
            elif onlyOneTrip:
                assert onlyOneTrip == True
                tripHeader = Row(Text('Operates: Only on %s %s' \
                                      % (tripStartWeekday, tripStartDate),
                                      align=LEFT,
                                      font=Font(size=fontSizeHead, weight=BOLD),
                                      colspan=6))
                tripBox.add(tripHeader)
            else:
                for tripDetail in tripDetails:
                    tripDetail = tripDetail[1:]
                    if tripDetail[TRIP_DETAILS_COUNT] > 1:
                        s = 's'
                    else:
                        s = ''
                    tripHeader = Row(
                        Text('%s-%s %s (%s trip%s)' \
                             % (tripDetail[TRIP_DETAILS_FIRST_START],
                                tripDetail[TRIP_DETAILS_LAST_START],
                                tripDetail[TRIP_DETAILS_FREQUENCY],
                                tripDetail[TRIP_DETAILS_COUNT],
                                s),
                             align=LEFT,
                             font=Font(size=fontSizeHead, weight=BOLD),
                             colspan=6))
                    tripBox.add(tripHeader)

            (fc, fp, fr, fi) = flightCrew.split('/')
            (ap, _as, ah, ai) = cabinCrew.split('/')
           
            tripSummary = Column(
                Row(Text('Trip Summary', colspan=2),
                    background='#cdcdcd',
                    border=border(bottom=1, top=1),
                    font=Font(size=fontSizeHead, style=ITALIC)),
                Row(Text('Flight Crew'),
                    Text('FC:%s, FP:%s, FR:%s, FI:%s' % (fc, fp, fr, fi))),
                Row(Text('Cabin Crew'),
                    Text('AP:%s, AS:%s, AH:%s, AI:%s' % (ap, _as, ah, ai))),
                Row(Text('Trip Id'),
                    Text(tripName)),
                Row(Text('Home base'),
                    Text(tripHomebase)),
                Row(Text('Duty time'),
                    Text(tripDutyTime)),
                Row(Text('Block length'),
                    Text(tripBlockTime)),
                Row(Text('Trip length'),
                    Text(tripDays)),
                Row(Text('TAFB'),
                    Text(tripTime)))

            legBoxHeader = None
            dutyBoxHeader = None
            legDutyBox = Column()
            firstDutyRow = True

            for duty in duties:
                legs = duty[-1]
                duty = duty[1:-1]
                
                dutyStart = duty[DUTY_START]
                dutyEnd = duty[DUTY_END]
                dutyTime = duty[DUTY_TIME]
                dutyBlockTime = duty[DUTY_BLOCK_TIME]
                dutyRestTime = duty[DUTY_REST_TIME]
                dutyLastInTrip = duty[DUTY_LAST_IN_TRIP]

                if dutyLastInTrip:
                    dutyRestTime = '-'
            
                dutyLegIndex = 1
                legBox = Column()
                dutyBox = Column()

                if not dutyBoxHeader:
                    dutyBoxHeader = Row(
                        Text('Duty Summary', colspan=2),
                        font=Font(size=fontSizeHead, style=ITALIC),
                        background='#cdcdcd',
                        border=border(bottom=1, top=1))
                    dutyBox.add(dutyBoxHeader)

                if not firstDutyRow:
                    legBox.add(Row(Text(colspan=10, border=border(bottom=1))))
                    dutyBox.add(Row(Text(colspan=2, border=border(bottom=1))))
                else:
                    firstDutyRow = False

                for leg in legs:
                    leg = leg[1:]

                    legDay = leg[LEG_DAY]
                    legWeekday = leg[LEG_WEEKDAY]
                    legDH = leg[LEG_DH]
                    legFlightNr = leg[LEG_FLIGHT_NR]
                    legFlightSuffix =leg[LEG_FLIGHT_SUFFIX]
                    legACType = leg[LEG_AC_TYPE]
                    legACChange = leg[LEG_AC_CHANGE]
                    legStartStation = leg[LEG_START_STATION]
                    legEndStation = leg[LEG_END_STATION]
                    legBlockTime = leg[LEG_BLOCK_TIME]
                    legBlockTimeFmt = leg[LEG_BLOCK_TIME_FMT]
                    legDeparture = leg[LEG_DEPARTURE]
                    legArrival = leg[LEG_ARRIVAL]
                    legGroundTime = leg[LEG_GROUND_TIME]
                    legPoints = leg[LEG_POINTS]
                    legLastInDuty = leg[LEG_LAST_IN_DUTY]
                    legMealCode = leg[LEG_MEAL_CODE]

                    if not legBoxHeader:
                        legBoxHeader = Row(
                            Text('Day'),
                            Text('Flight'),
                            Text('Sector'),
                            Text('Start'),
                            Text('End'),
                            Text('Meal'),
                            Text('Block'),
                            Text('Eqp'),
                            Text('Cnx'),
                            Text('Points'),
                            font=Font(size=fontSizeHead, style=ITALIC),
                            background='#cdcdcd',
                            border=border(bottom=1, top=1))
                        legBox.add(legBoxHeader)
                        
                    if not legBlockTime:
                        legBlockTimeFmt = ' - '
                    if legACChange:
                        legACType += '*'
                    if legLastInDuty:
                        legGroundTime = ''
                    if dutyLegIndex == 1:
                        legBox.add(
                            Row(Text(' ', colspan=2),
                                Text('Duty start'),
                                Text(dutyStart),
                                Text(' ', colspan=4)))

                    legBox.add(Row(
                        Text('%s %s' % (legDay, legWeekday)),
                        Text('%s%s%s' % (legDH, legFlightNr, legFlightSuffix)),
                        Text('%s-%s' % (legStartStation, legEndStation)),
                        Text(legDeparture),
                        Text(legArrival),
                        Text(legMealCode),
                        Text(legBlockTimeFmt, align=LEFT),
                        Text(legACType, align=LEFT),
                        Text(legGroundTime, align=LEFT),
                        Text(legPoints)))
                    dutyLegIndex += 1

                legBox.add(
                    Row(Text(' ', colspan=2),
                        Text('Duty end'),
                        Text(' '),
                        Text(dutyEnd),
                        Text(' ', colspan=3)))

                dutyBox.add(Row(Text('Duty'),
                                Text(dutyTime, align=LEFT)))
                dutyBox.add(Row(Text('Block'),
                                Text(dutyBlockTime, align=LEFT)))
                dutyBox.add(Row(Text('Rest'),
                                Text(dutyRestTime, align=LEFT)))

                
                legDutyBox.add(Row(legBox, ' ', dutyBox))
                
            tripBox.add(Row(legDutyBox, ' ', tripSummary, ' '))
            tripBox.add(Row(' '))
            tripBox.add(Row(' '))
            oneTrip = Row(tripBox)
            self.add(oneTrip)




