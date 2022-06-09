"""
 $Header$
 
 Agreement Groups

 Lists agreement groups, contracts and contained crew, with a summary.
 This is currently not used, here for upcoming needs only.
  
 Created:    March 2014
 By:         Lars Westerlind

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import OutputReport
from AbsDate import AbsDate
from RelTime import RelTime

# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'Agreement Groups'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

class csv_data:

    _rows = []
    _row = ""
    
    def __init__(self):
        self._rows = []
        self._row = ""

    def addValue(self,val):
        if len(self._row)>0:
            self._row += ";"
        if val is None:
           s = ""
        elif isinstance(val,int):
           s = str(val)
        else:
           s = str(val)
           s = '"'+s.replace('"',"'")+'"'
        self._row += s

    def addValues(self,vals):
        self._rows.append(";".join(vals))

    def addRow(self):
        self._rows.append(self._row)
        self._row = "" 
 
    def rows(self):
        return self._rows

class AgreementGroups(SASReport):

    def readRows(self):
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='fundamental.%is_roster%'),
            'report_common.%crew_is_cabin%',
            'report_common.%crew_agmt_group_id%',
            'report_common.%crew_agmt_group_desc%',
            'report_common.%crew_agmt_group_match_str%',
            'report_common.%crew_contract_id%',
            'report_common.%crew_contract_group_type%',
            'report_common.%crew_contract_part_time%',
            'report_common.%crew_contract_desc_short%',
            'report_common.%crew_contract_desc_long%',
            'report_common.%crew_id%',
            'report_common.%crew_name%'
            )

        rosters, = R.eval(CONTEXT, roster_expr)
        rows = []
        self.ag_dict = {}
        for (ix, is_cabin, ag_id, ag_desc, ag_match_str, contract_id, contract_type, contract_pt, contract_short,
            contract_long, crew_id, crew_name) in rosters:
            is_cabin=False
            #print "is_cabin",is_cabin
            #print "ag_id",ag_id
            #print "contract_pt",contract_pt
            #print "contract_id",contract_id
            #print "contract_short",contract_short
            #print "crew_id",crew_id,crew_name
            if ag_id is None:
                ag_id = '*None*'
            if contract_short is None:
                contract_short = '?'
            row = ["CC" if is_cabin else "FD", ag_id, contract_type, contract_pt, contract_id+": "+contract_short, crew_id, crew_name]
            rows.append(row)
            if not ag_id in self.ag_dict:
                self.ag_dict[ag_id] = (ag_id,ag_desc,ag_match_str)

        rows.sort()
        return rows
   
    def acc_grp_it(self,it,ag_id,contr_count,crew_count,pt_count):
        k = it+','+ag_id
        if k in self.acc:
            r = self.acc[k]
        else:
            r = [it,ag_id,0,0,0]
        r[2] += contr_count
        r[3] += crew_count
        r[4] += pt_count
        self.acc[k] = r
 
 
    def acc_grp(self,ag_id,ag_match_str,contr_count,crew_count,pt_count):
        for it in ag_match_str.split(','):
            self.acc_grp_it(it,ag_id,contr_count,crew_count,pt_count)
            self.acc_grp_it(it,'~',contr_count,crew_count,pt_count)
        else:
            self.acc_grp_it(' ',ag_id,contr_count,crew_count,pt_count)
            self.acc_grp_it(' ','~',contr_count,crew_count,pt_count)
 
    def create(self, reportType):
        outputReport = (reportType == "output")
        # Basic setup
        SASReport.create(self, TITLE, usePlanningPeriod=True)

	self.acc = {}
        hdr = ['F/C','Agmt group', 'F/V','Pt %','Contract','Crew','Crew Name']
        lgs = [7, 20, 7, 10, 30, 20, 50]
        lg_tot = 0
        for i in lgs:
            lg_tot += i
        
	rows = self.readRows()

        nr_cols = len(hdr)+2
        right_col = Column(width = self.pageWidth-lg_tot)
        main_col = Column()
        r = Row(self.getTableHeader(hdr, widths = lgs), right_col)
        main_col.add(r)
        outputRows = csv_data()
        outputRows.addValues(hdr)
        #outputRows = [";".join(hdr)]
        sums = []
	s_row = [None, None]
        s_count = [0, 0, 0]
        s_pt = [0, 0, 0]
        s_contracts = 0
        first_in_ag = True
        for row in rows:
            r = Row(Text(row[0]))
            outputRows.addValue(row[0])
            pt = 0
            for i in range(1,len(row)):
                s = row[i]
                if isinstance(s,int):
                    pt = s
                    s = format(s,'3d') # rightly sorted of 0-100
                r.add(Text(s))
                outputRows.addValue(row[i])
            id = s_row[0]
            if s_row[1]!=row[4] and s_row[1]!=None:
                
                if first_in_ag:
                    desc = self.ag_dict[id][1]
                    match_str = self.ag_dict[id][2]
                else:
                    desc= ""
                    match_str = ""
                sums.append([desc,match_str,s_row[1],format(s_count[2],'3d'),format(s_pt[2]/100,'3d')])
                first_in_ag = False
                s_count[2] = 0
                s_pt[2] = 0
                s_contracts += 1
            s_row[1] = row[4]
            if s_row[0]!=row[1] and s_row[0]!=None:
                id = s_row[0]
                desc = self.ag_dict[id][1]
                match_str = self.ag_dict[id][2]
                sums.append([desc,match_str,'***',format(s_count[1],'3d'),format((s_pt[1]+50)/100,'3d')])
                self.acc_grp(id,match_str,s_contracts,s_count[1],(s_pt[1]+50)/100)
                s_contracts = 0
                s_count[1] = 0
                s_pt[1] = 0
                first_in_ag = True
            s_row[0] = row[1]
           
            for i in range(len(s_count)):
                s_count[i] += 1 # added count
                s_pt[i] += pt # added part time 
	    main_col.add(r)
            main_col.page0()
            outputRows.addRow()

        id = s_row[0]
        if not id is None:
            if first_in_ag:
                desc = self.ag_dict[id][1]
                match_str = self.ag_dict[id][2]
            else:
                desc=""
                match_str=""
            sums.append([desc,match_str,s_row[1],format(s_count[2],'3d'),format(s_pt[2]/100,'3d')])
            s_contracts +=1
        if id!=None:
            sums.append([self.ag_dict[id][1],self.ag_dict[id][2],'***',format(s_count[1],'3d'),format(s_pt[1]/100,'3d')])
            self.acc_grp(id,self.ag_dict[id][2],s_contracts,s_count[1],(s_pt[1]+50)/100)
        sums.append(['***','','***',format(s_count[0],'3d'),format(s_pt[0]/100,'3d')])
        #print "sums count",len(sums),outputReport

        # Put it together
        if outputReport:
            self.set(font=Font(size=14))
            csvObject = OutputReport(TITLE, self, outputRows.rows())
            self.add(csvObject.getInfo())
        else:
            r = Row(self.getTableHeader(['Agmt group','Also matching','Contract','Count','Parttime'],widths=[20,40,10,10,10]))
            sum_col = Column()
            sum_col.page()
            sum_col.add(r)
            for row in sums:
                r = Row(Text(row[0]))
                for i in range(1,len(row)):
                    r.add(Text(row[i]))
                sum_col.add(r)
                sum_col.page0()
            
            r = Row(self.getTableHeader(['Derived','Base','Contracts','Crew','PT'],widths=[10,10,10,10,10]))
            tot_col = Column()
            tot_col.page()
            tot_col.add(r)
            totRows = self.acc.values()
            totRows.sort()
            for row in totRows:
                if row[1]=='~':
                    row[1] = '***'
                r = Row(Text(row[0]))
                for i in range(1,len(row)):
                    r.add(Text(row[i]))
                tot_col.add(r)
                tot_col.page0()
            
            self.add(main_col)
            self.add(Isolate(sum_col))
            self.add(Isolate(tot_col))

            
            
# End of file
