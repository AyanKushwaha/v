"""
 $Header$
 
 Freedays Info

 Lists the freeday balance for each crew
  
 Created:    December 2006
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

import csv
import carmensystems.rave.api as R
import os
import Tkinter, tkFileDialog    # Tk is used for displaying "Save as..." dialog for CSV
from datetime import datetime
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport

TITLE = 'Freedays Info'
CSV_DIR = "/samba-share/reports/FreedaysInfo"

headerItems = ('Name','Empno','Rank','Part time','Assigned','Required','Balance')
cellWidths = (172,50,30,50,90,50,50)
cellAligns = (LEFT,LEFT,LEFT,RIGHT,RIGHT,RIGHT,RIGHT)
ranksInUse = ("FC","FP","FR","AP","AS/AH","Other")
groupedRanks = "AS","AH"

def rankConvert(rank):
    if rank in groupedRanks:
        rank = "AS/AH"
    return rank

class FreedaysInfo(SASReport):
    class Category:
        def __init__(self):
            self.rows = []

        def add_crew(self, *args):
            self.rows.append(args)

    def boxed_row(self, row):
        result = Row()
        for (cell_value, cell_align) in zip(row, cellAligns):
            result.add(Text(cell_value, align=cell_align))
        return result

    def boxed_table_header(self):
        """Returns boxed header row"""
        
        def htext_l(*args, **kwargs):
            """Text for header row aligned left"""
            kwargs['align'] = LEFT
            kwargs['padding'] = padding(2, 2, 2, 2)
            return Text(*args, **kwargs)

        def htext_r(*args, **kwargs):
            """Text for header row aligned right"""
            kwargs['align'] = RIGHT
            kwargs['padding'] = padding(2, 2, 2, 2)
            return Text(*args, **kwargs)

        return Row(htext_l(headerItems[0], width=cellWidths[0]),
            htext_l(headerItems[1], width=cellWidths[1]),
            htext_l(headerItems[2], width=cellWidths[2]),
            htext_r(headerItems[3], width=cellWidths[3]),
            htext_r(headerItems[4], width=cellWidths[4]),
            htext_r(headerItems[5], width=cellWidths[5]),
            htext_r(headerItems[6], width=cellWidths[6]),
            font=self.HEADERFONT,
            background=self.HEADERBGCOLOUR)

    def create(self, reportType, context='default_context'):
        # Basic setup
        SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)
        write_copy_to_csv = True

        if write_copy_to_csv:
            timestamp = datetime.now()
            crew_planning_group, = R.eval('planning_area.%pa_item%("crew", 1)')
            crew_category, = R.eval('planning_area.%pa_item%("crew", 3)')
            try:
                csv_filename = ''
                if not os.path.isdir(CSV_DIR):
                    os.makedirs(CSV_DIR)
                # display Tk "Save as..." dialog
                tk_root = Tkinter.Tk()
                tk_root.withdraw()          # hides Tk main window
                saveas_dlg_options = {}
                saveas_dlg_options["defaultextension"] = ".csv"
                saveas_dlg_options["filetypes"] = [("CSV files", ".csv"), ("All files", ".*")]
                saveas_dlg_options["initialdir"] = CSV_DIR
                saveas_dlg_options["initialfile"] = "%s_%s_FreedaysInfo_%s_%s_%s.csv" % (crew_category, crew_planning_group, str(timestamp.year), str(timestamp.month).zfill(2), str(timestamp.day).zfill(2))
                saveas_dlg_options["title"] = "Save as"
                saveas_dlg_options["parent"] = tk_root
                csv_filename = tkFileDialog.asksaveasfilename(**saveas_dlg_options)
                tk_root.destroy()
                csv_writer = csv.writer(open(csv_filename, "wb"), delimiter=";")
            except Exception as e:
                print "Error opening CSV file: %s: %s" % (str(csv_filename), str(e))
                write_copy_to_csv = False

        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where=('fundamental.%is_roster%', 'crew.%has_some_variable_group_in_publ%')),
            'report_common.%crew_surname%',
            'report_common.%crew_firstname%',
            'report_common.%employee_number%',
            'report_common.%crew_rank%',
            'report_common.%crew_homebase%',
            'crew.%part_time_factor%',
            'report_common.%freedays_balance%',
            'report_common.%freedays_in_month%',
            'report_common.%req_freedays_in_month%',
            )

        rosters, = R.eval(context, roster_expr)
                
        categories = {}
        for (ix, surname, firstname, empno, rank, base, part_time, balance, freedays, req_freedays) in rosters:
            rank_group = rankConvert(rank)
            if (rank_group not in ranksInUse):
                rank = "Other"
            categories[base] = categories.get(base, self.Category())
            if (balance != 0):
                if not (freedays == 0):
                    if not freedays:
                        freedays = "-"
                if not (req_freedays == 0):
                    if not req_freedays:
                        req_freedays = "-"
                name = surname + ", " + firstname
                part_time = str(part_time) + "%"
                # negative values in the balance column are changed to zero
                categories[base].add_crew(name, empno, rank, part_time, freedays, req_freedays, max(balance, 0))

        # build report
        if write_copy_to_csv:
            try:
                csv_row = ['Base']
                csv_row.extend(headerItems)
                csv_writer.writerow(csv_row)
            except Exception as e:
                print "Error writing CSV file %s: %s" % (str(csv_filename), str(e))
        first_page = True
        for base in self.SAS_BASES:
            if categories.get(base, False) and len(categories[base].rows) > 0:
                if first_page:
                    first_page = False
                else:
                    self.newpage()
                header = Column()
                header.add(Row(base, font=self.HEADERFONT))
                header.add(self.boxed_table_header())
                self.setHeader(header)
                for row in categories[base].rows:
                    self.add(self.boxed_row(row))
                    self.page0()
                    if write_copy_to_csv:
                        try:
                            csv_row = [base]
                            csv_row.extend(row)
                            csv_writer.writerow(csv_row)
                        except Exception as e:
                            print "Error writing CSV file %s: %s" % (str(csv_filename), str(e))

# End of file
