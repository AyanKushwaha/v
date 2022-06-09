"""
 $Header$
 
 Balance Distribution

 Lists the various types of production and balance in pp.
  
 Created:    January 2007
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import OutputReport
from RelTime import RelTime

# constants
CONTEXT = 'default_context'
TITLE = 'Balance Distribution'

total_category = "Total"
ranks_in_use = ("FC","FP","FR","AP","AS/AH",total_category)

def rankConvert(rank):
    if rank in ("AS","AH"):
        rank = "AS/AH"
    return rank

class BalanceDistribution(SASReport):
    def headerRow(self, dates):
        tmpCsvRow = self.getCalendarRow(dates,leftHeader='-', csv=True)
        return tmpCsvRow

    def create(self, output = 'csv'):
        self.modify_pp()
        outputReport = (output == "csv")

        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE,
                         usePlanningPeriod=False)
        
        # Get Planning Period start and end
        pp_start,pp_end = R.eval('fundamental.%pp_start%',
                                 'fundamental.%publ_period_end%')
        date = pp_start
        dates = []
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)

        ranks = {}
        for i in range(10):
            pos = i+1
            ranks[pos], = R.eval('crew_pos.%%pos2func%%(%s)' % pos)

        groups = "FG","VG"

        ########################################################################
        #
        # Assigned production
        #
        ########################################################################
        assigned_expr = R.foreach(
            R.iter('iterators.roster_set',
                   where='fundamental.%is_roster%'),
            R.foreach(R.iter('iterators.trip_set',
                             where=('trip.%in_pp%','trip.%is_on_duty%')),
                      'trip.%is_blank_day%',
                      'trip.%start_day%',
                      'trip.%end_day%',
                      'trip.%crew_homebase%',
                      'crew.%in_fixed_group_trip_start%',
                      'crew.%rank_trip_start%',
                      )
            )

        assigned_trips, = R.eval(CONTEXT,assigned_expr)

        assigned_prod = dict()
        blank_days = dict()
        
        for (ix, trips) in assigned_trips:
            for (jx, bl, start_day, end_day, base, fg, rank) in trips:
                rank = rankConvert(rank)
                category = rank+"-"+base
                if fg:
                    group = "FG"
                else:
                    group = "VG"
                    
                if bl:
                    data = blank_days
                else:
                    data = assigned_prod
                    
                for cat in category, total_category:
                    data[cat] = data.get(cat,dict())
                    data[cat][group] = data[cat].get(group,dict())
                    
                    date = start_day
                    while (date <= end_day):
                        data[cat][group][date] = data[cat][group].get(date,0)+1
                        date += RelTime(24,0)

        
        ########################################################################
        #
        # Remaining production
        #
        ########################################################################
        remaining_expr = R.foreach(
            R.iter('iterators.trip_set',
                   where=('report_ccr.%unassigned_trip_to_be_counted%',
                          'trip.%in_pp%',
                          'not trip.%is_blank_day%',
                          )
                   ),
            'trip.%start_day%',
            'trip.%end_day%',
            'trip.%homebase%',
            R.foreach(R.times(10),
                      'fundamental.%py_index%',
                      'crew_pos.%trip_assigned_pos%(fundamental.%py_index%)',
                      )
            )
        remaining_trips, = R.eval('sp_crrs',remaining_expr)

        remaining_prod = dict()

        data = remaining_prod
        
        for (ix, start_day, end_day, base, crew) in remaining_trips:
            debug_str = "Trip %s %s-%s " %(base, start_day, end_day)
            for (jx, pos, count) in crew:
                if (count > 0):
                    debug_str += "pos %s: %s " %(jx, count)
                    rank = rankConvert(ranks[pos])
                    category = rank+"-"+base

                    for cat in category, total_category:
                        data[cat] = data.get(cat,dict())

                        date = start_day
                        while (date <= end_day):
                            data[cat][date] = data[cat].get(date,0)+count
                            date += RelTime(24,0)
        csvRows = []

        # Build categories
        cats = []
        for base in self.SAS_BASES:
            for rank in ranks_in_use:
                cats.append(rank+"-"+base)
        cats.append(total_category)

        for category in cats:
            if ((category in assigned_prod) or
                (category in blank_days) or
                (category in remaining_prod)):
                    
                total_prod = "TotalProd"
                remaining = "RemProd"
                assigned_VG = "Assigned (VG)"
                assigned_FG = "Assigend (FG)"
                assigned_Tot = "Assigned Tot"
                blank_VG = "Blank (VG)"
                blank_FG = "Blank (FG)"
                blank_Tot = "Blank Tot"
                balance = "Balance"
                for date in dates:
                    # Assigned prod
                    ass_fg = get_data_item(assigned_prod, category, "FG", date)
                    ass_vg = get_data_item(assigned_prod, category, "VG", date)
                    assigned_VG += ";"+str(ass_vg)
                    assigned_FG += ";"+str(ass_fg)
                    assigned_Tot += ";"+str(ass_vg+ass_fg)
                    # Blank days
                    bl_fg = get_data_item(blank_days, category, "FG", date)
                    bl_vg = get_data_item(blank_days, category, "VG", date)
                    blank_VG += ";"+str(bl_vg)
                    blank_FG += ";"+str(bl_fg)
                    blank_Tot += ";"+str(bl_vg+bl_fg)
                    
                    # Remaining
                    rem = get_data_item(remaining_prod, category, date)
                    remaining += ";"+str(rem)
                    
                    # Total = assigned + remaining
                    total_prod += ";"+str(ass_vg+ass_fg+rem)
                    # Balance = blank - remaining
                    balance += ";"+str(bl_vg+bl_fg-rem)
                csvRows.append(category)
                csvRows.append(self.headerRow(dates))
                csvRows.append(total_prod)
                csvRows.append(assigned_Tot)
                csvRows.append(assigned_FG)
                csvRows.append(assigned_VG)
                csvRows.append(remaining)
                csvRows.append(blank_Tot)
                csvRows.append(blank_FG)
                csvRows.append(blank_VG)
                csvRows.append(balance)
                csvRows.append(" ")

        if outputReport:
            self.set(font=Font(size=14))
            csvObject = OutputReport(TITLE, self, csvRows)
            self.add(csvObject.getInfo())

        self.reset_pp()

def get_data_item(data, key1, key2, key3=None):
    try:
        if key3:
            output = data[key1][key2][key3]
        else:
            output = data[key1][key2]
    except:
        output = 0
    return output

# End of file
