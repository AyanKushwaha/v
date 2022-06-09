"""
 $Header$
 
 Compday Distribution

 Lists the number of different compdays for each day in pp,
 separated by category (and total sum).
  
 Created:    December 2006
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime

# constants =============================================================={{{1
TITLE = 'Compday Distribution'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

class CompdayDistribution(SASReport):

    def headerRow(self, dates):
        tmpRow = self.getCalendarRow(dates,leftHeader='Type',rightHeader='Sum')
        return tmpRow

    def sumRow(self, data, dates):
        tmpRow = Row(border=border(top=0), font=Font(weight=BOLD))
        tmpRow.add(Text('Total', border=border(right=0)))
        sum = 0
        for date in dates:
            tmp = data.get(date,0)
            sum += tmp
            tmpRow.add(Text(tmp,align=RIGHT))
        tmpRow.add(Text(sum, border=border(left=0),align=RIGHT))
        return tmpRow
    
    def create(self, reportType):
        self.modify_pp()
        self.objectReport = (reportType == "object")
        self.generalReport = not self.objectReport
        if self.objectReport:
            CONTEXT = 'marked_in_window_left'
        else:
            CONTEXT = 'default_context'

        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)
        
        # Get Planning Period start and end
        pp_start,pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')
        pp_length = (pp_end - pp_start) / RelTime(24, 00)
        date = pp_start
        self.dates = []
        while date < pp_end:
            self.dates.append(date)
            date += RelTime(24,0)
        
        # Get the compdays in use
        #compdaysInUse = "F0","F1","F3","F3S","F31","F35","F7S","BL1"
        
        compdaysInUseRave = R.set('compdays.in_use').members()
        self.compdaysInUse = []
        for compday in compdaysInUseRave:
            self.compdaysInUse.append(compday)
        self.compdaysInUse.append("BL1")
        
        # Ranks in use
        self.ranksInUse = "FC","FP","FR","AP","AS","AH","AA","-","Summary" 
        
        #print "building rave expression"
        trip_expr = R.foreach(
            R.iter('iterators.trip_set'),
            'trip.%starts_in_pp%',
            'trip.%start_day%',
            'trip.%code%',
            'trip.%days%',
            )
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='fundamental.%is_roster%'),
            'report_common.%crew_string%',
            'report_common.%crew_rank%',
            trip_expr,
            )
        rosters, = R.eval(CONTEXT, roster_expr)

        if self.objectReport:
            for roster in rosters:
                data, crewString = self.process_data([roster])
                self.add(Row(Text(crewString, font=self.HEADERFONT)))
                self.output_data(data)
                self.page0()
        else:
            data, crewString = self.process_data(rosters)
            self.output_data(data)

        self.reset_pp()

    def process_data(self, rosters):
        # Loop over all the 'bags' that comes from the RAVE expression
        # and collect the data
        data = dict()
        for (ix,crewString,rank,trips) in rosters:
            if not (rank in self.ranksInUse):
                print "Strange rank: "+str(rank)+", CHECK THIS!"
                rank = "-"
            for (ix,in_pp,date,code,days) in trips:
                # Only do something if the current bag corresponds to a day
                # in the planning period and is a compday
                if in_pp and (code in self.compdaysInUse):
                    data[rank] = data.get(rank,dict())
                    data["Summary"] = data.get("Summary",dict())
                    data[rank][code] = data[rank].get(code,dict())
                    data["Summary"][code] = data["Summary"].get(code, dict())
                    try:
                        # Loop on days
                        for dayloop in range(days):
                            date_get = date + RelTime(24 * 60 * dayloop)
                            data[rank][code][date_get] = data[rank][code].get(date_get,0) + 1
                            data["Summary"][code][date_get] = data["Summary"][code].get(date_get,0) + 1
                    except:
                        print "Error "+str(date) + " " + code
        return data, crewString

    def output_data(self, data):
        # Output the provided data to the report
        if data:
            for rank in self.ranksInUse:
                if ((rank in data) and (self.generalReport or rank != "Summary")):
                    rankBox = Column()
                    if self.generalReport:
                        rankBox.add(Row(Text(rank),font=self.HEADERFONT))
                    rankBox.add(self.headerRow(self.dates))
                    compdays = []
                    dataBox = Column(border=border(left=0))
                    total = dict()
                    for compday in self.compdaysInUse:
                        if compday in data[rank]:
                            compdays.append(compday)
                            currentRow = Row()
                            sum = 0
                            for date in self.dates:
                                tmp = data[rank][compday].get(date,0)
                                total[date] = total.get(date,0)+tmp
                                currentRow.add(Text(tmp,align=RIGHT))
                                sum += tmp
                            currentRow.add(Text(sum, font=Font(weight=BOLD), align=RIGHT, border=border(left=0)))
                            dataBox.add(currentRow)
                    rankBox.add(Row(
                        self.getTableHeader(compdays, vertical=True),
                        dataBox))
                    rankBox.add(self.sumRow(total,self.dates))
                    self.add(Row(rankBox))
                    self.add(Row(" "))
        else:
            self.add("No compdays")

# End of file
