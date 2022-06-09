"""
 $Header$
 
 Pattern Conflict Info

 Displays conflicts between contractual and actual freeday-pattern
 for crew in fixed group
  
 Created:    March 2007
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime

# constants =============================================================={{{1
TITLE = 'Pattern Conflict Info'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8
DEF_COL = "#ffffff"
PROD_COL = "#cdcdcd"
CONFLICT_COL = "#aaaaaa"

class PatternConflictInfo(SASReport):

    def getCalendarRow(self, dates):
        dates_str = []
        for date in dates:
            tmp_date, = R.eval('crg_date.%%print_day_month%%(%s)' % date)
            dates_str.append(tmp_date)
        tmpRow = Row(font=Font(size=6, weight=BOLD), border=None, background=self.HEADERBGCOLOUR)
        tmpRow.add(Text("Pattern"))
        for date in dates_str:
            tmpRow.add(Text(date))
        return tmpRow

    def create(self, context='default_context'):
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)
        
        # Get Planning Period start and end
        pp_start,pp_end,pp_days = R.eval('fundamental.%pp_start%','fundamental.%pp_end%','pp.%days%')
        date = pp_start
        dates = []
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)
        
        #print "building rave expression"
        trip_expr = R.foreach(
            R.iter('iterators.trip_set', where='trip.%in_pp%'),
            'trip.%start_day%',
            'trip.%end_day%',
            'trip.%days%',
            'trip.%code%',
            'trip.%is_on_duty%',
            'trip.%is_pt_freeday%',
            'trip.%is_freeday%',
            'trip.%is_vacation% or trip.%is_illness%',
            )
        pattern_expr = R.foreach(
            R.times(pp_days),
            'report_common.%date_ix%',
            'report_common.%crew_pattern_daytype_ix%',
            )
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where=('fundamental.%is_roster%','crew.%has_some_fixed_group_in_pp%')),
            'report_common.%employee_number%',
            'report_common.%crew_string%',
            'report_common.%crew_rank%',
            'report_common.%crew_homebase%',
            pattern_expr,
            trip_expr,
            )
        rosters, = R.eval(context, roster_expr)

        data = dict()
        empnosAtBase = dict()
        # Loop over all the 'bags' that comes from the RAVE expression
        # and collect the data
        for (ix, empno, crewString, rank, base, pattern, trips) in rosters:
            if not (base in self.SAS_BASES):
                print "Strange base: "+str(base)+", CHECK THIS!"
                base = "Other"
            crewHasConflict = False
            data[base] = data.get(base,dict())
            data[base][empno] = dict()
            data[base][empno]["Contract"] = dict()
            data[base][empno]["Actual"] = dict()
            data[base][empno]["Conflict"] = dict()
            data[base][empno]["CrewInfo"] = crewString
            for (ix, day, patternCode) in pattern:
                
                data[base][empno]["Contract"][day] = patternCode or "-" 
                data[base][empno]["Actual"][day] = ""
                data[base][empno]["Conflict"][day] = False
            for (ix, start_day, end_day, days, code, on_duty,
                 pt_freeday, freeday, no_conflict) in trips:
                for day in range(days):
                    date = start_day+RelTime(day*24,0)
                    try:
                        contract = data[base][empno]["Contract"][date]

                        data[base][empno]["Actual"][date] = code
                        if contract == "-":
                            continue
                        elif no_conflict:
                            data[base][empno]["Conflict"][date] = False
                        elif pt_freeday:
                            data[base][empno]["Conflict"][date] = (contract != "D")
                        elif freeday:
                            data[base][empno]["Conflict"][date] = (contract != "F")
                        elif (contract != "P" and contract != "X"):
                            data[base][empno]["Conflict"][date] = True
                        crewHasConflict = (crewHasConflict or data[base][empno]["Conflict"][date])
                    except:
                        #date was out of range
                        pass
            if crewHasConflict:
                empnosAtBase[base] = empnosAtBase.get(base,[])
                empnosAtBase[base].append(empno)
                print 'has_conflict',empnosAtBase
        
        dataExists = False
        if data:
            for base in self.SAS_BASES:
                if base in empnosAtBase:
                    dataExists = True
                    baseBox = Column()
                    header = self.getDefaultHeader()
                    header.add(Row(" "))
                    extraRow = Row()
                    extraRow.add(Text(base, font=self.HEADERFONT))
                    extraRow.add(Text(" ", width=20, background=PROD_COL))
                    extraRow.add(Text(": Production"))
                    extraRow.add(Text(" ", width=20, background=CONFLICT_COL))
                    extraRow.add(Text(": Conflict"))
                    extraRow.add(Text(" ", width=500))
                    header.add(extraRow)
                    header.add(Row(" "))
                    self.setHeader(header)
                    for empno in empnosAtBase[base]:
                        crewBox = Column()
                        crewBox.add(Row(Text(data[base][empno]["CrewInfo"], font=self.HEADERFONT)))
                        crewBox.add(self.getCalendarRow(dates))
                        contractRow = Row(border=border(bottom=1))
                        actualRow = Row(border=border(bottom=1))
                        contractRow.add(Text("Contract", font=Font(weight=BOLD), background=DEF_COL, border=border(right=1)))
                        actualRow.add(Text("Actual", font=Font(weight=BOLD), background=DEF_COL, border=border(right=1)))
                        for date in dates:
                            contract = data[base][empno]["Contract"][date]
                            contractBgColor = DEF_COL
                            if (contract == "P"):
                                contractBgColor = PROD_COL
                            contractRow.add(Text(contract, background=contractBgColor))#, border=border(right=1)))
                            actualBgColor = DEF_COL
                            if (data[base][empno]["Conflict"][date]):
                                actualBgColor = CONFLICT_COL
                            else:
                                actualBgColor = contractBgColor
                            actualRow.add(Text(data[base][empno]["Actual"][date], background=actualBgColor))#, border=border(right=1)))
                        crewBox.add(contractRow)
                        crewBox.add(actualRow)
                        crewBox.add(Row(" "))
                        baseBox.add(Row(crewBox))
                        baseBox.page0()
                    self.add(baseBox)
                    self.page0()
        if not dataExists:
            self.add("No conflicts")

# End of file
