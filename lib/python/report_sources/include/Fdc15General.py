"""
 $Header$
 
 FDC15 General

 Lists how many crew are in each contract group at the beginning of the period
  
 Created:    Oct 2015
 By:         Lars Westerlind 

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
import carmensystems.publisher.api as p
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import OutputReport

# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'FDC15 General'
cells = ("name","empno","contract","parttimePercentage","yearFreedaysBasic","yearFreedaysEntitled","yearFreedaysScheduled","monthFreedaysEntitled","monthFreedaysScheduled","twinMFreedaysEntitled","twinMFreedaysScheduled","reducingDays","yearRatio")
cellWidths = (100,30,30,30,30,30,30,30,30,30,30,30,30)
cellAligns = (p.LEFT, p.LEFT, p.LEFT, p.RIGHT, p.RIGHT, p.RIGHT, p.RIGHT, p.RIGHT, p.RIGHT, p.RIGHT, p.RIGHT, p.RIGHT, p.RIGHT)



class Fdc15General(SASReport):

    def create(self, reportType):
        outputReport = (reportType == "output")
        # Basic setup
        SASReport.create(self, TITLE, usePlanningPeriod=True)
        self.HEADERFONT = p.Font(size=8, weight=p.BOLD)


        # Loop over crew, get pattern
            
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where=('fundamental.%is_roster%')),
            'report_common.%crew_surname%',
            'report_common.%crew_firstname%',
            'report_common.%employee_number%',
            'report_fdc15.%contract_period_count%',
            'report_fdc15.%contract_period_rule%(1)',
            'report_fdc15.%parttime_percentage%(1)',
            'report_fdc15.%current_year_entitled_basic%',
            'report_fdc15.%freedays_acc_year_entitled%',
            'report_fdc15.%freedays_acc_year_scheduled%',
            'report_fdc15.%freedays_calendar_month_entitled%',
            'report_fdc15.%freedays_calendar_month_scheduled%',
            'report_fdc15.%freedays_twin_month_entitled%',
            'report_fdc15.%freedays_twin_month_scheduled%',
            'report_fdc15.%freedays_reducing_days%'
            )
            

        rosters, = R.eval(CONTEXT, roster_expr)
        self.crewDict = dict()
        crewCol = p.Column()#width=0.5*self.pageWidth)
        
        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        for (ix, surname, firstname, empno, contractPeriodCount, contract, parttimePercentage, yearFreedaysBasic, yearFreedaysEntitled, yearFreedaysScheduled, monthFreedaysEntitled, monthFreedaysScheduled, twinMFreedaysEntitled, twinMFreedaysScheduled, reducingDays) in rosters:
            crew = CrewData(empno, surname, firstname, contractPeriodCount, contract, parttimePercentage, yearFreedaysBasic, yearFreedaysEntitled, yearFreedaysScheduled, monthFreedaysEntitled, monthFreedaysScheduled, twinMFreedaysEntitled, twinMFreedaysScheduled, reducingDays)
            self.crewDict[empno] = crew
          
        #Header row
        outputRows = [crew.getOutputHeader()]
        self.addHeader(crewCol)

        for crew in self.crewDict.values():
            outputRows.append(crew.getOutputText())
            crewCol.add(crew.getReportRow())
            crewCol.page0()
        

        # Put it together
        if outputReport:
            self.set(font=p.Font(size=14))
            csvObject = OutputReport(TITLE, self, outputRows)
            self.add(csvObject.getInfo())
        else:
            self.add(crewCol)

        self.getReportFooter(crewCol)
        
    def addHeader(self, crewCol):
        header = self.getDefaultHeader()
        crewCol.add(p.Column(self.getTableHeader(self.getReportHeader1(), widths= cellWidths, aligns = cellAligns)))
        crewCol.add(p.Column(self.getTableHeader(self.getReportHeader2(), widths= cellWidths, aligns = cellAligns)))
        crewCol.add(p.Column(self.getTableHeader(self.getReportHeader3(), widths= cellWidths, aligns = cellAligns)))
        
    def addHeaderRow(self, header, headerRow):
        header.add(self.getTableHeader(headerRow, widths= cellWidths, aligns = cellAligns))
        
    def getTotalRatio(self):
        entitled = 0
        soFar = 0
        for crew in self.crewDict.values():
            entitled += crew.getValue("yearFreedaysEntitled")
            soFar += crew.getValue("yearFreedaysScheduled")
        
        return crew.getYearRatio(entitled, soFar)
            
    def getTotal(self, key):
        sum = 0
        for crew in self.crewDict.values():
            value = crew.getValue(key)
            if value != None:
                sum += value
        return str(sum)

    def getReportFooter(self, crewCol):
        crewCol.add(self.getTableFooter(["Total", "", "", "", "","", self.getTotal("yearFreedaysScheduled"), self.getTotal("monthFreedaysEntitled"), self.getTotal("monthFreedaysScheduled"), self.getTotal("twinMFreedaysEntitled"), self.getTotal("twinMFreedaysScheduled"),self.getTotal("reducingDays"), self.getTotalRatio()],widths=cellWidths, aligns=cellAligns))
            
    def getTableFooter(self, items, vertical=False, widths=None, aligns=None, def_width=0):
        if vertical:
            output = p.Column(font=p.Font(weight=p.BOLD), border=None)
        else:
            output = p.Row(font=self.HEADERFONT, border=None)
#            output = p.Row(font=self.HEADERFONT, border=None, background=self.HEADERBGCOLOUR)
        ix = 0
        for item in items:
            if(ix == 0):
                txt = p.Text(item, font=self.HEADERFONT)
            else:
                if aligns:
                    txt = p.Text(item, align=aligns[ix])
                else:
                    txt = p.Text(item)
            if widths:
                tmpCol = p.Column(width=widths[ix])
            elif def_width > 0:
                tmpCol = p.Column(width=def_width)
            else:
                tmpCol = p.Column()
            if vertical:
                output.add(txt)
            else:
                tmpCol.add(txt)
                output.add(tmpCol)
            ix += 1            
        return output
  
#    def getReportHeader1(self):
#        return (["Name", "Empno", "Rule", "%", "Current", "Acc.", "Acc.", "Month", "Month", "Twin mon", "Twin mon", "Reducing", "Year"])
#        #return ["Name", "Empno","Contract","Parttime%","Freedays/year entitled ","Freedays/year scheduled","Freedays/month entitled","Freedays/month scheduled"]
#    def getReportHeader2(self):
#        return (["", "", "", "", "entitled", "entitled", "scheduled", "entitled", "scheduled", "entitled", "scheduled", "days", "ratio"])
#    def getReportHeader3(self):
#        return (["", "", "", "", "basic", "fdc15", "fdc15", "fdc15", "fdc15", "fdc15", "fdc15", "", ""])
  
    def getReportHeader1(self):
        return (["Name", "Empno", "Rule", "Pt", "Basic", "Acc", "Acc", "Mon", "Mon", "Twin", "Twin mon", "Reduc", "Year"])
    def getReportHeader2(self):
        return (["", 	"", 	"", 	"", 	"year",	"year",	"year",	"min",	"min",	"mon",	"mon", "days", "ratio"])
    def getReportHeader3(self):
        return (["", 	"", 	"", 	"", 	"entl", "entl", "sched", "entl", "sched", "entl", "sched", "", ""])
 
class CrewData:
    def __init__(self, empno, surname, firstname, contractPeriodCount, contract, parttimePercentage, yearFreedaysBasic, yearFreedaysEntitled, yearFreedaysScheduled, monthFreedaysEntitled, monthFreedaysScheduled,  twinMFreedaysEntitled, twinMFreedaysScheduled, reducingDays):
        self.values = dict()
        self.values["surname"] = surname
        self.values["firstname"] = firstname
        self.values["empno"] = empno
        self.values["name"] = firstname + " " + surname
        self.values["yearFreedaysBasic"] = yearFreedaysBasic
        self.values["yearFreedaysEntitled"] = yearFreedaysEntitled
        self.values["yearFreedaysScheduled"] = yearFreedaysScheduled
        self.values["contractPeriodCount"] = contractPeriodCount
        self.values["contract"] = self.getContractDependentString(contract)
        self.values["parttimePercentage"] = self.getContractDependentString(parttimePercentage)
        self.values["monthFreedaysEntitled"] = monthFreedaysEntitled
        self.values["monthFreedaysScheduled"] = monthFreedaysScheduled
        self.values["twinMFreedaysEntitled"] = twinMFreedaysEntitled
        self.values["twinMFreedaysScheduled"] = twinMFreedaysScheduled
        self.values["reducingDays"] = reducingDays
        self.values["yearRatio"] = self.getYearRatio(yearFreedaysEntitled, yearFreedaysScheduled)
    
    def getValue(self, key):
        return self.values[key]
        
    def getYearRatio(self, basic, soFar):
        yearRatioResult = ""
        #print "yearratio",str(basic),str(soFar)
        #print "type", type(basic),type(soFar)
        if basic :
            yearRatio = (float(soFar) / float(basic)) * 100
            yearRatioString = "{0:.1f}%".format(round(yearRatio, 1))
            yearRatioResult = self.getContractDependentString(yearRatioString)
        #print "returning ",yearRatioResult
        return yearRatioResult
            
        
    def getContractDependentString(self, string):
        if(self.values["contractPeriodCount"] > 1):
            return "*"
        else:
            return str(string)
    
        
    def getOutputHeader(self):
        return "Name;Empno;Rule;Parttime %;Freedays/year basic;Freedays/year entitled;Freedays/year so far;Freedays/month entitled;Freedays/month scheduled;Freedays/twin mon entitl;Freedays/twin mon sched;Reducing days;Year ratio"
    
    def getOutputText(self):
        return self.values["name"] + ";" + str(self.values["empno"]) + ";" + self.values["contract"] + ";" + self.values["parttimePercentage"] + ";" + str(self.values["yearFreedaysBasic"]) + ";" + str(self.values["yearFreedaysEntitled"]) + str(self.values["yearFreedaysScheduled"]) + ";" + str(self.values["monthFreedaysEntitled"]) + ";" + str(self.values["monthFreedaysScheduled"]) + ";"  + str(self.values["twinMFreedaysEntitled"]) + ";" + str(self.values["twinMFreedaysScheduled"])+ ";" + str(self.values["reducingDays"]) + ";" + self.values["yearRatio"]
  

    def getReportRow(self):
        tmpRow =p.Row()
        for(cell,cellAlign,cellWidth) in zip(cells,cellAligns,cellWidths) :
            tmpRow.add(p.Text(self.values[cell], align=cellAlign,width=cellWidth))
        return tmpRow
            
# End of file
