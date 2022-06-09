"""
 $Header$
 
 Production Distribution

 Lists the available crew, the various types of assigned activities, and the
 unassigned production in the planning period.

 Data is separated by rank, and if more than one rank is present, a summed total
 is included at the end.

 The report is available in standard (pdf/html) format and in csv.
 
  
 Created:    April 2007
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# Imports and constants
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import DataCollection, OutputReport
from RelTime import RelTime
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator as CCL
import Cui

TITLE = 'Production Distribution'
RANKS_IN_USE = ("FC","FP","FR","AP","AS","AH","All crew")
SUM_CATEGORY = "All crew"
CONTEXT_DEFAULT = 'default_context'
CONTEXT_ALL = 'sp_crew'

# The keys are separated in manco and assigned to enable separated sections in
# the report.
MANCO_KEYS = ("SH Flight days", "SH Active legs",
              "LH Flight days", "LH Active legs")
ASSIGNED_KEYS = ("Total (FG)", "Total (VG)",
                 "FTE (FG)", "FTE (VG)",
                 "Net FTE (FG)",  "Net FTE (VG)",
                 "Flights SH", "Flights LH", "Flights below rank",
                 "SBY SH", "SBY LH", "SBY Scattered",
                 "BL", "F (FG)", "F (VG)", "VAC", "Compdays", "LOA",
                 "PT Freedays", "ILL",
                 "ADM", "SIM", "REC", "Other")

# These keys define where a bottom border is wanted.
BORDER_KEYS = ("Net FTE (VG)", "SBY Scattered", "ILL")
        
class ProductionDistribution(SASReport):
    """
    The main class for the report.
    """
    def sumData(self):
        """
        Adds the values from all data categories (ranks) and creates a data
        collection with the total sum.
        """
        sum = DataCollection(SUM_CATEGORY)
        for rank in self.data:
            sum.addDataCollection(self.data[rank])
        self.data[SUM_CATEGORY] = sum

    def create(self, outputType = 'standard', allCrew = True):
        #print "create report with allCrew=",allCrew
        """
        The main function for generating the report.

        Can be called with a parameter that defines report type
        ('standard' (pdf) or 'csv').
        """
        self.modify_pp()
        self.csvReport = (outputType == 'csv')            
        SASReport.create(self, TITLE, orientation=LANDSCAPE,
                         usePlanningPeriod=True)
        
        # Get Planning Period start and end and generate a list with the dates
        # in the planning period.
        pp_start,pp_end = R.eval('fundamental.%pp_start%',
                                 'fundamental.%pp_end%')
        pp_length = int((pp_end - pp_start) / RelTime(24, 00))
        self.dates = []
        for day in range(pp_length):
            self.dates.append(pp_start + RelTime(24*day,0))
            
        DataCollection.dates = self.dates
        #DataCollection.keys = MANCO_KEYS + ASSIGNED_KEYS
        DataCollection.sumCategory = SUM_CATEGORY

        self.data = dict()
        
        # Assigned production
        assignedProdExpr = R.foreach(
            R.iter('iterators.trip_set', where='trip.%in_pp%'),
            'trip.%start_day%',
            'trip.%days%',
            'crew.%in_fixed_group_trip_start%',
            'trip.%has_only_flight_duty%',
            'trip.%is_long_haul%',
            'crew_pos.%trip_lower_rank%',
            'trip.%is_standby%',
            'trip.%is_standby_line%',
            'trip.%is_standby_long_haul%',
            'trip.%is_scattered_standby_at_home%',
            'trip.%is_off_duty%',
            'trip.%is_freeday%',
            'trip.%is_vacation%',
            'trip.%is_compensation_day%',
            'trip.%is_loa%',
            'trip.%is_pt_freeday%',
            'trip.%is_illness%',
            'trip.%is_meeting% or trip.%is_office_duty%',
            'trip.%is_simulator%',
            'trip.%has_recurrent%',# or trip.%is_emg%',
            'trip.%is_gnd%',
            'trip.%is_blank_day%',
            )
        
        rosterExpr = R.foreach(
            'iterators.roster_set',
            'crew.%rank%',
            'crew.%in_fixed_group_pp_start%',
            'crew.%group_change_in_pp%',
            'crew.%first_group_change_date_pp_start%',
            'crew.%second_group_change_date_pp_start%',
            'crew.%part_time_factor_pp_start%',
            'crew.%part_time_factor_pp_end%',
            'crew.%part_time_change_in_pp_date%',
            assignedProdExpr,
            )
        
        context = CONTEXT_ALL if allCrew else CONTEXT_DEFAULT
        #print "selecting context ",context
        rosters, = R.eval(context, rosterExpr)
        for (ix, rank,
             inFixedGroupPPStart, groupChangeInPP,
             firstGroupChangeDate, secondGroupChangeDate,
             partTimePPStart, partTimePPEnd, partTimeChangeDate,
             trips) in rosters:
                 
            # secondGroupChangeDate is 01Jan1986 if no change  
            if (secondGroupChangeDate < pp_end and
               secondGroupChangeDate > pp_start):
                secondGroupChange = True
            else:
                secondGroupChange = False
                
            if (rank in RANKS_IN_USE):
                # Get a link to the appropriate data structure to reduce typing.
                if (not rank in self.data):
                    # If it doesn't exist we create it
                    self.data[rank] = DataCollection(rank)
                dt = self.data[rank]
                    
                # Number of crew data
                fixedGroup = inFixedGroupPPStart
                partTime = partTimePPStart
                partTimeChangeInPP = (partTimeChangeDate is not None)
                # We allow one change in the planning period. These variables
                # control the change. By initializing them to whether there is
                # a change in pp we reduce the if-cases.
                groupChanged = not groupChangeInPP
                groupChangedAgain = not secondGroupChange
                partTimeChanged = not partTimeChangeInPP

                for date in self.dates:
                    # If the group or parttime hasn't been changed (but should)
                    # groupChanged/partTimeChanged will be False. If the date is
                    # the change date we switch the variables.
                    if (not groupChanged and (date >= firstGroupChangeDate)):
                        fixedGroup = not fixedGroup
                        groupChanged = True
                    if (not groupChangedAgain and
                        (date >= secondGroupChangeDate)):
                        fixedGroup = not fixedGroup
                        groupChangedAgain = True
                    if (not partTimeChanged and (date >= partTimeChangeDate)):
                        partTime = partTimePPEnd
                        partTimeChanged = True
                    if fixedGroup:
                        group = "FG"
                    else:
                        group = "VG"
                    
                    totKey = "Total (%s)" %group
                    fteKey = "FTE (%s)" %group
                    fteNetKey =  "Net FTE (%s)" %group
                    # Part time is returned from rave as percent (factor 100)
                    partTimeQ = partTime/100.0
                    # The FTE Net is added here to be reduced later.
                    for (key, val) in zip(
                        (totKey, fteKey, fteNetKey), (1, partTimeQ, partTimeQ)):
                        dt.add(key, date, val)

                # Used days are saved in a dictionary to enable counting of empty
                # days.
                usedDays = dict()

                for (jx, startDate, days, fixedGroupTripStart,
                     flightDuty, longHaul, belowRank,
                     standby, standbyLine, standbyLH, scatteredStandby,
                     offDuty, freeday, vacation, compday, loa, ptFreeday, ill,
                     meetingOrOffice, sim, recOrEmg, groundDuty, bl) in trips:
                    # The default case is to not reduce the FTE with the trip
                    #days.
                    reduceFTE = False
                    if fixedGroupTripStart:
                        group = "FG"
                    else:
                        group = "VG"
                    fteNetKey = "Net FTE (%s)" %group
                    
                    # Flight duties
                    if flightDuty:
                        if scatteredStandby:
                            key = "SBY Scattered"
                        elif standbyLine or standbyLH:
                            # Standby lines and cabin standby with code RAL are interpreted as long haul standbys.
                            key = "SBY LH"
                        elif standby:
                            # Standbys that are not scattered or line are
                            # interpreted as short haul standbys.
                            key = "SBY SH"
                        else:
                            # Flight duty that is not standby
                            if longHaul:
                                type = "LH"
                            else:
                                type = "SH"
                            key = "Flights %s" %type

                    # Off duties
                    elif offDuty:
                        # Freedays needs to be handled last since other off duty
                        # activities can count as freeday.
                        reduceFTE = True
                        if vacation:
                            key = "VAC"
                        elif ill:
                            key = "ILL"
                        elif loa:
                            key = "LOA"
                        else:
                            # For the remaining cases the FTE should not be reduced.
                            reduceFTE = False
                            if compday:
                                key = "Compdays"
                            elif ptFreeday:
                                key = "PT Freedays"
                            elif freeday:
                                key = "F (%s)" %group
                                                        
                    # Other on-duties that are not flight duties.
                    else:
                        if bl:
                            key = "BL"
                        else:
                            if meetingOrOffice:
                                key = "ADM"
                            elif sim:
                                key = "SIM"
                            elif recOrEmg:
                                key = "REC"
                            else:
                                key = "Other"

                    for day in range(days):
                        # For all days in the trip we add it to the appropriate
                        # category and reduce the FTE if it should be done.
                        date = startDate + RelTime(24*day,0)
                        if (usedDays.get(date, False)):
                            # The day already has a registered activity.
                            # This specifically handles SIM activities that have
                            # weird trip-breaks.
                            pass
                        else:
                            usedDays[date] = True
                            if reduceFTE:
                                dt.add(fteNetKey, date, -1)
                            dt.inc(key, date)
                            # A trip can be in both a flight duty category and
                            # in the fbr category.
                            if (flightDuty and belowRank):
                                dt.inc("Flights below rank", date)

                    # End of trip loop
                            
                # Open days
                for date in self.dates:
                    # If a date in the period isn't True in usedDays we assume
                    # it is empty.
                    if (not usedDays.get(date,False)):
                        fixedGroup = inFixedGroupPPStart
                        partTime = partTimePPStart
                        groupChanged = not groupChangeInPP
                        groupChangedAgain = not secondGroupChange
                        partTimeChanged = not partTimeChangeInPP
                        if (not groupChanged and (date >= firstGroupChangeDate)):
                            fixedGroup = not fixedGroup
                            groupChanged = True
                        if (not groupChangedAgain and
                            (date >= secondGroupChangeDate)):
                            fixedGroup = not fixedGroup
                            groupChangedAgain = True
                        if (not partTimeChanged and (date >= partTimeChangeDate)):
                            partTime = partTimePPEnd
                            partTimeChanged = True
                        if fixedGroup:
                            group = "FG"
                        else:
                            group = "VG"
                        dt.inc("F (%s)" % group, date)

                # End of crew loop
                
        # Remaining production
        rankExpr = R.foreach(
            R.times(10),
            'crew_pos.%pos2func%(fundamental.%py_index%)',
            'crew_pos.%trip_assigned_pos%(fundamental.%py_index%)',
            )
        
        legExpr = R.foreach(
            R.iter('iterators.leg_set', where='not leg.%is_deadhead%'),
            'leg.%start_date%',
            )

        remProdExpr = R.foreach(
            R.iter('iterators.trip_set',
                   where=('crew_pos.%trip_assigned% > 0',
                          'trip.%in_pp%')),
            'trip.%code%',
            'trip.%homebase%',
            'trip.%is_on_duty%',
            'trip.%start_day%',
            'trip.%days%',
            'trip.%is_long_haul%',
            legExpr,
            rankExpr,
            )

        saved = None

        remainingProd = None
        
        remainingProd, = R.eval('default_context',remProdExpr)
                
        for (ix, code, tripBase, onDuty, startDate, days, longHaul, legs, crew
             ) in remainingProd:

            # An unassigned trip can have multiple positions with a need > 0
            for (jx, rank, count) in crew:
                    
                # 'count' is the need in the current position. It can be > 1.
                # We ignore blank days.
                if (count > 0 and code != "BL"):
                    if (rank in RANKS_IN_USE):

                        # Get a link to the appropriate data structure to reduce
                        # typing.
                        if (not rank in self.data):
                            # If it doesn't exist we create it
                            self.data[rank] = DataCollection(rank)
                        dt = self.data[rank]

                        if longHaul:
                            type = "LH"
                        else:
                            type = "SH"
                        daysKey = "%s Flight days" %type
                        legsKey = "%s Active legs" %type
                        date = startDate
                        for day in range(days):
                            date = startDate + RelTime(24*day,0)
                            dt.add(daysKey, date, count)
                        for (kx, date) in legs:
                            dt.add(legsKey, date, count)

                # End of crew position loop

            # End of trip loop
            
        # If we're building a csv report we need to initialize a structure to
        # hold the rows.
        if self.csvReport:
            self.csvRows = []
            
        # Counter to control inclusion of "All crew" section.
        counter = 0
        
        # We loop over ranks instead of over keys in the data to control the
        # order of the sections.
        for rank in RANKS_IN_USE:
            if rank in self.data:
                counter += 1
                # When the counter hits 2 (i.e. more than one rank in the data)
                # we generate the sum.
                if (counter == 2):
                    self.sumData()
                    
                if self.csvReport:
                    # If we're building a csv report we add a row with the rank
                    # and a calendar row. 
                    self.csvRows.append(rank)
                    self.csvRows.append(self.getCalendarRow(
                        self.dates,leftHeader='Date', csv=self.csvReport))
                else:
                    # If we're building a standard report we create boxes to
                    # enable page breaks control.
                    rankBox = Column()
                    rankBox.add(Row(Text(rank, font=self.HEADERFONT)))
                    self.mancoBox = Column(self.getCalendarRow(
                        self.dates, leftHeader='Manco', rightHeader='Sum', 
                        csv=self.csvReport))
                    self.assignedBox = Column(self.getCalendarRow(
                        self.dates, leftHeader='Assigned', rightHeader='Sum', 
                        csv=self.csvReport))

                self.buildBox(rank)
                if allCrew:
                    self.buildBox(rank, manco=True)
                if not self.csvReport:
                    rankBox.add(Row(self.assignedBox))
                    if allCrew:
                        rankBox.add(Row(self.mancoBox))
                    self.add(Row(rankBox))
                    self.page0()

        if self.csvReport:
            self.set(font=Font(size=14))
            csvObject = OutputReport(TITLE, self, self.csvRows)
            self.add(csvObject.getInfo())

        self.reset_pp()
        
    def buildBox(self, rank, manco=False):
        """
        A function to build a box with the appropriate data rows.
        """
        # We create a link to the data to reduce typing
        dt = self.data[rank]

        if manco:
            keys = MANCO_KEYS
            if self.csvReport:
                header = "Manco "
            else:
                box = self.mancoBox
        else:
            keys = ASSIGNED_KEYS
            if self.csvReport:
                header = ""
            else:
                box = self.assignedBox

        for key in keys:
            items = []
            for date in self.dates:
                items.append(dt.get(key, date, type="int"))
            dataRow = self.dataRow(key, items)
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
            if header in BORDER_KEYS:
                output.set(border=border(bottom=0))
            output.add(Text(header,
                            font=Font(weight=BOLD),
                            border=border(right=0)))
            sum = 0
            for item in items:
                tmp = int(item+0.999)
                sum += tmp
                output.add(Text(tmp, align=RIGHT))
            output.add(Text(sum, align=RIGHT, border=border(left=0)))
        return output

# End of file
