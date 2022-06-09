"""
 $Header$
 
 PGT Distribution

 Lists all PGT activities in the planning period, and the number of crew assigned to them.
   
 Created:    August 2007
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime
import Errlog
# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'PGT Distribution'

base_map={"1":"STO", "2":"CPH", "3":"OSL"}

class PGTDistribution(SASReport):

    def get_day_header(self, date):
        tmp_date, = R.eval('crg_date.%%print_day_month%%(%s)' % date)
        return Text(tmp_date,align=RIGHT)
        
    def create(self):
        # Basic setup
        self.modify_pp()
        SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)

        # Get Planning Period start and end
        pp_start,pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')

        date = pp_start
        dates = []
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)
        
        trip_expr = R.foreach(
            R.iter('iterators.trip_set', where=('trip.%is_pgt%', 'trip.%starts_in_pp%', 'not training.%trip_is_pgt_ref%')),
            'training.%pgt_trip_start_day%',
            'training.%trip_pgt_code_compact%',
            'training.%trip_pgt_code_ext%',
            'training.%trip_pgt_code_full%',
            'training.%min_crew_on_pgt%',
            'training.%max_crew_on_pgt%',
            'training.%max_crew_on_pgt_with_qual%',
            'training.%trip_pgt_qual%',
            )
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='fundamental.%is_roster%'),
            'crew.%id%',
            'crew.%ac_family_by_qual%',
            trip_expr,
            )
        rosters, = R.eval(CONTEXT, roster_expr)

        data = dict()
        data_full_max = dict()
        used_dates = dict()
        ac_familys_by_code = dict()
        max_per_ext = dict()
        used_full_codes = dict()

        for (ix, crew_id, ac_fam, trips) in rosters:
            for (jx, day, pgt_code_compact, pgt_code_ext, pgt_code_full,
                 min_crew_ext, max_crew_ext, max_crew_full, pgt_ac_qual) in trips:
                # Get base via first digit in code
                for el in pgt_code_ext:
                    if el.isdigit():
                        pgt_code = base_map.get(el,None)
                        break
                else:
                    pgt_code = None
                    
                if not pgt_code:
                    Errlog.log('PGTDistribution.py:: create: Unable to get pgt_code for'+\
                               ' crew id %s on trip starting %s'%(crew_id, day))
                    pgt_code = 'Unknown station'
                    
                used_dates[day] = True

                ac_familys_by_code[pgt_code] = ac_familys_by_code.get(pgt_code, dict())
                ac_familys_by_code[pgt_code][pgt_ac_qual] = True

                data[pgt_code] = data.get(pgt_code, dict())
                data[pgt_code][day] = data[pgt_code].get(day, dict())
                data[pgt_code][day][pgt_ac_qual] = data[pgt_code][day].get(pgt_ac_qual, 0)+1
                data[pgt_code][day]["min"] = min_crew_ext
                data[pgt_code][day]["max"] = max_crew_ext

                data_full_max[day] = data_full_max.get(day, dict())
                data_full_max[day][pgt_ac_qual] = max_crew_full
        
        pgt_codes_sorted = data.keys()
        pgt_codes_sorted.sort()

        page = Row()

        header_row = self.getCalendarHeaderRow()
        header_row.add(" ")
        for date in dates:
            if used_dates.get(date, False):
                header_row.add(self.get_day_header(date))
        self.add(header_row)

        for pgt_code in pgt_codes_sorted:
            pgt_box = Row(border=border(bottom=0))
            ac_familys_this_code = ac_familys_by_code[pgt_code].keys()
            ac_familys_this_code.sort()

            # Creating the left column, displaying the ac familys for this code
            left_column = Column()
            left_column.add(Text("%-4s" % pgt_code, font=Font(weight=BOLD)))
            for ac_fam in ac_familys_this_code:
                left_column.add(Text("     %s" % ac_fam))
            left_column.add(Text("Total", font=Font(weight=BOLD)))
            left_column.add(Text("Min", font=Font(weight=BOLD)))
            left_column.add(Text("Max", font=Font(weight=BOLD)))
            pgt_box.add(left_column)

            # Creating the data area
            for date in dates:
                if used_dates.get(date, False):
                    day_column = Column()
                    day_column.add(" ")
                    if data[pgt_code].get(date,False):
                        this_data = data[pgt_code][date]
                        tot_assigned = 0
                        for ac_fam in ac_familys_this_code:
                            assigned_this_ac = this_data.get(ac_fam,0)
                            tot_assigned += assigned_this_ac
                            if assigned_this_ac > 0:
                                day_column.add(Text("%s (%s)" % (assigned_this_ac, data_full_max[date][ac_fam]), align=RIGHT))
                            else:
                                day_column.add(" ")
                        if tot_assigned > 0:
                            if tot_assigned > this_data['max'] or tot_assigned < this_data['min']:
                                day_column.add(Text(tot_assigned, font=Font(weight=BOLD), align=RIGHT, background=self.HEADERBGCOLOUR))
                            else:
                                day_column.add(Text(tot_assigned, font=Font(weight=BOLD), align=RIGHT))
                            day_column.add(Text(this_data['min'], font=Font(weight=BOLD), align=RIGHT))
                            day_column.add(Text(this_data['max'], font=Font(weight=BOLD), align=RIGHT))
                    pgt_box.add(day_column)
            self.add(pgt_box)

        self.reset_pp()

def sumMax(data):
    sum = 0
    for f in data.values():
        sum += f
    return sum


# End of file
