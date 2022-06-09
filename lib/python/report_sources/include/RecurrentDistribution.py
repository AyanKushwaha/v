"""
 $Header$
 
 Recurrent Distribution


 Created:    April 2007
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# Imports and constants
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
import report_sources.include.ReportUtils as ReportUtils
#import DataCollection
from RelTime import RelTime

TITLE = 'Recurrent Distribution'
SUM_CATEGORY = "All bases"

class RecurrentDistribution(SASReport):
    """
    The main class for the report.
    """
    
    def create(self):
        """
        The main function for generating the report.
        """
        self.modify_pp()
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)
        self.bases = self.SAS_BASES + (SUM_CATEGORY,)
        
        # Get Planning Period start and end and generate a list with the dates
        # in the planning period.
        pp_start,pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')
        pp_length = (pp_end - pp_start) / RelTime(24, 00)
        self.dates = []
        for day in range(pp_length):
            self.dates.append(pp_start + RelTime(24*day,0))

        ReportUtils.DataCollection.dates = self.dates
        ReportUtils.DataCollection.sumCategory = SUM_CATEGORY

        rec_codes_set = R.set('report_common.add_codes_rec_rep').members()
        
        add_where_clause = ""
        str_list = []
        for r_type in rec_codes_set:
            if len(str_list) > 0:
                str_list.append(" or ")
            else:
                str_list.append(" or (")
                
            is_asterisk = r_type.find("*") > -1
            r_t = r_type.rstrip("*")
            if is_asterisk:
                str_list.append("substr(leg.%%code%%, 1, %d) = \"%s\"" % (len(r_t), r_t))
            else:
                str_list.append("leg.%%code%% = \"%s\"" % r_t)
            
        if len(str_list) > 0:
            str_list.append(")")
            add_where_clause = "".join(str_list)
            
	    
        self.data = dict()
        
        rosterExpr = R.foreach(
            R.iter('iterators.roster_set', where='crew.%is_cabin%'),
                R.foreach(R.iter('iterators.leg_set', where=('leg.%%in_pp%% and (report_common.%%leg_is_rec%% %s)' % add_where_clause)),
                          'report_common.%rec_base%',
                          'report_common.%rec_start%',
                          'report_common.%rec_code%',
                          )
            )
        
        rosters, = R.eval('default_context',rosterExpr)
        
        for (ix, trips) in rosters:
            
            for (kx, base, date, code) in trips:
		
                if not base in self.bases:
                    print "Base not in SAS bases: %s" %base
                # Get a link to the appropriate data structure to reduce typing.
                if (not base in self.data):
                    # If it doesn't exist we create it
                    self.data[base] = ReportUtils.DataCollection(base)
                dt = self.data[base]
                    
               # for day in range(days):
                    # For all days in the trip we add it to the appropriate
                    # category.
                    #date = startDate + RelTime(24*day,0)
                dt.inc(code, date)

                # End of trip loop
                            
            # End of crew loop
                                           

        # Counter to control inclusion of "All bases" section.
        counter = 0
        
        # We loop over bases instead of over keys in the data to control the
        # order of the sections.
        for base in self.bases:
            if base in self.data:
                dt = self.data[base]
                counter += 1
                # When the counter hits 2 (i.e. more than one base in the data)
                # we generate the sum.
                if (counter == 2):
                    ReportUtils.sumDataCollections(SUM_CATEGORY, self.data)

                baseBox = Column()
                baseBox.add(Row(Text(base, font=self.HEADERFONT)))
                self.dataBox = Column(self.getCalendarRow(
                    self.dates,leftHeader=' ',rightHeader='Sum'))

                self.buildBox(base)
                baseBox.add(Row(self.dataBox))
                self.add(Row(baseBox))
                self.page0()
                
        self.reset_pp()


    def buildBox(self, base):
        """
        A function to build a box with the appropriate data rows.
        """
        # We create a link to the data to reduce typing
        dt = self.data[base]
        # Get the keys in the data and sort them.
        keys = dt.keys()
        keys.sort()
        sum = dict()

        for key in keys:
            monthSum = 0
            items = []
            for date in self.dates:
                val = dt.get(key, date)
                items.append(val)
                sum[date] = sum.get(date,0) + val
                monthSum += val
            dataRow = self.dataRow(key, items)
            dataRow.add(Text(monthSum, align=RIGHT))
            self.dataBox.add(dataRow)

        totalSum = 0
        items = []
        for date in self.dates:
            items.append(sum[date])
            totalSum += sum[date]
        sumRow = self.dataRow("Total", items)
        sumRow.add(Text(totalSum, align=RIGHT, font=Font(weight=BOLD)))
        sumRow.set(border=border(top=0))
        self.dataBox.add(sumRow)

    def dataRow(self, header, items):
        """
        Generates a row in the appropriate format.
        """
        
        output = Row(border=border(bottom=0))
        output.add(Text(header,
                        font=Font(weight=BOLD),
                        border=border(right=0)))
        if (header == "Total"):
            itemFont = Font(weight=BOLD)
        else:
            itemFont = None
        for item in items:
            if (item == 0):
                item = " "
            output.add(Text(item, align=RIGHT, font=itemFont, border=border(right=0)))
        return output
    
# End of file
