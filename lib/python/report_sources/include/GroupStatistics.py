"""
 $Header$
 
 Group Statistics

 Lists how many crew are in each contract group at the beginning of the period
  
 Created:    March 2007
 By:         Jonas Carlsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import OutputReport
from AbsDate import AbsDate
from RelTime import RelTime

# constants =============================================================={{{1
TITLE = 'Group Statistics'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

class GroupStatistics(SASReport):

    def create(self, reportType, context='default_context'):
        outputReport = (reportType == "output")
        # Basic setup
        SASReport.create(self, TITLE, usePlanningPeriod=True)

        # Loop over crew, get pattern
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='fundamental.%is_roster%'),
            'report_common.%in_variable_group_pp_start%',
            'report_common.%pattern_pp_start%',
            'report_common.%cycle_start_day_pp_start%',
            'report_common.%part_time_factor_pp_start%'
            )
        
        rosters, = R.eval(context, roster_expr)

        pt = set()
        group = set()
        patterns = set()
        data = dict()
        # Loop over all the 'bags' that comes from the RAVE expression
        # and collect the data
        for (ix, vg, pattern, cycle_start, pt_factor) in rosters:
            key = ""
            if vg:
                key = "VG"
            else:
                key = "%s - %2i" % (pattern, cycle_start)

            pt.add(pt_factor)
            group.add(key)
            if not vg: patterns.add(pattern)

            data[key] = data.get(key, dict())
            data["Total"] = data.get("Total", dict())
            data[key]["Total"] = data[key].get("Total", 0) + 1
            data[key][pt_factor] = data[key].get(pt_factor, 0) + 1
            data["Total"][pt_factor] = data["Total"].get(pt_factor, 0) + 1
            data["Total"]["Total"] = data["Total"].get("Total", 0) + 1

            
        sorted_pt = sorted(pt, reverse=True)
        sorted_group = sorted(group)

        # Main column
        pad = 200
        colw = 30
        group_col = Column()#width=0.5*self.pageWidth)
        pattern_col = Column()#width=0.5*self.pageWidth)
        
        # Header row
        th = ["Group"]
        for spt in sorted_pt:
            th.append("%s%%" % spt)
        th.append("Total")
        outputRows = [";".join(th)]
        t_row = Row("Groups:", font=Font(size=9, style=ITALIC, weight=BOLD))

        nr_cols = len(th)+2
        right_col = Column(width = self.pageWidth-nr_cols*colw)
        group_col.add(Column(t_row, Row(self.getTableHeader(th, widths=[colw for i in range(len(th)+2)]), right_col)))
        
        # Group/pt + group total
        for sgr in sorted_group:
            row = Row(Text(sgr))
            outputRows.append(sgr)
            for spt in sorted_pt:
                i = "%i" % data[sgr].get(spt, 0)
                row.add(Text(i))
                outputRows[-1] += ";%s" % i
            i = "%i" % data[sgr].get("Total", 0)
            row.add(Text(i))
            outputRows[-1] += ";%s" % i
            group_col.add(row)


        # PT total
        row = Row(Column(Text("Total"), font=Font(weight=BOLD)))
        outputRows.append("Total")
        for spt in sorted_pt:
            i = "%i" % data["Total"].get(spt, 0)
            row.add(Text(i))
            outputRows[-1] += ";%s" % i
        i = "%i" % data["Total"].get("Total", 0)
        row.add(Text(i))
        outputRows[-1] += ";%s" % i
        group_col.add(row)

 
        # Patterns
        t_row = Row("Patterns:", font=Font(size=9, style=ITALIC, weight=BOLD))
        pattern_col.add(Column(Text(""),
                               t_row,
                               self.getTableHeader(["Id", "Pattern"])))
        outputRows += ["", "Patterns:", "Id;Pattern"]

        sorted_patterns = sorted(patterns)
        for pattern in sorted_patterns:
            # Create the pattern string
            pattern_length, = R.eval('current_context', 'report_common.%%pattern_no_days%%(%s)' % pattern)
            if pattern_length:
                # Pattern was found
                pattern_expr = R.foreach(R.times(pattern_length),
                                         'crew.%%pattern_daytype%%(%s, fundamental.%%py_index%%)' % pattern,
                                         'crew.%%pattern_act_start%%(%s, fundamental.%%py_index%%)' % pattern,
                                         'crew.%%pattern_act_end%%(%s, fundamental.%%py_index%%)' % pattern)
                                         
                
                pattern_daytypes, = R.eval('current_context', pattern_expr)

                pattern_str = ""
                next_pos = 1
                for (ix, dt, _as, ae) in pattern_daytypes:
                    if _as == next_pos:
                        next_pos = ae + 1
                        pattern_str = "%s %i" % (pattern_str, next_pos - _as)
                    
                pattern_col.add(Row(pattern, pattern_str))
                outputRows.append("%s;%s" % (pattern, pattern_str))
            else:
                pattern_col.add(Row(pattern, "No data!"))
                outputRows.append("No data!")

        # Put it together
        if outputReport:
            self.set(font=Font(size=14))
            csvObject = OutputReport(TITLE, self, outputRows)
            self.add(csvObject.getInfo())
        else:
            self.add(group_col)
            self.add(Isolate(pattern_col))

            
            
# End of file
