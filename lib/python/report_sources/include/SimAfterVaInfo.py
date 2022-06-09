"""
 $Header$
 
 Sim After Vacation Info

 Lists crev that have too cloose between end of vacation and simulator training.
 
 Created:    July 2007
 By:         Anna Olsson, Jeppesen

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime
import Cui

# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'Sim After Vacation Info'

class SimAfterVaInfo(SASReport):
    
    def create(self, report_type):
        # Basic setup
        SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)

        # Get start date and trips that are simulators 
        trip_expr = R.foreach(
            R.iter('iterators.trip_set', where='report_ccr.%trip_is_sim_close_to_va%'),
            'report_ccr.%start_of_sim_close_to_va%',
            'report_ccr.%days_between_sim_and_va%')
        
        # Get the rosters that have simulator too close after vacation
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='report_ccr.%roster_has_sim_after_va%'),
            'report_common.crew_id',
            'report_common.crew_name',
            trip_expr) 
        
        # Evaluate rave expression
        rosters, = R.eval(CONTEXT, roster_expr)

        # Table header
        self.add(self.getTableHeader(('Crew Id','Crew Name','Date','Number of days', 'Informed')))
        
        # Loop over all the 'bags' that comes from the RAVE expression and collect the data        
        for (ix, crew_id, crew_name,list) in rosters:
            crew_column = Column()
            crew_row = None
            for(ix,start_date, num_days) in list:
                crew_row = Row(start_date, num_days)
                crew_column.add(crew_row)

            crew_row = Row(Column(crew_id),Column(crew_name))
            crew_row.add(crew_column)
            self.add(crew_row)
            self.page0()

                 
# End of file
