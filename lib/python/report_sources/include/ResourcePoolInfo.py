"""
 $Header$
 
 Resource Pool Info

 
  
 Created:    May 2007
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# Imports
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
import Cfh
import Cui


import utils.Names as Names
from tm import TM
from carmstd import cfhExtensions
from RelTime import RelTime
from AbsDate import AbsDate
from AbsTime import AbsTime
import os
import tempfile

# Constants
TITLE = 'Resource Pool Info'

class ResourcePoolInfo(SASReport):
        
    def extraHeader(self, base):
        headerRow = Row(font=self.HEADERFONT, background=self.HEADERBGCOLOUR)
        headerRow.add("Crew (%s)" %base)
        monthsRow = Row()
        for (ix, monthName) in self.monthNames:
            monthsRow.add(monthName)
        monthsRow.add("Total")
        headerRow.add(Column(Row("(Planned/Qualifying)"), monthsRow))
        return headerRow
    
    def create(self):
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)

        varPrefix = 'report_common.%skbu_resource_pool_'
        self.months, = R.eval("default_context", 'report_common.%skbu_resource_pool_months%')
        
        self.monthNames, = R.eval("default_context",
                                  R.foreach(R.times(self.months),
                                            'report_common.%skbu_resource_pool_month_str_ix%',
                                            )
                                  )
                
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='crew.%is_skbu_resource_pool%'),
            'report_common.%crew_string%',
            'report_common.%crew_homebase%',
            R.foreach(R.times(self.months),
                      'report_common.%skbu_resource_pool_planned_ix%',
                      'report_common.%skbu_resource_pool_qualifying_ix%',
                      )
            )
        
        rosters, = R.eval('default_context', roster_expr)
        baseBoxes = dict()
        pad = padding(2,10,2,0)
        for (ix, crewString, base, data) in rosters:
            if not base in baseBoxes:
                baseBoxes[base] = list()
            crewRow = Row(Text(crewString, padding=pad))
            plannedTotal = 0
            qualifyingTotal = 0
            for (jx, planned, qualifying) in data:
                plannedTotal += planned
                qualifyingTotal += qualifying
                crewRow.add(Text("%s/%s" %(planned, qualifying), padding=pad))
            crewRow.add(Text("%s/%s" %(plannedTotal, qualifyingTotal), font=Font(weight=BOLD), padding=pad))
            baseBoxes[base].append(crewRow)

        if len(rosters) == 0:
            self.add("No resoucre pool crew in plan")

        for base in baseBoxes:
            counter = 0
            for row in baseBoxes[base]:
                if (counter % 25 == 0):
                    self.page0()
                    self.add(self.extraHeader(base))
                self.add(row)
                counter += 1
            self.page0()
            

def runReport():
    pp_start,pp_end, = R.eval('fundamental.%pp_start%', 'fundamental.%pp_end%')
    
    arg = "startDate=" + str(AbsDate(pp_start))
    arg += " endDate=" + str(AbsDate(pp_end))
    arg += " account=ALL"
    arg += " base=ALL"
    arg += " maincat=ALL"
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea,"plan","ResourcePoolInfo.py", 0, arg)            

# End of file
