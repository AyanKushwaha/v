"""
 $Header$
 
 Standby Distribution

 Lists the number of standbys for each day in pp,
 separated by category (rank and base and total sum).
 This report does not include standby lines.
  
 Created:    March 2007
 By:         Jonas Carlsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime

# constants =============================================================={{{1
TITLE = 'Standby Distribution'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8
RanksInUse = "FC","FP","FR","AP","AS/AH","-","Summary"
BasesInUse = "CPH","STO","OSL","TRD","SVG","-",""
class StandbyDistribution(SASReport):

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

    def getData(self, show_RL, objectReport):
        duty_expr = R.foreach(
            R.iter('iterators.duty_set', where = ('report_common.%report_show_SB%', 'duty.%in_pp%')),
            'duty.%start_day%',
            'duty.%code%',
            'duty.%start_hb%',
            'duty.%end_hb%',
            'duty.%is_standby_line%'
            
            )
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='fundamental.%is_roster%'),
            'report_common.%crew_string%',
            'report_common.%crew_rank%',
            'report_common.%crew_homebase%',
            duty_expr,
            )
        rosters, = R.eval(self.context, roster_expr)

        if objectReport:
            data = []
            for roster in rosters:
                subData, crewString = self.getDataSub([roster], show_RL)
                data.append([crewString, subData])
        else:
            data, crewString = self.getDataSub(rosters, show_RL)

        return data

    def getDataSub(self, rosters, show_RL):
        data = dict()
        # Loop over all the 'bags' that comes from the RAVE expression
        # and collect the data
        for (ix, crewString, rank, base, duties) in rosters:
            if rank == 'AS' or rank == 'AH': rank = 'AS/AH'
            if not (rank in RanksInUse):
                print "Strange rank: "+str(rank)+", CHECK THIS!"
                rank = "-"
            if not (base in BasesInUse):
                print "Strange base: "+str(base)+", CHECK THIS!"
                base = "-"
            category = rank + base
            for (ix, date, code, start_hb, end_hb, sb_line) in duties:
                # Use the code and the start and end time as the key
                codeandtime = "%s (%s-%s)" % (code, start_hb.time_of_day(), end_hb.time_of_day())
                code = codeandtime
                # Only do something if the current bag corresponds to a day
                # in the planning period and is a standby
                data[category] = data.get(category, dict())
                data["Summary"] = data.get("Summary", dict())
                data[category][code] = data[category].get(code, dict())
                data["Summary"][code] = data["Summary"].get(code, dict())
                if (show_RL):
                    data[category]["Total RL"] = data[category].get("Total RL", dict())
                    data[category]["Total RS"] = data[category].get("Total RS", dict())
                    data["Summary"][rank + " Total RL"] = data["Summary"].get(rank + " Total RL", dict())
                    data["Summary"]["Total RL"] = data["Summary"].get("Total RL", dict())
                    data["Summary"]["Total RS"] = data["Summary"].get("Total RS", dict())
                try:
                    data[category][code][date] = data[category][code].get(date, 0) + 1
                    data["Summary"][code][date] = data["Summary"][code].get(date, 0) + 1
                    if (show_RL):
                        if (sb_line):
                            data[category]["Total RL"][date] = data[category]["Total RL"].get(date, 0) + 1
                            data["Summary"][rank + " Total RL"][date] = data["Summary"][rank + " Total RL"].get(date, 0) + 1
                            data["Summary"]["Total RL"][date] = data["Summary"]["Total RL"].get(date, 0) + 1
                        else:
                            data[category]["Total RS"][date] = data[category]["Total RS"].get(date, 0) + 1
                            data["Summary"]["Total RS"][date] = data["Summary"]["Total RS"].get(date, 0) + 1

                except:
                    print "Error " + str(date) + " " + code
        return data, crewString

    def getDates(self, pp_start,pp_end):
        # Get Planning Period start and end
        pp_length = (pp_end - pp_start) / RelTime(24, 00)
        date = pp_start
        dates = []
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)
        return dates
            
    def presentRankBaseData(self, rank, base, data, dates, objectReport, generalReport):
        category = rank + base
        if ((category in data) and (generalReport or category != "Summary")):
            # categoryBox = Column()
            if generalReport:
                header = rank + ", " + base
                if (category == "Summary"):
                    header = category
                # categoryBox.add(Row(Text(header), font=self.HEADERFONT))
                self.add(Row(Text(header), font=self.HEADERFONT))
            # categoryBox.add(self.headerRow(dates))
            self.add(self.headerRow(dates))
            standbys = []
            # dataBox = Column(border=border(left=0))
            total = dict()

            # Sort the standby types
            sby_keys = sorted(data[category].keys())
            for sby in sby_keys:
                if sby == "Total RL":
                    currentFont = Font(weight=BOLD)
                else:
                    currentFont = Font(weight=None)
                standbys.append(sby)
                currentRow = Row()
                currentRow.add(Text(sby, font=Font(weight=BOLD), border=border(right=0)))
                sum = 0
                for date in dates:
                    tmp = data[category][sby].get(date, 0)
                    if sby.find("Total") < 0:
                        total[date] = total.get(date, 0) + tmp
                    currentRow.add(Text(tmp, align=RIGHT, font=currentFont))
                    sum += tmp
                currentRow.add(Text(sum, font=Font(weight=BOLD), align=RIGHT, border=border(left=0)))
                # dataBox.add(currentRow)
                self.add(currentRow)
                self.page0()
            # categoryBox.add(Row(self.getTableHeader(standbys, vertical=True), dataBox))
            # categoryBox.add(self.sumRow(total, dates))
            self.add(self.sumRow(total, dates))
            # self.add(Row(categoryBox))
            self.add(Row(" "))
            self.page()

    def presentData(self, data, dates, objectReport, generalReport, show_RL):
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)
        # The old design with a big category box doesn't work for reports with lots of data since
        # explicit page breaks can't be added.
        if objectReport:
            # objectReport data is a list of data items with [crewString, data]
            for crew_data in data:
                self.add(Row(Text(crew_data[0], font=self.HEADERFONT)))
                if crew_data[1]:
                    self.presentDataSub(crew_data[1], dates, objectReport, generalReport, show_RL)
                else:
                    self.add(Row('No standbys'))
                    self.add(Row(' '))
                    self.page()
        else:
            self.presentDataSub(data, dates, objectReport, generalReport, show_RL)

    def presentDataSub(self, data, dates, objectReport, generalReport, show_RL):
        if show_RL:
            for rank in RanksInUse:
                for base in BasesInUse:
                    self.presentRankBaseData(rank, base, data, dates, objectReport, generalReport)
        else:
            for base in BasesInUse:
                for rank in RanksInUse:
                    self.presentRankBaseData(rank, base, data, dates, objectReport, generalReport)
        
        
        
    
            
    def create(self, reportType, context='default_context'):
        self.context = context
        self.modify_pp()
        objectReport = (reportType == "object")
        pp_start,pp_end,show_RL = R.eval('fundamental.%pp_start%','fundamental.%pp_end%', 'report_common.%report_show_RL%')
        generalReport = not objectReport
        data = self.getData(show_RL, objectReport)
        # Basic setup
        dates = self.getDates(pp_start,pp_end)

        # AS and AH are counted as one in this report
        
        if data:
            self.presentData(data, dates, objectReport, generalReport, show_RL)
        else:
            self.add("No standbys")
        self.reset_pp()

# End of file
