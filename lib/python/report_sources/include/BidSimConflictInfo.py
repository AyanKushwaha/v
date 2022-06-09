"""
 $Header$
 
 Bid Sim Conflict Info

 Lists bids that have time off bids that could not be granted due to
 simulator duties
  
 Created:    April 2007
 By:         Jonas Carlsson, Jeppesen

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
TITLE = 'Bid Sim Conflict Info'

class BidSimConflictInfo(SASReport):
    
    def create(self, report_type):
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)

        # Get the non-general off bids that are violated by the trip
        bid_expr = R.foreach(
            R.times('bid.crew_num_bids',
                    where=('bid.%is_not_general%(fundamental.%py_index%)',
                           'bid.%is_violated_valid_off_bid%(fundamental.%py_index%)',
                           'bid.%get_trip_is_violating%(fundamental.%py_index%)')),
            'bid.%abs1%(fundamental.%py_index%, 0)',
            'bid.%abs2%(fundamental.%py_index%, 0)',
            'bid.%abs2%(fundamental.%py_index%, 0) - 0:01',
            'time_of_day(bid.%abs1%(fundamental.%py_index%, 0)) = 0:00',
            'time_of_day(bid.%abs2%(fundamental.%py_index%, 0)) = 0:00',
            'bid.%description%(bid.%type%(fundamental.%py_index%, 0))',
            )

        # Get the training trips that violates any bid
        trip_expr = R.foreach(
            R.iter('iterators.trip_set', where = ('trip.in_pp',
                                                  'report_common.trip_is_training',
                                                  'bid.trip_violates_any')),
            'report_common.trip_recurrent_type',
            'crg_date.%print_date%(trip.%start_day%)',
            bid_expr
            )

        # Get the rosters that have any violated off bid
        roster_expr = R.foreach(
            R.iter('iterators.roster_set',
                   where='bid.any_valid_off_bid_violated'),
            'report_common.crew_string_variant_1',
            trip_expr
            )

        # Evaluate rave expression
        rosters, = R.eval(CONTEXT, roster_expr)

        # Table header
        self.add(self.getTableHeader(('Crew','Recurrent type', 'Recurrent date','Bid type', 'Bid period')))
        
        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        for (ix, crew_string, trips) in rosters:
            training_column = Column()
            training_row = None
            for(ix, trip_group, trip_start_day, bids) in trips:
                for (ix, start, end, end_rev, midnight_start, midnight_end, descr) in bids:
                    startday = AbsDate(start)
                    endday = AbsDate(end_rev)
                    if (startday == endday):
                        dateText = "%s" % startday
                    else:
                        start_1 = "%s" % start
                        end_1   = "%s" % end
                        if midnight_start:
                            start_1 = "%s" % startday
                        if midnight_end:
                            end_1   = "%s" % endday
                            
                        dateText = "%s - %s" % (start_1, end_1)
                        
                    training_row = Row(trip_group,
                                       str(trip_start_day),
                                       descr,
                                       "%s" % dateText)
                    training_column.add(training_row)
                    
            if training_row:
                crew_row = Row(Column(crew_string))
                crew_row.add(training_column)
                self.add(crew_row)
                self.page0()

            
         
# End of file
