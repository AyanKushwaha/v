"""
 $Header$
 
 Course and Office days distribution

 The report shows assigment specific Course and Office days for each day in pp,
 (and total sum).
  
 Created:    May 2007
 By:         Peter Schulz, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime

# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'Course and Office day Distribution'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

class CourseOfficedayDistribution(SASReport):

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
        objectReport = (reportType == "object")
        generalReport = not objectReport
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)
        
        # Get Planning Period start and end
        pp_start,pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')
        pp_length = (pp_end - pp_start) / RelTime(24, 00)
        date = pp_start
        dates = []
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)
        
        # Course and Office days in use
        #courseOfficedaysInUse = "MT11", "MT12", "MT17", "MT18", "OK41"

        courseOfficedaysIterator = R.iter('report_ccr.different_task_codes', where='report_ccr.%course_office_day%', sort_by=('leg.%code%'))
        fe = R.foreach(courseOfficedaysIterator, 'leg.%code%')
        bases, = R.eval(CONTEXT, fe)
        basecount = 0
        courseOfficedaysInUse = []
        for base in bases:
            basecount += 1
            duty = base[-1]
            courseOfficedaysInUse.append(duty)    

        # Ranks in use
        ranksInUse = "Summary" 
        ranksInUse2 = "FC","FP","FR","AP","AS","AH","AA","-","Summary" 
        
        #print "building rave expression"
        trip_expr = R.foreach(
            R.iter('iterators.trip_set'),
            'trip.%starts_in_pp%',
            'trip.%start_day%',
            'trip.%days%',
            'trip.%code%',
            )
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='fundamental.%is_roster%'),
            'report_common.%crew_string%',
            'report_common.%crew_rank%',
            trip_expr,
            )
        rosters, = R.eval(CONTEXT, roster_expr)

        data = dict()
        # Loop over all the 'bags' that comes from the RAVE expression
        # and collect the data
        for (ix,crewString,rank,trips) in rosters:
            if not (rank in ranksInUse):
                print "Strange rank: "+str(rank)+", CHECK THIS!"
                rank = "-"
            for (ix,in_pp,date,days,code) in trips:
                # Only do something if the current bag corresponds to a day
                # in the planning period and is a Course or Office day
                if in_pp and (code in courseOfficedaysInUse):
                    data["Summary"] = data.get("Summary",dict())
                    data["Summary"][code] = data["Summary"].get(code, dict())
                    for day in range(days):
                        this_date = date + RelTime(day*24,0)
                        try:
                            data["Summary"][code][this_date] = data["Summary"][code].get(this_date,0) + 1
                        except:
                            print "Error "+str(this_date) + " " + code
        if objectReport:
            self.add(Row(Text(crewString, font=self.HEADERFONT)))
        if data:
            for rank in ranksInUse2:
                if ((rank in data) and (generalReport ) and (rank != "-")):
                    rankBox = Column()
                    if generalReport:
                        rankBox.add(Row(Text(rank),font=self.HEADERFONT))
                    rankBox.add(self.headerRow(dates))
                    courseOfficedays = []
                    dataBox = Column(border=border(left=0))
                    total = dict()
                    for courseOfficeday in courseOfficedaysInUse:
                        if courseOfficeday in data[rank]:
                            courseOfficedays.append(courseOfficeday)
                            currentRow = Row()
                            sum = 0
                            for date in dates:
                                tmp = data[rank][courseOfficeday].get(date,0)
                                total[date] = total.get(date,0)+tmp
                                currentRow.add(Text(tmp,align=RIGHT))
                                sum += tmp
                            currentRow.add(Text(sum, font=Font(weight=BOLD), align=RIGHT, border=border(left=0)))
                            dataBox.add(currentRow)
                    rankBox.add(Row(
                        self.getTableHeader(courseOfficedays, vertical=True),
                        dataBox))
                    rankBox.add(self.sumRow(total,dates))
                    self.add(Row(rankBox))
                    self.add(Row(" "))
        else:
            self.add("No MT, OK, or UP days")
            
        self.reset_pp()

# End of file
