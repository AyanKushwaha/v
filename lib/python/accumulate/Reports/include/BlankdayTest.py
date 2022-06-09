"""
 $Header$
 
 Blankday Distribution

 Lists the number of blankdays for each day in pp,
 separated by category (rank and base and total sum).
  
 Created:    December 2006
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime
import re
agmtgrp = 'SKD_CC_AG'
mon = 'AUG'
lis1 = []
tup1 = ()
tup2 = ()

# constants =============================================================={{{1
TITLE = 'Blankday Distribution'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

class BlankdayTest(SASReport):

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
        
        self.blankdaysInUse = "BL","BL1","BL2","BL3","BL5","BL7","BL8","BL9","BL12","BL20"

        #build where-expr.
        #Note: Should be replaced with trip.%is_blank_day%, but data is broken ATM
        where_expr = 'trip.%code% = "BL"'
        for blankday in self.blankdaysInUse:
            if (blankday != "BL"):
                where_expr += ' or trip.%code% = "'+blankday+'"'
        # Ranks in use
        # "Sum" and "mary" is some magic to build the header for the report 
        self.ranksInUse = "FC","FP","FR","AP","AS","AH","AA","-","Summary"
        self.basesInUse = "CPH","STO","OSL","TRD","SVG","BJS","NRT","SHA","-",""
        
        #print "building rave expression"
        trip_expr = R.foreach(
            R.iter('iterators.trip_set', where = where_expr),
            'trip.%starts_in_pp%',
            'trip.%start_day%',
            'trip.%code%',
            'trip.%days%',
            )
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='crew.%agmt_group_id% = '+ "\""+ str(agmtgrp) + "\""),
            'report_common.%crew_string%',
            'report_common.%crew_rank%',
            'report_common.%crew_homebase%',
            trip_expr,
            )
        rosters, = R.eval(CONTEXT, roster_expr)

        
        for crew_id in rosters:
          
          lis1 = crew_id[4]
          count = 0
          for lis in lis1:
             tup2 = lis
             abs = str(tup2[2])
             if mon in abs:
                 count = count + 1
          print str(re.findall(r'\(.*?\)', crew_id[1])),";",count,";"
       #     print "print", str(re.findall(r'\(.*?\)', crew_id[1])) , " ", abs
       #  print "Crew id is " , crew_id
       #  print "No of blankdays" , crew_id[4].count('JUL')
       #  print "Expected data is" , str(re.findall(r'\(.*?\)', crew_id[1])) , ";" , crew_id[4].count('JUL'), ";"
       #  print str(re.findall(r'\(.*?\)', crew_id[1])) , ";" , crew_id[4].count('JUL'), ";"
         
        
    def process_data(self, rosters):
        # Loop over all the 'bags' that comes from the RAVE expression
        # and collect the data.
        data = dict()
        for (ix, crewString, rank, base, trips) in rosters:
            if not (rank in self.ranksInUse):
                print "Strange rank: "+str(rank)+", CHECK THIS!"
                rank = "-"
            if not (base in self.basesInUse):
                print "Strange base: "+str(base)+", CHECK THIS!"
                base = "-"
            category = rank + base
            for (ix,in_pp,date,code,days) in trips:
                # Only do something if the current bag corresponds to a day
                # in the planning period and is a blankday
                if in_pp and (code in self.blankdaysInUse):
                    data[category] = data.get(category,dict())
                    data["Summary"] = data.get("Summary",dict())
                    data[category][code] = data[category].get(code,dict())
                    data["Summary"][code] = data["Summary"].get(code, dict())
                    try:
                        # Loop on days
                        for dayloop in range(days):
                            date_get = date + RelTime(24 * 60 * dayloop)
                            data[category][code][date_get] = data[category][code].get(date_get,0) + 1
                            data["Summary"][code][date_get] = data["Summary"][code].get(date_get,0) + 1
                    except:
                        print "Error "+str(date) + " " + code
        return data, crewString

    def output_data(self, data):
        # Output the provided data to the report
        if data:
            for base in self.basesInUse:
                for rank in self.ranksInUse:
                    category = rank + base
                    if ((category in data) and (self.generalReport or category != "Summary")):
                        categoryBox = Column()
                        if self.generalReport:
                            header = rank + ", " + base
                            if (category == "Summary"):
                                header = category
                            categoryBox.add(Row(Text(header),font=self.HEADERFONT))
                        categoryBox.add(self.headerRow(self.dates))
                        blankdays = []
                        dataBox = Column(border=border(left=0))
                        total = dict()
                        for blankday in self.blankdaysInUse:
                            if blankday in data[category]:
                                blankdays.append(blankday)
                                currentRow = Row()
                                sum = 0
                                for date in self.dates:
                                    tmp = data[category][blankday].get(date,0)
                                    total[date] = total.get(date,0)+tmp
                                    currentRow.add(Text(tmp,align=RIGHT))
                                    sum += tmp
                                currentRow.add(Text(sum, font=Font(weight=BOLD), align=RIGHT, border=border(left=0)))
                                dataBox.add(currentRow)
                        categoryBox.add(Row(
                            self.getTableHeader(blankdays, vertical=True),
                            dataBox))
                        categoryBox.add(self.sumRow(total,self.dates))
                        self.add(Row(categoryBox))
                        self.add(Row(" "))
                        self.page0()
        else:
            self.add("No blankdays")

# End of file
