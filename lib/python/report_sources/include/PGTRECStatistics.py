# -*- coding: utf-8 -*-

"""
 $Header$
 
 PGT REC Statistics, CR 365

 Lists the number of crew in each recurrent month
  
 Created:    March 2010
 By:         Erik Arnström, Jeppesen Systems AB

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
TITLE = 'PGT REC Statistics'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

NAME_CC = "Cabin"
NAME_FD = "Flight deck"
NAME_TOT = "Total"

class PGTRECStatistics(SASReport):

    def add_to_data(self, mainkey, subkey, month):
        self.data[mainkey] = self.data.get(mainkey, dict())
        self.data[mainkey][subkey] = self.data[mainkey].get(subkey, dict())
        self.data[mainkey][subkey][month] = self.data[mainkey][subkey].get(month, 0) + 1

        self.data[mainkey]["Tot"] = self.data[mainkey].get("Tot", dict())
        self.data[mainkey]["Tot"][month] = self.data[mainkey]["Tot"].get(month, 0) + 1
        self.data[mainkey][subkey][14] = self.data[mainkey][subkey].get(14, 0) + 1
        self.data[mainkey]["Tot"][14] = self.data[mainkey]["Tot"].get(14, 0) + 1
                
    def create(self, reportType="pdf"):
        outputReport = (reportType == "output")
        # Basic setup
        SASReport.create(self, TITLE, usePlanningPeriod=True)
        
        month_names = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec", 13:"Missing", 14:"Tot"}

        rosterExpr = R.foreach('iterators.roster_set',
                               'crew.%is_cabin%',
                               'report_common.%pgt_rec_base%',
                               'report_common.%pgt_rec_group%',
                               'report_common.%pgt_rec_month%',
                               )
                
        rosters, = R.eval('default_context', rosterExpr)

        self.data = dict()

        for (ix, is_cc, base, grp, month) in rosters:
            if base is not None and grp <> "-":
                self.add_to_data(NAME_TOT, base, month)
                if is_cc:
                    self.add_to_data(NAME_CC, grp, month)
                else:
                    self.add_to_data(NAME_FD, grp, month)
                        
        csvRows = []
        
        for grp_name in (NAME_CC, NAME_FD, NAME_TOT):
            if not grp_name in self.data:
                continue
            if grp_name == NAME_TOT and NAME_FD not in self.data:
                continue
            grp_box = Column(border=border(0,0,0,0))
            grp_box.add(Row(Text(grp_name, font=self.HEADERFONT)))
            csvRows.append(grp_name)
            
            subs = self.data[grp_name].keys()
            subs.sort()
            header = self.getTableHeader([" ",]+subs, def_width=30)
            csvRows.append(";".join([" ",]+subs))
            grp_box.add(header)

            for month in range(14):
                csvRow = ""
                if month == 13:
                    month_row = Row(font=Font(weight=BOLD))
                elif month >= 11:
                    month_row = Row(border=border(bottom=0))
                else:
                    month_row = Row(border=border(bottom=0, colour='#cdcdcd'))
                month_row.add(month_names[month+1])
                csvRow += month_names[month+1]
                for sub in subs:
                    try:
                        count = self.data[grp_name][sub][month+1]
                    except:
                        count = 0
                    month_row.add(count)
                    csvRow += ";"+str(count)
                grp_box.add(month_row)
                csvRows.append(csvRow)
            if not outputReport:       
                self.add(Isolate(grp_box))
                self.add(" ")
                self.page0()
        if outputReport:
            self.set(font=Font(size=14))
            csvObject = OutputReport(TITLE, self, csvRows)
            self.add(csvObject.getInfo())

                        
# End of file
