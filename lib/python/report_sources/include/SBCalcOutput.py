"""
 $Header$
 
 Trip statistics daily

 Lists a number of KF for all trips in
 a plan summarized by calendar day in the planning period.
 The time base is home base time
 
 Created:    September 2006
 By:         Jonas Carlsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import DataCollection, OutputReport
from report_sources.include.TripLengthEtab import TripLengthEtab
#from AbsDate import AbsDate
#from RelTime import RelTime

import os
import os.path
from datetime import datetime
# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'Trip statistics daily'
THINMARGIN = 2
THICKMARGIN = 8

# Need to specify the keys here to get them in the right order
KEYS = ['Work Days', 'AcBlock Hrs', 'Block Hrs',
        'Duty Hrs', 'Block Hrs/Work Days', 'Duty Hrs/Work Days']

GENERAL_KEYS = ['Night Stops', 'Day stops', 'AC legs', 'Active legs',
                'Passive legs', 'Extra seat legs', '1 Day Trips',
                '2 Day Trips', '3 Day Trips', '4 Day Trips', '5 Day Trips', 'UpperSB', 'LowerSB']

KEY_WD = KEYS[0]
KEY_AC_BLOCK = KEYS[1]
KEY_BLOCK = KEYS[2]
KEY_DUTY = KEYS[3]
KEY_AV_BLOCK = KEYS[4]
KEY_AV_DUTY = KEYS[5]
KEY_NIGHT_STOPS = GENERAL_KEYS[0]
KEY_DAY_STOPS = GENERAL_KEYS[1]
KEY_AC = GENERAL_KEYS[2]
KEY_ACTIVE = GENERAL_KEYS[3]
KEY_PASSIVE = GENERAL_KEYS[4]
KEY_EXTRA_SEATS = GENERAL_KEYS[5]
KEY_1_DAY_TRIPS = GENERAL_KEYS[6]
KEY_2_DAY_TRIPS = GENERAL_KEYS[7]
KEY_3_DAY_TRIPS = GENERAL_KEYS[8]
KEY_4_DAY_TRIPS = GENERAL_KEYS[9]
KEY_5_DAY_TRIPS = GENERAL_KEYS[10]
KEY_UPPER_SB = GENERAL_KEYS[11]
KEY_LOWER_SB = GENERAL_KEYS[12]
KEY_FD = 'Req Freedays (LH)'
def formatDate(date):
    try:
        d = date.yyyymmdd()
        return "%s-%s-%s" %(d[:4], d[4:6], d[6:])
    except:
        return str(date)

def formatDateStr(date):
    try:
        d = date.ddmonyyyy()
        return "%s" %(d[:9])
    except:
        return str(date)
# classes ================================================================{{{1

# PairingStatsDaily----------------------------------------------------------{{{2
class SBCalcOutput(SASReport):
    """
    Create the report using the Python Publisher API.

    Assumes that if a duty d starts on day D all of the time for
    duty d is assigned to day D
    """
    def setup(self, outputType):
        #################
        ## Basic setup
        #################

        # Get the mode, dated or standard, and the output format
        self.dated, = R.eval(CONTEXT, 'crg_pairing_statistics.%is_dated_mode%')
        self.csvReport = (outputType == 'csv')
          
        # Get Planning Period start and end and generate a list with the dates
        # in the planning period.
        self.dates = self.getDates()

        # Weekdays are needed for non dated plans
        self.weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']  
        
        # Setup the DataCollection
        DataCollection.dates = self.dates
        DataCollection.sumCategory = 'All bases'
        # Get the calendar weeks that cover the dates
        self.weeks = self.getWeeks()
        if self.dated:
            SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)
        else:
            SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)

        if self.csvReport: self.csvRows = list()       
        
    def getWeeks(self):
        weeks = []
        if self.dated:
            #self.weeks = []
            found_weeks = []
            if self.odd_dates:
                dates = self.dates[:-1]
            else:
                dates = self.dates
            for date in dates:
                week, = R.eval('format_time(%s, "%%W")' % date)
                if week not in found_weeks:
                    weeks.append((week, date))
                    found_weeks.append(week)

            for w in range(len(weeks)):
                (week, start_date) = weeks[w]
                try:
                    (next_week, next_start_date) = weeks[w + 1]
                except IndexError:
                    next_start_date = dates[-1] + RelTime(24, 0)
                weeks[w] = (week, start_date, next_start_date - RelTime(24, 0))
        # Add the entire period as the last "week", not including
        # the extra date added if the number of dates are odd
        if self.odd_dates:
            weeks.append((0, self.dates[0], self.dates[-2]))
        else:
            weeks.append((0, self.dates[0], self.dates[-1]))
        return weeks

    def getRawSBData(self, context=CONTEXT):
        fe = R.foreach(R.iter('iterators.duty_set', where = 'report_sb_overview.%duty_is_sh_standby_to_consider% or studio_sb_handling.%consider_duty_for_sb_calculation%'),
                       'trip.%homebase%',
                       'report_common.%upper_sb%',
                       'report_common.%lower_sb%',
                       'crg_pairing_statistics.%duty_start_day%',
                       'report_sb_overview.%duty_is_sh_standby_to_consider%',
                       'studio_sb_handling.%consider_duty_for_sb_calculation_no_sb%')
        duties, = R.eval(context, fe)
        return duties
    def getRawData(self, context=CONTEXT):
        #################
        ## Data collecting
        #################        

        # This report should always use home base times (Scandinavian times)
        # Therefore make sure that the time mode parameter is set accordingly
        # Also save the previous value so that it can be reset
        tm_old, = R.eval('crg_trip.time_mode')
        tm_hb, = R.eval('crg_basic.timemode_HB')
        R.param('crg_trip.time_mode').setvalue(tm_hb)
        
        # The Rave API expression that gives the trip and duty values that we need
        fe = R.foreach(R.iter('iterators.trip_set', where = 'studio_sb_handling.%consider_trip_for_sb_calculation%'),
                       'trip.homebase',
                       'crg_trip.trip_start_day_safe',
                       'crg_pairing_statistics.trip_start_weekday',
                       'crg_trip.trip_days_safe',
                       'crew_pos.trip_assigned',
                       'trip.is_long_haul',
                       'report_common.num_night_stops_in_trip',
                       'report_common.num_day_stops_in_trip',
                       'trip.num_legs',
                       'trip.num_active_legs',
                       'trip.num_deadheads',
                       'report_common.num_extra_seat_legs_in_trip', 
                       'report_common.is_1_day_trip', 
                       'report_common.is_2_day_trip',
                       'report_common.is_3_day_trip',
                       'report_common.is_4_day_trip',
                       'report_common.is_5_day_trip',
                       R.foreach(R.times(12),
                                 'report_common.%no_of_crew_in_pos_ix%',
                                 'report_common.%req_freedays_after_trip_in_pos_ix%'
                                 ),
                       R.foreach(R.iter('iterators.duty_set'),
                                 'crg_pairing_statistics.duty_start_day',
                                 'crg_pairing_statistics.duty_start_weekday',
                                 'duty.block_time',
                                 'report_common.duty_duty_time',
                                 R.foreach(R.iter('iterators.leg_set'),
                                           'report_common.%leg_key%',
                                           'leg.%block_time%',
                                           'leg.%is_deadhead%'
                                           )
                                 )
                       )

        # Evaluate the RAVE expression
        trips, = R.eval(context, fe)

        # Reset time mode so other reports are not disturbed
        R.param('crg_trip.time_mode').setvalue(tm_old)
        return trips
    
    def getData(self, onlyProdDays = False, mybase = "ALL"):
        #################
        ## Data processing
        #################
        # Master data structure

        # Bool to check whether any req LH freedays have been found
        self.req_freedays_in_use = False

        allbases = (mybase == "ALL")
        raw = self.getRawData(CONTEXT)
        self.getDataForContext(onlyProdDays, mybase, allbases, raw)
        raw = self.getRawSBData("sp_crew")
        self.getDataForSBContext(onlyProdDays, mybase, allbases, raw)

    def getDataForSBContext(self, onlyProdDays, mybase, allbases, raw):
        for (_, base, upper, lower, date, sb, prod) in raw:
            if ((not allbases) and (not base == mybase)):
                continue
            if (not base in self.data):
                # If it doesn't exist we create it
                self.data[base] = DataCollection(base)
            dt = self.data[base]
            if sb:
                if upper:
                    dt.add(KEY_UPPER_SB, date, 1)
                if lower:
                    dt.add(KEY_LOWER_SB, date, 1)
            if prod:
                dt.add(KEY_WD, date, 1)
    def getDataForContext(self, onlyProdDays, mybase, allbases, raw):
        self.data = dict()
        # We need to check individual flights to keep track of ac block hrs
        added_flights = []
        # Iterate over the results and collect daily data
        for (_, base, trip_start_day, trip_start_weekday, trip_days,
             trip_assigned, is_long_haul, night_stops, day_stops, ac,
             active_legs, passive_legs, extra_seats, one_day_trip, two_day_trip,
             three_day_trip, four_day_trip, five_day_trip, freedays, duties) in raw:
            if ((not allbases) and (not base == mybase)):
                continue
            # Get a link to the appropriate data structure to reduce typing.
            if (not base in self.data):
                # If it doesn't exist we create it
                self.data[base] = DataCollection(base)
            dt = self.data[base]
            
            ## Add trip dependent data
            for i in range(trip_days):
                dt.add(KEY_WD, trip_start_day + RelTime(i * 24, 00), trip_assigned)
            if (not onlyProdDays):
                dt.add(KEY_NIGHT_STOPS, trip_start_day, night_stops)
                dt.add(KEY_DAY_STOPS, trip_start_day, day_stops)
                dt.add(KEY_AC, trip_start_day, ac)
                dt.add(KEY_ACTIVE, trip_start_day, active_legs)
                dt.add(KEY_PASSIVE, trip_start_day, passive_legs)
                dt.add(KEY_EXTRA_SEATS, trip_start_day, extra_seats)

                dt.add(KEY_1_DAY_TRIPS, trip_start_day, one_day_trip * 1)
                dt.add(KEY_2_DAY_TRIPS, trip_start_day, two_day_trip * 1)
                dt.add(KEY_3_DAY_TRIPS, trip_start_day, three_day_trip * 1)
                dt.add(KEY_4_DAY_TRIPS, trip_start_day, four_day_trip * 1)
                dt.add(KEY_5_DAY_TRIPS, trip_start_day, five_day_trip * 1)

                ## Add freedays (required after long haul)
                first_day_after_trip = trip_start_day + RelTime(24*trip_days,0) 
                for (_, no_of_crew, req_freedays) in freedays:
                    if is_long_haul and no_of_crew > 0 and req_freedays > 0:
                        self.req_freedays_in_use = True
                        for i in range(req_freedays):
                            dt.add(KEY_FD, first_day_after_trip + RelTime(i * 24, 00), no_of_crew)
                    else:
                        dt.add(KEY_FD, first_day_after_trip, 0)

                ## Iterate over duties
                for (_, duty_start_day, _,
                     duty_block, duty_duty, legs) in duties:

                    ## Add duty dependent data
                    dt.add(KEY_BLOCK, duty_start_day, duty_block * trip_assigned)
                    dt.add(KEY_DUTY, duty_start_day, duty_duty * trip_assigned)

                    for (_, leg_key, leg_time, leg_is_deadhead) in legs:
                        if leg_key in added_flights:
                            continue
                        else:
                            if not leg_is_deadhead:
                                added_flights.append(leg_key)
                            dt.add(KEY_AC_BLOCK, duty_start_day, leg_time)
        if (not onlyProdDays):
        # Sum data for all bases
            self.sumData(self.data)
            # Create daily averages
            for base in self.data:
                dt = self.data[base]
                for date in self.dates:
                    days = dt.get(KEY_WD, date)
                    if days == 0:
                        # Avoid division by zero in else branch
                        dt.add(KEY_AV_BLOCK, date, RelTime(0, 0))
                        dt.add(KEY_AV_DUTY, date, RelTime(0, 0))

                    else:
                        # Block time
                        try:
                            (h, m) = (dt.get(KEY_BLOCK, date) / days).split()
                        except:
                            (h, m) = (0, 0)
                        av_block = RelTime(h, m)
                        dt.add(KEY_AV_BLOCK, date, av_block)

                        # Duty time
                        try:
                            (h, m) = (dt.get(KEY_DUTY, date) / days).split()
                        except:
                            (h, m) = (0, 0)
                        av_duty = RelTime(h, m)
                        dt.add(KEY_AV_DUTY, date, av_duty)

            # Create total for base
            for base in self.data.keys():
                dt = self.data[base]
                self.getDataForBase(base, dt)

    def getDataForBase(self, base, dt):
        total_night_stops = 0
        total_day_stops = 0
        total_ac = 0
        total_active_legs = 0
        total_passive_legs = 0 
        total_extra_seats = 0
        total_one_day_trips = 0
        total_two_day_trips = 0
        total_three_day_trips = 0
        total_four_day_trips = 0
        total_five_day_trips = 0
        for date in self.dates:
            # Night stops
            try:
                night_stops = dt.get(KEY_NIGHT_STOPS, date)
            except:
                night_stops = 0
            total_night_stops = total_night_stops + night_stops

            # Day stops
            try:
                day_stops = dt.get(KEY_DAY_STOPS, date)
            except:
                day_stops = 0
            total_day_stops = total_day_stops + day_stops

            # AC legs
            try:
                ac = dt.get(KEY_AC, date)
            except:
                ac = 0
            total_ac = total_ac + ac

            # Active legs
            active_legs = dt.get(KEY_ACTIVE, date)
            total_active_legs = total_active_legs + active_legs 

            # Passive legs
            passive_legs = dt.get(KEY_PASSIVE, date)
            total_passive_legs = total_passive_legs + passive_legs

            # Extra seats
            extra_seats = dt.get(KEY_EXTRA_SEATS, date)
            total_extra_seats = total_extra_seats + extra_seats

            # 1 Day trips
            one_day_trips = dt.get(KEY_1_DAY_TRIPS, date)
            total_one_day_trips = total_one_day_trips + one_day_trips

            # 2 Day trips
            two_day_trips = dt.get(KEY_2_DAY_TRIPS, date)
            total_two_day_trips = total_two_day_trips + two_day_trips

            # 3 Day trips
            three_day_trips = dt.get(KEY_3_DAY_TRIPS, date)
            total_three_day_trips = total_three_day_trips + three_day_trips

            # 4 Day trips
            four_day_trips = dt.get(KEY_4_DAY_TRIPS, date)
            total_four_day_trips = total_four_day_trips + four_day_trips

            # 5 Day trips
            five_day_trips = dt.get(KEY_5_DAY_TRIPS, date)
            total_five_day_trips = total_five_day_trips + five_day_trips

        dt.add(KEY_NIGHT_STOPS, base, total_night_stops)
        dt.add(KEY_DAY_STOPS, base, total_day_stops)
        dt.add(KEY_AC, base, total_ac)
        dt.add(KEY_ACTIVE, base, total_active_legs)
        dt.add(KEY_PASSIVE, base, total_passive_legs)
        dt.add(KEY_EXTRA_SEATS, base, total_extra_seats)
        dt.add(KEY_1_DAY_TRIPS, base, total_one_day_trips)
        dt.add(KEY_2_DAY_TRIPS, base, total_two_day_trips)
        dt.add(KEY_3_DAY_TRIPS, base, total_three_day_trips)
        dt.add(KEY_4_DAY_TRIPS, base, total_four_day_trips)
        dt.add(KEY_5_DAY_TRIPS, base, total_five_day_trips)
    
    def getDates(self):
        pp_start,pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')
        #pp_length = int((pp_end - pp_start) / RelTime(24, 00))
        dates = []
        date = pp_start
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)
        # Get an even number of dates
        self.odd_dates = len(dates) % 2 == 1
        if self.odd_dates:
            dates.append(dates[-1] + RelTime(24, 0))
        return dates

    def presentData(self):
        name, aname, periodName, version, period = R.eval('sb_handling.%sb_handling_table_p%','global_sp_name', 'global_lp_name', 'global_fp_version', 'crg_info.%period%')
        self.presentRawData(name, periodName)
        #else:
        #    self.presentNormalData()
            
    def presentBaseForDate(self, csvRows, prodDays, base, date, upper_sb, lower_sb):
        try:
            csvRows.append("%s;%s;%s;%s;%s;" %(base, formatDate(date), prodDays,upper_sb, lower_sb))
        except:
            #dateData = 0
            print "No data for %s;%s;%s;%s;%s;" %(base, formatDate(date), prodDays, upper_sb, lower_sb)

    def presentBase(self, csvRows, dt, base):
        for date in self.dates:
            prodDays  = dt.get(KEY_WD, date) or 0
            upper_sb = dt.get(KEY_UPPER_SB, date) or 0
            lower_sb = dt.get(KEY_LOWER_SB, date) or 0
            self.presentBaseForDate(csvRows, prodDays, base, date, upper_sb, lower_sb)

    def presentRawData(self, name, periodString = ""):
        # build report
        csvRows = []
        dataExists = True
        samba_path = os.getenv('SAMBA', "/samba-share")
        if dataExists:    
            for base in self.data.keys():
                self.presentBase(csvRows, self.data[base], base)
        else:
            csvRows.append("No trips")
        mypath = "%s/%s/" %(samba_path, 'reports/SBHandling/CMSOutput')
        #, source, periodString)
        if not os.path.isdir(mypath):
            os.makedirs(mypath)
        timeStamp = str(datetime.now().date())
        reportName = "ProdDays_%s_%s-%s_%s" %(name , formatDateStr(self.dates[0]),formatDateStr(self.dates[len(self.dates)-1]),timeStamp)
        myFile = mypath + reportName + '.csv'
        csvFile = open(myFile, "w")
        csvFile.write(name + "\n")
        for row in csvRows:
            csvFile.write(row + "\n")
        csvFile.close()
        self.add("The output data is saved in %s" %myFile)
        
    def presentNormalData(self):
        #################
        ## Format the output
        #################
                    
        # 4 cases need to be handled: Dated-Standard, Dated-Csv, Weekly-Standard, Weekly-Csv
        # Especielly the Weekly variant differ somewhat from the Dated and require some
        # special treatment
        # Add the sum category as the last 'base' in the output and loop over
        # all possible bases
        self.SAS_BASES = self.SAS_BASES + (DataCollection.sumCategory,)
        for base in self.SAS_BASES:
            if base in self.data:
                self.baseBox = Column()
                self.calendarBox = Column()
                self.summaryBox = Column()

                if self.csvReport:
                    # If we're building a csv report we add a row with the rank
                    # and a calendar row.
                    self.csvRows.append('')
                    self.csvRows.append(base)
                    self.csvRows.append(self.getCalendarRow(
                        self.dates, leftHeader = 'Date', csv = self.csvReport))
                    self.buildBox(base)
                else:
                    # If we're building a standard report we create boxes to
                    # enable page breaks control.
                    self.calendarBox.add(Row(Text(base, font = self.HEADERFONT)))
                    # If in dated mode then divide the calendar in two rows to fit
                    if self.dated:
                        half_dates = len(self.dates) / 2
                        date_intervals = [self.dates[:half_dates],
                                          self.dates[half_dates:]]
                    else:
                        date_intervals = [self.dates]
                    #interval = 0
                    for dates in date_intervals:
                        self.calendarBox.add(self.getCalendarRow(dates, leftHeader = 'Date', csv = self.csvReport, isDated = self.dated))#, markDay = 6))
                        self.buildBox(base, dates)
                        self.calendarBox.add(Row(''))
                    self.baseBox.add((self.calendarBox))

                # Add summarys for all the calendar weeks covering the dates
                # Or all weekdays if the plan is not dated
                self.buildSummaryHeader(base, self.weeks)
                self.buildSummaryBox(base, self.weeks)
                self.baseBox.add(Isolate(self.summaryBox))
                
                self.buildGeneralStatisticsHeader(base, self.weeks)
                self.buildGeneralStatisticsBox(base, self.weeks)

                if not self.csvReport:
                    self.add(Row(self.baseBox))
                    if not base == DataCollection.sumCategory: self.newpage()

        if self.csvReport:
            self.set(font=Font(size=14))
            csvObject = OutputReport(TITLE, self, self.csvRows)
            self.add(csvObject.getInfo())
    
    def create(self, outputType = 'standard', onlyProdDays = True):
        self.setup(outputType)
        base, = R.eval('sb_handling.%sb_base%')
        self.getData(onlyProdDays, base)
        self.presentData()
        self.createTripLengthEtab()

    def createTripLengthEtab(self):
        otherR = TripLengthEtab()
        duties,dataExists = otherR.getData(CONTEXT)
        etab_name, = R.eval('sb_handling.%sb_daily_length_table_p%')
        etab_path = "%s/%s/%s" %(os.environ['CARMDATA'], 'ETABLES', etab_name)
        otherR.presentRawData(duties, dataExists, etab_path)
        

    def buildBox(self, base, dates = None):
        """
        Builds a box with the appropriate data rows.
        """
        # Create a link to the data to reduce typing
        dt = self.data[base]
        
        header = ""
        box = self.calendarBox
        if not dates: dates = self.dates

        # We have to do this since freeday data will typically not be available,
        # so we only include the row if data exists.
        if self.req_freedays_in_use:
            loop_keys = KEYS +[KEY_FD,]
        else:
            loop_keys = KEYS
            
        for key in loop_keys: 
            items = []
            if self.dated:
                for date in dates:
                    items.append(dt.get(key, date))
            else:
                if key == KEY_AV_BLOCK or key == KEY_AV_DUTY:
                    # The date dependent calculation performed earlier
                    # is not correct for a standard week, recompute here
                    for weekday in self.weekdays:
                        days = dt.getWeekdaySum(KEY_WD, weekday)
                        if key == KEY_AV_BLOCK: val = dt.getWeekdaySum(KEY_BLOCK, weekday)
                        elif key == KEY_AV_DUTY: val = dt.getWeekdaySum(KEY_DUTY, weekday)
                        items.append(val / days)
                else:
                    for weekday in self.weekdays:
                        items.append(dt.getWeekdaySum(key, weekday))
            dataRow = self.dataRow(key, items)
            if self.csvReport:
                self.csvRows.append(header + dataRow)
            else:
                box.add(dataRow)

    def buildSummaryHeader(self, base, weeks = None):
        """
        Builds the header of the summary box
        """
        box = self.summaryBox
    
        if self.csvReport:
            csv_row1 = 'Summary %s;' % base
            csv_row2 = ';'
        else:
            tmp_row = self.getCalendarHeaderRow()
            tmp_row.add(Text('Summary %s' % base))
            
        for (week, start_date, end_date) in weeks:
            if self.dated:
                start_date_str, = R.eval('crg_date.%%print_day_month%%(%s)' % start_date)
                end_date_str, = R.eval('crg_date.%%print_day_month%%(%s)' % end_date)
            else:
                start_date_str = self.weekdays[0] 
                end_date_str = self.weekdays[-1] 
                
            if self.csvReport:
                csv_row1 += '%s - %s;;;' % (start_date_str, end_date_str)
                csv_row2 += 'Average;Total;;'
 
            else:
                tmp_row.add(Column(Row(Text('%s - %s' % (start_date_str, end_date_str), align = CENTER)),
                                   Row(Text('Average', align = RIGHT),
                                       Text('Total', align = RIGHT),
                                       Text(''))))
        if self.csvReport:
            self.csvRows.append(csv_row1)
            self.csvRows.append(csv_row2)
        else:
            box.add(tmp_row)

    def buildGeneralStatisticsHeader(self, base, weeks = None):
        """
        Builds the header of the general statistics box
        """
        
        box = self.summaryBox
        box.add(Row(""))
        
        if self.csvReport:
            csv_row1 = 'General Statistics %s;' % base
            csv_row2 = ';'
        else:
            tmp_row = self.getCalendarHeaderRow()
            tmp_row.add(Text('General Statistics %s' % base))

        start_date = self.dates[0]
        end_date = self.dates[-1]
        start_date_str, = R.eval('crg_date.%%print_day_month%%(%s)' % start_date)
        end_date_str, = R.eval('crg_date.%%print_day_month%%(%s)' % end_date)
                        
        if self.csvReport:
            csv_row1 += '%s - %s;;;' % (start_date_str, end_date_str)
            csv_row2 += 'Total;;'
        else:
            tmp_row.add(Column(Row(Text('Total', align = RIGHT),
                                   Text(''))))

        if self.csvReport:
            self.csvRows.append(csv_row1)
        else:
            box.add(tmp_row)
                
    def buildSummaryBox(self, base, weeks = None): #fromDate = None, toDate = None):
        """
        Builds the Base / All bases totals
        """
        # Create a link to the data to reduce typing
        dt = self.data[base]
        header = ""
        box = self.summaryBox

        if not weeks:
            weeks = [(0, None, None)]

        # We have to do this since freeday data will typically not be available,
        # so we only include the row if data exists.
        if self.req_freedays_in_use:
            loop_keys = KEYS +[KEY_FD,]
        else:
            loop_keys = KEYS
       
        # For this to work, unfortunately some assumptions have to be made on
        # the keys. If more keys are added to the report, then this
        # code might have to be updated as well 
        for key in loop_keys:
            #key_row = Row()
            key_values = []
            space = ''
            for (_, fromDate, toDate) in weeks:
                if key == KEY_AV_BLOCK:
                    # Total block / Total work days
                    block = dt.getSum(KEY_BLOCK, fromDate, toDate)
                    wd = dt.getSum(KEY_WD, fromDate, toDate)
                    if wd == 0: key_values += [RelTime(0, 0), 'N/A', space]
                    else: key_values += [block / wd, 'N/A', space]

                elif key == KEY_AV_DUTY:
                    # Total duty / Total work days
                    duty = dt.getSum(KEY_DUTY, fromDate, toDate)
                    wd = dt.getSum(KEY_WD, fromDate, toDate)
                    if wd == 0: key_values += [RelTime(0, 0), 'N/A', space]
                    else: key_values += [duty / wd, 'N/A', space]

                elif key in (KEY_WD, KEY_FD):
                    # Keep the average work day/freeday to two decimals
                    key_values += ["%.2f" % dt.getAverage(key, fromDate, toDate, self.dated), dt.getSum(key, fromDate, toDate), space]
                else:
                    key_values += [dt.getAverage(key, fromDate, toDate, self.dated), dt.getSum(key, fromDate, toDate), space]

            dataRow = self.dataRow(key, key_values)
            if self.csvReport:
                self.csvRows.append(header + dataRow)
            else:
                box.add(dataRow)

    def buildGeneralStatisticsBox(self, base, weeks = None): #fromDate = None, toDate = None):
        """
        Builds the Base / All bases totals
        """
        # Create a link to the data to reduce typing
        dt = self.data[base]
        header = ""
        box = self.summaryBox

        if not weeks:
            weeks = [(0, None, None)]
        
        trip_loop_keys = GENERAL_KEYS
       
        #key_row = Row()
        space = ''
        #fromDate = weeks[0][1]
        #toDate = weeks[0][2]
        for key in trip_loop_keys:
            key_values = [dt.get(key, base), space]

            dataRow = self.dataRow(key, key_values)
            if self.csvReport:
                self.csvRows.append(header + dataRow)
            else:
                box.add(dataRow)

                
    def dataRow(self, header, items):
        """
        Generates a row in the appropriate format.
        """
        
        if self.csvReport:
            output = header
            for item in items:
                output += ";" + str(item)
        else:
            output = Row()
            output.add(Text(header,
                            font=Font(weight=BOLD)))
            for item in items:
                output.add(Text(item, align=RIGHT))
        return output

    def sumData(self, data):
        """
        Adds the values from all data categories (bases) and creates a data
        collection with the total sum. 
        """
        sum = DataCollection('All bases')

        for base in data:
            sum.addDataCollection(data[base])
        data['All bases'] = sum
        
### End of file
