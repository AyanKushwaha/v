"""
 $Header$
 
 FDC15 General

 Lists how many crew are in each contract group at the beginning of the period
  
 Created:    Mar 2015
 By:         Lars Westerlind 

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
import carmensystems.publisher.api as p
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import OutputReport

# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'FDC15 Year target'

rave_desc = [
          (None,     'crewix'),
          ('report_common.%crew_surname%', 'surname'),
          ('report_common.%crew_firstname%','firstname'),
          ('report_common.%employee_number%','empno'),
          ('report_fdc15.%contract_period_count%','periodcount'),
          ('report_fdc15.%contract_period_rule%(1)','fdcrule'),
          ('report_fdc15.%parttime_percentage%(1)','pt'),
          ('report_fdc15.%freedays_fdc_days%','fdcdays'),
          ('report_fdc15.%freedays_reducing_days%','reduc'),
          ('report_fdc15.%freedays_calendar_month_scheduled%','possible'),
          ('report_fdc15.%freedays_acc_balance%','balance'),
          ('report_fdc15.%freedays_year_target%','target')]
RD_RAVE = 0
RD_KEY = 1

col_desc = [
            ('name',    'Name',     110,p.LEFT),
            ('empno',   'Empno',    30,p.LEFT),
            ('fdcrule', 'Rule',     35,p.LEFT),
            ('pt',      'Pt %',     20,p.LEFT),
            ('fdcdays', 'Fdc days', 35,p.RIGHT),
            ('reduc',   'Reduc',    50,p.RIGHT),
            ('possible','Poss free',50,p.RIGHT),
            ('balance', 'Fdc bal',  50,p.RIGHT),
            ('planfree','Plan free',50,p.RIGHT),
            ('planblank','Plan blank',50,p.RIGHT),
            ]
CD_KEY = 0
CD_HDR1 = 1
CD_WID = 2
CD_ALGN = 3
           
def cd_tuple(col):
    ret = ()
    for t in col_desc:
        ret += (t[col],)
    return ret 

def dec2_frm(val):
    return "{0:.2f}".format(round(float(val)/100, 2))

class Fdc15Year(SASReport):

    def create(self, reportType):
        outputReport = (reportType == "output")
        # Basic setup
        SASReport.create(self, TITLE, usePlanningPeriod=True)
        self.HEADERFONT = p.Font(size=8, weight=p.BOLD)


        # Loop over crew, get pattern
            
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where=('fundamental.%is_roster%')),
            rave_desc[1][RD_RAVE],
            rave_desc[2][RD_RAVE],
            rave_desc[3][RD_RAVE],
            rave_desc[4][RD_RAVE],
            rave_desc[5][RD_RAVE],
            rave_desc[6][RD_RAVE],
            rave_desc[7][RD_RAVE],
            rave_desc[8][RD_RAVE],
            rave_desc[9][RD_RAVE],
            rave_desc[10][RD_RAVE],
            rave_desc[11][RD_RAVE]
            )
            

        rosters, = R.eval(CONTEXT, roster_expr)
        self.crewDict = dict()
        self.crewList = []
        crewCol = p.Column()#width=0.5*self.pageWidth)
        
        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        for t in rosters:
            crew = CrewData()
            for i in range(len(rave_desc)):
                k = rave_desc[i][RD_KEY]
                crew.addData(i,k,t[i])
            crew.finalize()
            self.crewDict[crew.values[k]] = crew
            self.crewList.append(crew)
        #Header row
        outputRows = [crew.getOutputHeader()]
        self.addHeader(crewCol)

        for crew in self.crewList:
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
        #self.addHeaderRow(header,  self.getReportHeader1())
        #self.addHeaderRow(header,  self.getReportHeader2()) width=t[CD_WID], align=t[CD_ALGN]
        crewCol.add(p.Column(self.getTableHeader(self.getReportHeader1(),widths= cd_tuple(CD_WID), aligns = cd_tuple(CD_ALGN))))
        crewCol.add(p.Column(self.getTableHeader(self.getReportHeader2(),widths= cd_tuple(CD_WID), aligns = cd_tuple(CD_ALGN))))

        #self.setHeader(header)
        
    def addHeaderRow(self, header, headerRow):
        header.add(self.getTableHeader(headerRow))
                    
    def getTotal(self, key):
        sum = 0
        for crew in self.crewList:
            value = crew.values[key]
            if value != None:
                sum += value
        return sum

    def getFooterItems(self):
        ret = ["Total","","",""]
        ret.append(str(self.getTotal('fdcdays')))
        ret.append(str(self.getTotal('reduc')))
        ret.append(str(self.getTotal('possible')))
        ret.append(str(self.getTotal('balance')))
        ret.append(dec2_frm(self.getTotal('target')))
        ret.append(dec2_frm(self.getTotal('targetblank')))
        return ret

    def getReportFooter(self, crewCol):
        crewCol.add(self.getTableFooter(self.getFooterItems(),widths= cd_tuple(CD_WID), aligns = cd_tuple(CD_ALGN)))
            
    def getTableFooter(self, items, vertical=False, widths=None, aligns=None, def_width=0):
        if vertical:
            output = p.Column(font=p.Font(weight=p.BOLD), border=None)
        else:
            output = p.Row(font=self.HEADERFONT, border=None)
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
  
    def getReportHeader1(self):
        ret = []
        for t in col_desc:
            ret.append(t[CD_HDR1])
        return ret
    
    def getReportHeader2(self):
        ret = []
        for t in col_desc:
            ret.append("")
        return ret
 
 
class CrewData:

    def __init__(self):
        self.values = dict()

    def addData(self, i, k, val):
        i#print i,k,val,type(val)
        if i==0:
            self.values[k] = val.index
        else:
            self.values[k] = val

    def finalize(self):
        #print self.values
        #print type(self.values['possible']),self.values['target']
        self.values['name'] = self.values['surname'] + ', ' + self.values['firstname']
        self.values['targetblank'] = 100 * self.values['possible'] - self.values['target']            
        self.values['planfree'] = dec2_frm(self.values['target'])
        self.values['planblank'] = dec2_frm(self.values['targetblank'])
        if not self.values['fdcrule']:
            self.values['fdcrule'] = '-'
        if self.values['periodcount']>1:
            self.values['fdcrule'] += ' *'
            self.values['pt'] = str(self.values['periodcount']) + ' *'
        
        
    def getOutputHeader(self):
        ret = col_desc[0][CD_HDR1]
        for i in range(1, len(col_desc)):
            ret += ";" + col_desc[i][CD_HDR1]
        return ret
    
    def getOutputText(self):
        ret = str(self.values[col_desc[0][CD_KEY]])
        for i in range(1, len(col_desc)):
            ret += ";" + str(self.values[col_desc[i][CD_KEY]])
        return ret
  
    def getReportRow(self):
        ret =p.Row()
        for t in col_desc:
            k = t[CD_KEY]
            ret.add(p.Text(self.values[k], width=t[CD_WID], align=t[CD_ALGN]))
        return ret
            
# End of file
