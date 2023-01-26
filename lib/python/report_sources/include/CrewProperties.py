"""
 $Header$
 
 Crew Properties

 ...
  
 Created:    March 2008
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport

# constants =============================================================={{{1
TITLE = 'Crew Properties'

class CrewProperties(SASReport):

    def hdr_row(self, header):
        if header:
            self.page.add(Row(Text(header, font = self.HEADERFONT)))

    def prop_row(self,prop_table,key):
        if key in prop_table:
            r = prop_table[key]
            row = Row()
            row.add(Text("%s: " % r[1], font=Font(weight=BOLD)))
            row.add(Text("%s "  % r[2]))
            self.page.add(Isolate(row))
            return True
        return False

    def prop_rows(self,prop_table,keys):
        ret = False
        for k in keys:
            if self.prop_row(prop_table,k):
                ret = True
        return ret
 
    def set_row(self,prop_table,keys):
        r = Row()
        ret = False
        for k in keys:
            if k in prop_table:
                r.add(Text("%s: " % prop_table[k][1], font=Font(weight=BOLD)))
                r.add(Text("%s "  % prop_table[k][2]))
                ret = True
        if ret: 
            self.page.add(Isolate(r))
        return ret

    def list_row(self, col, row):
        if row[1]:
            r = Row()
            for it in row[1:]:
                r.add(it)
            col.add(r)
            return True
        return False

    def multi_row(self,data): 
        r = Row()
        ret = False
        for (ix, item, val) in data:
            if item:
                r.add(Text("%s: " %item, font=Font(weight=BOLD)))
                r.add(Text("%s " %val))
                ret = True
        if ret:
            self.page.add(Isolate(r))
        return ret

    def prop_block_basic(self, header, prop_table):
        self.hdr_row(header)
        self.set_row(prop_table, ['Seniority','Homebase','Rank','Contract','Parttime factor'])
        self.prop_rows(prop_table, [8])
        self.page.add(Row(" "))

    def prop_block(self, header, prop_table,keys):
        self.hdr_row(header)
        ret = self.prop_rows(prop_table,keys)
        if not ret:
            self.page.add("No %s" % header)
        self.page.add(Row(" "))

    def list_block(self, header, data):
        self.hdr_row(header)
        col = Column()
        ret = False
        for row in data:
            # item 0 is iterator
            # item 1 is first data item, check if exist
            if self.list_row(col, row):
                ret = True
        if ret:
             self.page.add(Isolate(col))
        else:
             self.page.add("No %s" % header)
        self.page.add(Row(" "))

    def multi_block(self, header, data):
        self.hdr_row(header)
        if not self.multi_row(data):
            self.page.add("No %s" % header)
        self.page.add(Row(" "))

    def rec_block(self, data):
        self.page.add(Row(Text("Recurrent documents", font = self.HEADERFONT)))
        
        rec_order = ("LPC","LPCA3","LPCA4","LPCA5","LPCA3A5","OPC","OPCA3","OPCA4","OPCA5","OPCA3A5","OTS","OTSA3","OTSA4","OTSA5","OTSA3A5"
                     "PGT", "LC", "CRM",
                     "REC")
        info_row = Row()
        for doc in rec_order:
            for (ix, item, val) in data:
                if item == doc:
                    info_row.add(Text("%s: " %item, font=Font(weight=BOLD)))
                    info_row.add(Text("%s " %val))
        self.page.add(Isolate(info_row))
        self.page.add(Row(" "))
        
    def create(self, headers=False, context='default_context'):
        # Basic setup
        SASReport.create(self, TITLE, headers=headers, usePlanningPeriod=True)

        ctl_to_show = ("LPC", "OPC", "OTS", "CRM", "PGT", "LC", "ILC",
                       "REC", "REC CX", "AST", "ASF")
        basic_prop_expr = R.foreach(
            R.times('report_crew_properties.%basic_count%'),
            'report_crew_properties.%basic_name_ix%',
            'report_crew_properties.%basic_val_ix%'
            )
        recurrent_expr = R.foreach(
            R.times(10),
            'report_crew_properties.%rec_type_ix%',
            'report_crew_properties.%rec_type_expiry_ix%'
            )
        training_expr = R.foreach(
            R.times('report_crew_properties.%ctl_items%',
                    sort_by = '31dec2099-report_crew_properties.%ctl_time_ix%'),
            'report_crew_properties.%ctl_type_ix%',
            'report_crew_properties.%ctl_code_ix%',
            'report_crew_properties.%ctl_attr_ix%',
            'report_crew_properties.%ctl_time_str_ix%',
            )
        account_expr = R.foreach(
            R.times('report_crew_properties.%account_items%'),
            'report_crew_properties.%account_type_ix%',
            'report_crew_properties.%account_balance_ix%'
            )
        qual_expr = R.foreach(
            R.times('report_crew_properties.%qualification_items%'),
            'report_crew_properties.%qualification_desc_ix%',
            'report_crew_properties.%qualification_date_ix%'
            )
        restriction_expr = R.foreach(
            R.times('report_crew_properties.%restriction_items%'),
            'report_crew_properties.%restriction_desc_ix%',
            'report_crew_properties.%restriction_date_ix%'
            )


        roster_expr = R.foreach(
            'iterators.roster_set',
            'report_common.%crew_surname%',
            'report_common.%crew_firstname%',
            'report_common.%employee_number%',
            'report_crew_properties.%ctl_time_limit%',
            basic_prop_expr,
            recurrent_expr,
            training_expr,
            account_expr,
            qual_expr,
            restriction_expr,
            'report_crew_properties.%weekends_free_in_quarters%',
            )
        
        rosters, = R.eval(context, roster_expr)
        self.page = Column(width=500)

        for (ix, surname, firstname, empno, ctl_limit,
             basic_props, recurrent, training, accounts, quals,
             restrictions, weekends_free_in_quarters) in rosters:

            prop_table = {}
	    for r in basic_props:
                if r[1]:
                    prop_table[r[0].index] = r;
        
            # Header
            header_vals = (surname, firstname, empno)
            header = "%s, %s,  %s" %header_vals
            self.page.add(Row(Text(header,
                              font = self.HEADERFONT),
                         background=self.HEADERBGCOLOUR))

            # Basic crew properties
            self.prop_block_basic(False,prop_table)

            # Recurrent documents
            self.rec_block(recurrent)

            # Training activities
            training_mod = []
            for (jx, ctl_type, ctl_code, ctl_attr, ctl_time) in training:
                if ctl_type in ctl_to_show:
                    training_mod.append(
                        (jx, ctl_type, ctl_code, ctl_attr, ctl_time))
            self.list_block("Training Activities after " + ctl_limit, training_mod)

            # Accounts
            self.multi_block("Accounts", accounts)

            # Qualifications
            self.list_block("Qualifications", quals)

            # Restrictions
            self.list_block("Restrictions", restrictions)

            # Weekend Free
            weekends=[]
            weekends.append((1,weekends_free_in_quarters))
            self.list_block("Weekends", weekends)

            # Misc
            self.prop_block("Miscellaneous", prop_table, [6,7,9,10,11,12,13,14,15,16,17,18])
            self.page.page()

        self.add(self.page)


# End of file
