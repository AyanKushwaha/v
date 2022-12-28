"""
 
 Mismatching A3/A4 LPC and OPC/OTS dates.
  
 Created:    June 2007
 By:         Peter Schulz, Jeppesen

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport

# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'Sim Mismatching LPC Dates Info'

cellWidths = (250,50,50,50,50,100)
#aligns = (LEFT,CENTER,CENTER,CENTER,CENTER,LEFT)

class SimMismatchingPCDatesInfo(SASReport):
        
    def extraHeader(self):
        headerItems = ('Crew','LPCA3','OPCA4','OTSA4','LPCA4','OPCA3','OTSA3','Notes')
        columnHeaders = Row(font=self.HEADERFONT, background=self.HEADERBGCOLOUR, border=None)
        items = zip(headerItems,cellWidths) #,aligns)
        for (item,itemwidth) in items:
            columnHeaders.add(Text(item, width=itemwidth, border=None, padding=padding(1,4,1,4)))
        return columnHeaders

    def create(self, reportType):
        SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)
            
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='report_ccr.%recurrent_type_mismatch_expiry_date%'),
            'report_common.%crew_string%',
            'report_ccr.%lpca3_month%',
            'report_ccr.%opca4_month%',
            'report_ccr.%otsa4_month%',
            'report_ccr.%lpca4_month%',
            'report_ccr.%opca3_month%',
            'report_ccr.%otsa3_month%'
            )
        rosters, = R.eval(CONTEXT, roster_expr)
                
        boxes = dict()
        
        header = self.getDefaultHeader()
        header.add(self.extraHeader())
        self.setHeader(header)        

        for (ix, crew_string, LPCA3, OPCA4, OTSA4, LPCA4, OPCA3,  OTSA3) in rosters:
            tmpRow = Row(border=None)
            textItems = (crew_string, LPCA3, OPCA4, OTSA4, LPCA4, OPCA3, OTSA3, '')
            items = zip(textItems, cellWidths) #, aligns)
            for (item, itemwidth) in items:
                tmpRow.add(Text(item, width=itemwidth, border=None, padding=padding(1,3,1,4)))
            self.add(tmpRow)

# End of file
