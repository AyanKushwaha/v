"""
 $Header$
 
 Sim Statistics

 Information about the number of crew with PC date or OPC month in each month

 Created:    June 2007
 By:         Peter, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime

# constants =============================================================={{{1
CONTEXT = 'default_context'
#CONTEXT = 'sp_crew'
TITLE = 'Sim Statistics'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

class SimStatistics(SASReport):

    def headerRow(self, monthsInYear):
        tmpRow = self.getTableHeader(monthsInYear)
        #,leftHeader='Type',rightHeader='Sum')
        return tmpRow

    def headerMonths(self, items):
        output = Row(font=self.HEADERFONT, border=None, background=self.HEADERBGCOLOUR)
        output.add(Text("Type",align=LEFT))
        for item in items:
            output.add(Text(item,align=RIGHT))
        output.add(Text("Sum",align=LEFT))
        return output

    def sumRow(self, data, monthsInYear):
        tmpRow = Row(border=border(top=0), font=Font(weight=BOLD))
        tmpRow.add(Text('Total', border=border(right=0)))
        sum = 0
        for month in monthsInYear:
            tmp = data.get(month)
            sum += tmp
            tmpRow.add(Text(tmp,align=RIGHT))
        tmpRow.add(Text(sum, border=border(left=0),align=RIGHT))
        return tmpRow

    def sumRowPC(self, data1, data2, monthsInYear):
        tmpRow = Row(border=border(top=0), font=Font(weight=BOLD))
        tmpRow.add(Text('Total', border=border(right=0)))
        sum1 = 0
        sum2 = 0
        for month in monthsInYear:
            tmp1 = data1.get(month)
            tmp2 = data2.get(month)
            sum1 += tmp1
            sum2 += tmp2
            if tmp1 > 0:
                tmpstr = str(tmp1) + "(" + str(tmp2) + ")"
            else:
                tmpstr = str(tmp1)
            tmpRow.add(Text(tmpstr,align=RIGHT))
        if tmp1 > 0: 
            sumstr = str(sum1) + "(" + str(sum2) + ")"
        else:
            sumstr = str(sum1)
        tmpRow.add(Text(sumstr, border=border(left=0),align=RIGHT))
        return tmpRow
    
    def createForType(self, rank, qual, type, data):
        try:
            data[qual] = data.get(qual,dict())
            data[qual][type] = data[qual].get(type,dict())
            data[qual][type][rank] = data[qual][type].get(rank,dict())
            data[qual][type]["Summary"] = data[qual][type].get("Summary", dict())
        except:
            print "Error type" +str(month) + " " + rank
            
    def createForQual(self, rank, month, qual, type, data):
        try:
            self.createForType(rank, qual, type, data)
            self.createForMonth(rank, month, qual, type, data)
        except:
            print "Error qual" +str(month) + " " + rank

    def createForMonth(self, rank, month, qual, type, data):
        try:
            data[qual][type][rank][month] = data[qual][type][rank].get(month,0) + 1
            data[qual][type]["Summary"][month] = data[qual][type]["Summary"].get(month,0) + 1
        except:
            print "Error month"+str(month) + " " + rank

    def createForDoubleQualCat(self, rank, opc_month1, opc_qual, pc_month1, pc_qual, data):
        try:
            self.createForType(rank, opc_qual, "OPC", data)
            self.createForType(rank, pc_qual, "PC", data)
            month = opc_month1 - 1
            self.createForMonth(rank, month, opc_qual, "OPC", data)
            month = pc_month1 - 1
            self.createForMonth(rank, month, pc_qual, "PC", data)
        except:
            print "Error cat1" + rank + " " + str(opc_month1) + " " +  str(pc_month1) + " " + str(data)        
    def createForCat(self, rank, opc_month1, pc_month1, qual, data):
        try:
            self.createForType(rank, qual, "OPC", data)
            self.createForType(rank, qual, "PC", data)
            month = opc_month1 - 1
            self.createForMonth(rank, month, qual, "OPC", data)
            month = pc_month1 - 1
            self.createForMonth(rank, month, qual, "PC", data)
        except:
            print "Error cat2" + rank + " " + str(opc_month1) + " " +  str(pc_month1) + " " + str(data)
        
    def createForOPCPC(self, rank, opc_month1, pc_month1, qual, data):
        try:
            self.createForType(rank, qual, "", data)
            month = opc_month1 - 1
            self.createForMonth(rank, month, qual, "", data)
            month = pc_month1 - 1
            self.createForMonth(rank, month, qual, "", data)
        except:
            print "Error cat3" + rank + " " + str(opc_month1) + " " +  str(pc_month1) + " " + str(data)
        
            
    def create(self, reportType):
        objectReport = (reportType == "object")
        generalReport = not objectReport
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE)

##        # Get Planning Period start and end
##        pp_start,pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')
##        pp_length = (pp_end - pp_start) / RelTime(24, 00)
##        varPrefix = 'report_ccr.%skbu_resource_pool_'
##        self.months, = R.eval("default_context", varPrefix + 'months%')
        
##        self.monthNames, = R.eval("default_context",
##                                  R.foreach(R.times(self.months),
##                                             varPrefix + 'month_str - 1_ix%',
##                                            )
##                                  )
        

        
 
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='fundamental.%is_roster% and not keywords.%hidden%'),
            ##R.iter('iterators.roster_set', where='fundamental.%is_roster%'),
            'report_common.%crew_string%',
            'report_common.%crew_rank%',
            'crew.%homebase%',
            'training.%pc_month_1%',
            'training.%opc_month_1%',
            'training.%opc_month_2%',
            'training.%pc_qual_1%',
            'training.%opc_qual_1%',
            'training.%opc_qual_2%',
            'training.%pc_month_2%',
            'training.%pc_qual_2%',
            'report_ccr.%recurrent_type_mismatch_expiry_date%',
            'crew.%is_double_qualified_new%',
            'crew.%is_crew_double_qualified%',
            'crew.%is_double_qualified_skn%',
            'crew.%has_agmt_group_sk_fd_mff%'
            )
        
        rosters, = R.eval(CONTEXT, roster_expr)

        data = dict()
        missmatch_data = dict()
        pc_data = dict()
        num_crew_missing_document = 0
        # Loop over all the 'bags' that comes from the RAVE expression
        # and collect the data
        for (ix,crewString,rank,base,pc_month1,opc_month1,opc_month2,pc_qual1,qual1,opc_qual2,pc_month2,qual2,missmatch, double_qual, double_LH, double_no, mff) in rosters:
            if missmatch:
                temp = missmatch_data
            else:
                temp = data
            # Qual other than A3 A4
            # A3/A4 qual
            if (((qual1 == "A3" or qual1 == "A4" or qual1 == "A5" or qual1 == "A2") or (qual1 == "37" or qual1 == "38")) and qual2 == None and opc_month1 != None and pc_month1 != None):
                self.createForCat(rank, opc_month1, pc_month1, qual1, temp)

            elif (double_qual and opc_month1 != None and pc_month1 != None):
                self.createForOPCPC(rank, opc_month1, pc_month1, "PC/OPC", temp)
                try:
                    i = pc_month1 - 1
                    pc_data[rank] = pc_data.get(rank,dict())
                    pc_data[rank][i] = pc_data[rank].get(i,0) + 1
                except:
                    print "Error other" +str(i) + " " + rank
            #Dual qualified A3 A5 or 37 38
            elif (double_no and pc_month1 != None and opc_month1 != None):
                self.createForDoubleQualCat(rank, opc_month1, qual1, pc_month1, pc_qual1, data)
            elif (double_LH and (pc_month1 != None and pc_month2 != None) or (opc_month1 != None and opc_month2 != None)):
                if(pc_month1 != None and pc_month2 != None):
                    qual = pc_qual1
                    month = pc_month1 - 1
                    self.createForQual(rank, month, qual, "PC", temp)
                    if (mff):
                        qual = qual2
                        month = pc_month2 - 1
                        self.createForQual(rank, month, qual, "PC", temp)
                if(opc_month1 != None and opc_month2 !=None):
                    qual = qual1
                    month = opc_month1 - 1
                    self.createForQual(rank, month, qual, "OPC", temp)
                    if (mff):
                        qual = opc_qual2
                        month = opc_month2 - 1
                        self.createForQual(rank, month, qual, "OPC", temp)
                

            else:
                num_crew_missing_document += 1    
        
        self.createReportFor(data, missmatch_data, pc_data, objectReport, generalReport, num_crew_missing_document) 
                             
        
    def createReportFor(self, data, missmatch_data, pc_data, objectReport, generalReport, num_crew_missing_document):
        # OPC months in year
        if objectReport:
            self.add(Row(Text(crewString, font=self.HEADERFONT)))
        self.createReportForData(data, pc_data, generalReport)
        self.newpage()
        self.createReportForData(missmatch_data, pc_data, generalReport)
        self.add(Row(" "))
        missingstr = str(num_crew_missing_document) + " crew is missing OPC/PC document"
        self.add(Row(Text(missingstr, align=RIGHT)))
        
    def createReportForData(self, data, pc_data, generalReport):
        monthsInYear = "Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec" 
               ## basesInUse = []
##        for base in self.SAS_BASES:
##            basesInUse.append(base)
##        basesInUse.append("Summary")
        
        # Ranks in use
        ranksInUse = "FC","FP","FR","AP","AS","AH","AA","-","Summary" 
        if data:
           for month_qual in data:
               for type in data[month_qual]:
                    rankBox = Column()
                    if generalReport:
                       rankBox.add(Row(Text(month_qual + " " + type),font=self.HEADERFONT))
                    rankBox.add(self.headerMonths(monthsInYear))
                    ranks = []
                    dataBox = Column(border=border(left=0))
                    total = dict()
                    pc_total = dict()
                    #if ((base in data[ac_qual]) and (generalReport or base != "Summary")):
                    for rank in ranksInUse:
                        if (rank in data[month_qual][type] and rank != "Summary"):
                            dataBox.add(self.createQualTypeRankRow(month_qual, type, rank, data, pc_data, ranks, total, pc_total))
                    rankBox.add(Row(
                        self.getTableHeader(ranks, vertical=True),
                        dataBox))
                    #rankBox.add(data[month_qual]["Summary"])
                    if month_qual == "PC/OPC":
                        rankBox.add(self.sumRowPC(total,pc_total,range(12)))
                    else:
                        rankBox.add(self.sumRow(total,range(12)))
                    self.add(Row(rankBox))
        else:
            self.add("No Sim Assignments")
        
    def createQualTypeRankRow(self, month_qual, type, rank, data, pc_data, ranks, total, pc_total):
        ranks.append(rank)
        currentRow = Row()
        sum = 0
        if month_qual == "PC/OPC":
            pc_sum = 0
            for i in range(12):
                tmp = data[month_qual][type][rank].get(i,0)
                pc = pc_data[rank].get(i,0)
                if tmp > 0:
                    tmpstr = str(tmp) + "(" + str(pc) + ")"
                else:
                    tmpstr = str(tmp)
                total[i] = total.get(i,0)+tmp
                pc_total[i] = pc_total.get(i,0)+pc
                currentRow.add(Text(tmpstr, align=RIGHT))
                sum += tmp
                pc_sum += pc
            if sum > 0:
                sumstr = str(sum) + "(" + str(pc_sum) + ")"
            else:
                sumstr = str(sum) 
        else:
            for i in range(12):
                tmp = data[month_qual][type][rank].get(i,0)
                total[i] = total.get(i,0)+tmp
                currentRow.add(Text(tmp,align=RIGHT))
                sum += tmp
            sumstr = str(sum)
        
        currentRow.add(Text(sumstr, font=Font(weight=BOLD), align=RIGHT, border=border(left=0)))
        return currentRow 
# End of file
