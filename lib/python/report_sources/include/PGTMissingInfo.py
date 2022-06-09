"""
 $Header$
 
 PGT Missing Info

 
 
 Created:    August 2007
 By:         Anna Olsson, Jeppesen


Scope: All crew
Layout idea:

TABLE 1:
Missing registration

TABLE 2:
Previous year(s)

TABLE 3:
This year

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
import carmensystems.publisher.api as p
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime
import Cui

# constants =============================================================={{{1
CONTEXT = 'sp_crew'
TITLE = 'PGT Missing Info'


class PGTMissingRow(p.Row):

    def __init__(self, crew_str, expiry_date, note):
        p.Row.__init__(self,
                       p.Column(crew_str),
                       p.Column(expiry_date),
                       p.Column(note))
        self._cmp_item = expiry_date

    def __cmp__(self, row2):
        item1 = self.cmp_item
        item2 = row2.cmp_item
        try:
            item1 = AbsDate("01"+item1) # Format from Rave is Mon-Year, need day
            item2 = AbsDate("01"+item2)
        except:
            pass
        return cmp(item1,item2)

    @property
    def cmp_item(self):
        return self._cmp_item

class PGTMissingColumns:
    def __init__(self, parent, title_text, nr_rows_on_page):
        self._nr_rows_on_page = nr_rows_on_page
        self._height = 0
        self._parent = parent
        self._title = title_text
        self._rows = []
        
    def add_row(self, crew_str, expiry_date, note):
        self._rows.append(PGTMissingRow(crew_str, expiry_date, note))
        
    def create_header(self, column):
        column.add(p.Row(p.Text(""),height=8, border=p.border(top=1)))
        column.add(p.Text(self._title, font=p.font(weight=p.BOLD)))
        column.add(self._parent.getTableHeader(('Crew', 'Expiry date', 'Code last performed')))
        return 3 # nr of rows
    
    def create(self, current_height=0):
        """
        Adds rows to report and handles page breaks based on current height and given
        nr row per page
        """
        self._rows.sort()
        self._height = current_height
        current_col = p.Column(width=self._parent.pageWidth)
        self._height += self.create_header(current_col) #Header text + label
        for row in self._rows:
            current_col.add(row)
            self._height += 1
            if self._height > self._nr_rows_on_page:
                self._parent.add(current_col)
                self._parent.page0()
                current_col = p.Column(width=self._parent.pageWidth)
                self._height = self.create_header(current_col) #Header text + label, init height
        self._parent.add(current_col)
        return self._height
      
class PGTMissingInfo(SASReport):
    
    def create(self, report_type):
        # Basic setup
        SASReport.create(self, TITLE, orientation=p.PORTRAIT, usePlanningPeriod=True)
        
        where_expr = 'report_ccr.%pgt_required%'
        # Get the rosters for crew that needs pgt
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where=where_expr),
            'crew.%rank%',
            'report_ccr.%pgt_missing_current_year%',
            'report_ccr.%pgt_missing_previous_year%' ,
            'report_ccr.%pgt_missing_registration%',
            'report_common.%crew_string_variant_2%',
            'report_ccr.%pgt_exp_date_show%',
            'report_ccr.%pgt_last_performed_code%')
            
        # Evaluate rave expression
        rosters, = R.eval(CONTEXT, roster_expr)

        # Create report
        missing_reg_col = PGTMissingColumns(self, 'Missing PGT Registration', 60)
        missing_prev_col = PGTMissingColumns(self, 'PGT expiry previous year(s)', 60)
        missing_curr_col = PGTMissingColumns(self, 'PGT expiry current year', 60)
        # Print RAVE data in columns
        for (ix, rank, missing_current, missing_prev, missing_reg,
             crew_string1, exp_date1, note) in rosters:
            # only ranks used by SAS
            if rank not in self.SAS_RANKS:
                continue
            if missing_current:
                missing_curr_col.add_row(crew_string1, exp_date1, note)
            elif missing_prev:
                missing_prev_col.add_row(crew_string1, exp_date1, note)
            elif missing_reg:
                missing_reg_col.add_row(crew_string1, exp_date1, note)

        new_height = missing_reg_col.create(current_height=0)
        new_height = missing_prev_col.create(current_height=new_height)
        new_height = missing_curr_col.create(current_height=new_height)

            
                 
# End of file
