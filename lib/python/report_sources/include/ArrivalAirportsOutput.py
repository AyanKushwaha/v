"""
 $Header$
 
 ArrivaL Airports Output

 Lists all arrival airports in an output file
 
 Created:    August 2007
 By:         Anna Olsson, Jeppesen

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.ReportUtils import OutputReport
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime
import Cui

# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'Arrival Airports'

class ArrivalAirportsOutput(SASReport):
    
    def create(self):
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)

        # Get start date and trips that are simulators 
        leg_expr = R.foreach(
            R.iter('iterators.end_station_set', sort_by = "leg.%end_station%"),
            'leg.%end_station%',
            'report_common.%long_airport_name%')
        
        # Evaluate rave expression
        airports, = R.eval(CONTEXT, leg_expr)

      
        #Create report
        csvRows = []

        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        for (ix, name, long_name) in airports:        
            csvRows.append(name +", " + long_name)
            
     
        self.set(font=Font(size=14))
        csvObject = OutputReport(TITLE, self, csvRows)
        self.add(csvObject.getInfo())
                       
# End of file
