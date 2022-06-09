"""
 $Header$
 
 Sim Assignment Distribution

 Contains the information about assigned
 recurrent training: PC,OPC,AST,ASF,PGT,RCRM
  
 Created:    June 2007
 By:         Peter, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime

# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'Sim Assignment Distribution'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

class SimAssignmentDistribution(SASReport):

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
        
        # Get the compdays in use
        #SimAssignInUse = "OPC","OPC3","OPC4","PC","PC3","PC4","AST","ASF","PGT","CRM","EMG"
        #"F0","F1","F3","F3S","F31","F35","F7S","BL1"
        
        #compdaysInUseRave = R.set('compdays.in_use').members()
        #compdaysInUse = []
        #for compday in compdaysInUseRave:
        #    compdaysInUse.append(compday)
        #compdaysInUse.append("BL1")
        basesInUse = []
        for base in self.SAS_BASES:
            basesInUse.append(base)
        basesInUse.append("Summary")
        
        # Ranks in use
        ranksInUse = "FC","FP","FR","AP","AS","AH","AA","-","Summary" 
        
        #print "building rave expression"
        duty_expr = R.foreach(
            R.iter('iterators.duty_set'),
            'trip.%starts_in_pp%',
            'duty.%start_day%',
            'trip.%code%',
            'duty.%is_recurrent_or_deadhead%',
            )

        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='fundamental.%is_roster%'),
            'report_common.%crew_string%',
            'report_common.%crew_rank%',
            'crew.%homebase%',
            duty_expr,
            )
        rosters, = R.eval(CONTEXT, roster_expr)

        data = dict()
        # Loop over all the 'bags' that comes from the RAVE expression
        # and collect the data
        for (ix,crewString,rank,base,duties) in rosters:
           for (ix,in_pp,date,code,recurrent) in duties:
               # Only do something if the current bag corresponds to a day
               # in the planning period and is a Sim recurrent training
               # if in_pp and recurrent training:
               if in_pp and recurrent:
                   data[base] = data.get(base,dict())
                   data["Summary"] = data.get("Summary",dict())
                   data[base][rank] = data[base].get(rank,dict())
                   data["Summary"][rank] = data["Summary"].get(rank, dict())
                   try:
                       data[base][rank][date] = data[base][rank].get(date,0) + 1
                       data["Summary"][rank][date] = data["Summary"][rank].get(date,0) + 1
                   except:
                       print "Error "+str(date) + " " + rank
        if objectReport:
            self.add(Row(Text(crewString, font=self.HEADERFONT)))
        if data:
            for base in basesInUse:
                rankBox = Column()
                if generalReport:
                    rankBox.add(Row(Text(base),font=self.HEADERFONT))
                rankBox.add(self.headerRow(dates))
                compdays = []
                dataBox = Column(border=border(left=0))
                total = dict()
                if ((base in data) and (generalReport or base != "Summary")):
                    for rank in ranksInUse:
                        if rank in data[base]:
                            print "Base2: "+str(base)
                            compdays.append(rank)
                            currentRow = Row()
                            sum = 0
                            for date in dates:
                                tmp = data[base][rank].get(date,0)
                                total[date] = total.get(date,0)+tmp
                                currentRow.add(Text(tmp,align=RIGHT))
                                sum += tmp
                            currentRow.add(Text(sum, font=Font(weight=BOLD), align=RIGHT, border=border(left=0)))
                            dataBox.add(currentRow)
                    rankBox.add(Row(
                        self.getTableHeader(compdays, vertical=True),
                        dataBox))
                    rankBox.add(self.sumRow(total,dates))
                    self.add(Row(rankBox))
                    self.add(Row(" "))
                    self.page0()
        else:
            self.add("No Sim Assignments")
            
        self.reset_pp()

# End of file
