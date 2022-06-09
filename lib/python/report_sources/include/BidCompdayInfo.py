"""
 $Header$
 
 Bid Compday Info

 Lists the compday bids for each crew in pp.
  
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
CONTEXT = 'marked_in_window_left'
TITLE = 'Bid Compday Info'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

class BidCompdayInfo(SASReport):
    
    def create(self, reportType):
        # Basic setup
        SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)
            
        roster_expr = R.foreach(
            R.iter('iterators.roster_set',
                   where=('fundamental.%is_roster%','compdays.%crew_has_bid_in_pp%')),
            'report_common.%crew_string%',
            R.foreach(
            R.times('bid.%crew_num_bids%', where='compdays.%bid_is_compday_in_pp_ix%'),
            'compdays.%compdaytype_ix%',
            'compdays.%start_time_ix%',
            'compdays.%end_time_ix%',
            'compdays.%bid_nr_days_ix%',
            'compdays.%bid_granted_ix%',
            ))
        
        rosters, = R.eval(CONTEXT, roster_expr)

        if len(rosters) == 0:
            self.add("No crew with compday bids in selection")
            return
        crewWidth = 330
        typeWidth = 50
        dateWidth = 110
        grantedWidth = 80
        header = self.getDefaultHeader()
        header.add(self.getTableHeader(('Crew','Type','Bid period','Granted'), widths=(crewWidth,typeWidth,dateWidth,grantedWidth)))
        self.setHeader(header)
                
        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        for (ix, crewString, bids) in rosters:
            crewRow = Row(border=border(bottom=0))
            crewRow.add(Column(Text(crewString), width=crewWidth))
            typeColumn = Column(width=typeWidth)
            dateColumn = Column(width=dateWidth)
            grantedColumn = Column(width=grantedWidth)
            for (jx, compdaytype, starttime, endtime, days, granted) in bids:
                startday = AbsDate(starttime)
                endday = AbsDate(endtime)
                typeColumn.add(compdaytype)
                if (startday == endday):
                    dateText = str(startday)
                else:
                    dateText = str(startday)+"-"+str(endday)
                dateColumn.add(dateText)
                if granted:
                    grantedColumn.add('Yes')
                else:
                    grantedColumn.add('No')
            # This is done to get some space before next crew
            typeColumn.add(" ")
            crewRow.add(typeColumn)
            crewRow.add(dateColumn)
            crewRow.add(grantedColumn)
            self.add(crewRow)
            self.page0()
         
# End of file
