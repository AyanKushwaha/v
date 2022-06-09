from report_sources.include.SASReport import SASReport
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
import utils.Names as Names
from tm import TM
import Cui
import Cfh
from carmstd import cfhExtensions
from RelTime import RelTime
from AbsDate import AbsDate
from AbsTime import AbsTime
import os
import tempfile

CREW_WIDTH = 45
ACCOUNT_WIDTH = 80
DATE_WIDTH = 50
AMOUNT_WIDTH = 40
RATE_WIDTH = 40
REASON_WIDTH = 85
SOURCE_WIDTH = 110
ENTRYTIME_WIDTH = 75
USERNAME_WIDTH = 60
SI_WIDTH = 185

def get_duplicates(ST,ET,ACCOUNT='ALL',BASE='ALL',MAINCAT='ALL'):

    class crewObject(object):
        def __init__(self, crewid, empno):
            self.crewid = crewid
            self.empno = empno
            self.entries = {}

        def __str__(self):
            return self.crewid

        def getEmpno(self):
            return self.empno

        def add_entry(self,account,tim,reasoncode,args = None):
            if account not in self.entries.keys():
                self.entries[account] = {}

            if not tim in self.entries[account].keys():
                self.entries[account][tim] = {}

            if not reasoncode in self.entries[account][tim].keys():
                self.entries[account][tim][reasoncode] = {}

            amount = args['amount']
            if not amount in self.entries[account][tim][reasoncode].keys():
                self.entries[account][tim][reasoncode][amount] = []

            self.entries[account][tim][reasoncode][amount].append(args)

        def get_duplicates(self):
            duplicates = []
            for account in self.entries.keys():
                for tim in self.entries[account].keys():
                    for reasoncode in self.entries[account][tim].keys():
                        for amount in self.entries[account][tim][reasoncode].keys():
                            if len(self.entries[account][tim][reasoncode][amount]) > 1:
                                for args in self.entries[account][tim][reasoncode][amount]:
                                    duplicates.append([account,tim,reasoncode,args['source'],args['si'],args['amount'],args['rate'],args['entrytime'],args['username']])
            return duplicates

    crewlist = {}
    for entry in TM.account_entry.search('(&(tim>=%s)(tim<=%s))' % (ST,ET)):
        crew = entry.crew.id
        empno = entry.crew.empno
        tim = str(entry.tim).split()[0]
        account = entry.account.id
        source = entry.source
        si = entry.si
        amount = entry.amount
        rate = entry.rate
        reasoncode = entry.reasoncode
        entrytime = entry.entrytime
        username = entry.username

        if (ACCOUNT == 'ALL' or ACCOUNT == account):
            if crew not in crewlist.keys():
                crewlist[crew] = crewObject(crew,empno)
    
            args = {'source':source, 'si':si, 'amount':amount, 'rate':rate, 'entrytime':entrytime, 'username':username}
            crewlist[crew].add_entry(account,tim,reasoncode,args)

    duplicates = {}
    for crew in crewlist.keys():
        crew_dup_checked = False
        for employment in TM.crew[(crew)].referers('crew_employment', 'crew'):
            if not crew_dup_checked and employment.validto >= AbsTime(ST) and employment.validfrom <= AbsTime(ET):
                base = employment.base.id
                maincat = employment.titlerank.maincat.id

                if (BASE == 'ALL' or BASE == base) and \
                   (MAINCAT == 'ALL' or MAINCAT == maincat):
                    crew_dup_checked = True
                    crew_duplicates = crewlist[crew].get_duplicates()
                    if crew_duplicates:
                        duplicates[crewlist[crew].getEmpno()] = {'crewid': crew, 'base': base, 'maincat': maincat, 'duplicates': crew_duplicates}

    return duplicates

def exportToExcel(duplicates={}):
    import csv
    import time
    try:
        user = R.eval('user')[0]
    except:
        user = Names.username()
    
    carmtmp = os.environ['CARMTMP']
    timestampFormat="%Y%m%d_%H%M%S"
    filename='AccountConflictReport.%s.%s.csv' % (user, time.strftime(timestampFormat))
    
    filepath = os.path.join(carmtmp, 'logfiles', filename)
    csvFile = open(filepath,'wb')
    writer = csv.writer(csvFile, delimiter=';')
    writer.writerow(['Crew id','Crew empno', 'Base', 'Maincat', 'Account', 'Date', 'Amount', 'Rate', 'Reason', 'Source', 'Entrytime', 'Username', 'SI'])

    crew_empnumbers = duplicates.keys()
    crew_empnumbers.sort()

    for crew in crew_empnumbers:
        crewid = duplicates[crew]['crewid']
        base = duplicates[crew]['base']
        maincat = duplicates[crew]['maincat']
        for entry in duplicates[crew]['duplicates']:
            [account,date,reasoncode,source,si,amount,rate,entrytime,username] = entry
            writer.writerow([crewid,crew,base,maincat,account,date,amount,rate,reasoncode,source,entrytime,username,si])
    csvFile.close()
    
    return filepath


class AccountConflictReport(SASReport):
    def createCSVReport(self):
        self.add(Row(Text('Data exported to:')))
        self.add(Row(Text(str(self.filepath))))
        
    def create(self):
        title = 'Account Entry Conflicts'
        try:
            user = R.eval('user')[0]
        except:
            user = Names.username()

        if not 'startDate' in dir(self):
            self.startDate = self.arg("startDate")
            self.endDate = self.arg("endDate")
            self.account = self.arg("account")
            self.base = self.arg("base")
            self.maincat = self.arg("maincat")

        if self.account == '': self.account = 'ALL'
        if self.base == '': self.base = 'ALL'
        if self.maincat == '': self.maincat = 'ALL'
        duplicates = get_duplicates(self.startDate,self.endDate,self.account,self.base,self.maincat)
        
        nowTime, = R.eval('fundamental.%now%')
        headerItemsDict = {'By user: ':user, 'Created: ':nowTime, 'Period: ': '%s - %s' % (AbsDate(self.startDate), AbsDate(self.endDate)), 'Account: ' : self.account, 'Base: ' : self.base, 'Maincat: ': self.maincat}
        bgColorRow = '#eeeeee'
        SASReport.create(self, title, showPlanData=False, orientation=LANDSCAPE, headerItems=headerItemsDict)

        header = self.getDefaultHeader()
        header.add(self.getTableHeader(items=('Crew', 'Account', 'Date', 'Amount', 'Rate', 'Reason', 'Source', 'Entrytime', 'Username', 'SI'),
            widths=(CREW_WIDTH, ACCOUNT_WIDTH, DATE_WIDTH, AMOUNT_WIDTH, RATE_WIDTH, REASON_WIDTH, SOURCE_WIDTH, ENTRYTIME_WIDTH, USERNAME_WIDTH, SI_WIDTH),
            aligns=(LEFT, LEFT, LEFT, RIGHT, RIGHT, LEFT, LEFT, LEFT, LEFT, LEFT)))
        self.setHeader(header)

        crew_empnumbers = duplicates.keys()
        crew_empnumbers.sort()
        for crew in crew_empnumbers:
            if bgColorRow == '#ffffff':
                bgColorRow = '#eeeeee'
            else:
                bgColorRow = '#ffffff'
            for entry in duplicates[crew]['duplicates']:
                [account,date,reasoncode,source,si,amount,rate,entrytime,username] = entry
                if si and len(si) > 35:
                    si = si[:35] + '...'
                self.add(Row(
                             Column(Text('%s'%str(crew)), width=CREW_WIDTH),
                             Column(Text('%s'%str(account)), width=ACCOUNT_WIDTH),
                             Column(Text('%s'%str(date)), width=DATE_WIDTH),
                             Column(Text('%s'%str(amount), align=RIGHT), width=AMOUNT_WIDTH),
                             Column(Text('%s'%str(rate), align=RIGHT), width=RATE_WIDTH),
                             Column(Text('%s'%str(reasoncode)), width=REASON_WIDTH),
                             Column(Text('%s'%str(source)), width=SOURCE_WIDTH),
                             Column(Text('%s'%str(entrytime)), width=ENTRYTIME_WIDTH),
                             Column(Text('%s'%str(username)), width=USERNAME_WIDTH),
                             Column(Text('%s'%str(si)), width=SI_WIDTH),
                             background=bgColorRow
                             ))
            self.page()


class AccountConflictForm(Cfh.Box):
    def __init__(self, *args):
        Cfh.Box.__init__(self, *args)

        pp_start,pp_end, = R.eval('fundamental.%pp_start%', 'fundamental.%pp_end%')

        account_set = [account.id for account in TM.account_set]
        maxwidth = len(max(account_set,key=len))

        startDate = int(pp_start)
        self.startDate = Cfh.Date(self, "STARTDATE", startDate)
        self.startDate.setMandatory(1)

        endDate = int(pp_end + RelTime('0:01'))
        self.endDate = Cfh.Date(self, "ENDDATE", endDate)
        self.endDate.setMandatory(1)


        accounts = 'Account;ALL;'+';'.join(account_set)
        self.account = Cfh.String(self,'ACCOUNT',maxwidth, 'ALL')
        self.account.setMenuString(accounts)
        self.account.setMenuOnly(1)
        self.account.setMandatory(0)
        self.account.setTranslation(Cfh.String.ToUpper)

        bases = 'Base;ALL;'+';'.join([base.id for base in TM.crew_base_set])
        self.base = Cfh.String(self,'BASE',maxwidth, 'ALL')
        self.base.setMenuString(bases)
        self.base.setMenuOnly(1)
        self.base.setMandatory(0)
        self.base.setTranslation(Cfh.String.ToUpper)

        maincats = 'Maincat;ALL;FD;CC'
        self.maincat = Cfh.String(self,'MAINCAT',maxwidth,'ALL')
        self.maincat.setMenuString(maincats)
        self.maincat.setMenuOnly(1)
        self.maincat.setMandatory(0)
        self.maincat.setTranslation(Cfh.String.ToUpper)

        formats = 'Format;REPORT;CSV'
        self.exportFormat = Cfh.String(self,'FORMAT',maxwidth,'REPORT')
        self.exportFormat.setMenuString(formats)
        self.exportFormat.setMenuOnly(1)
        self.exportFormat.setMandatory(0)
        self.exportFormat.setTranslation(Cfh.String.ToUpper)

        self.ok = Cfh.Done(self, "B_OK")
        self.cancel = Cfh.Cancel(self, "B_CANCEL")

        form_layout =  """
FORM;ACCOUNTCONFLICT_FORM;Account Conflict Report
GROUP
HEADER;Account Conflict Report;
GROUP
FIELD;STARTDATE;Start
FIELD;ENDDATE;End
FIELD;ACCOUNT;Account
FIELD;BASE;Base
FIELD;MAINCAT;Maincat
FIELD;FORMAT;Format

BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
"""

        account_conflict_form_file = tempfile.mktemp()
        f = open(account_conflict_form_file, 'w')
        f.write(form_layout)
        f.close()
        self.load(account_conflict_form_file)
        os.unlink(account_conflict_form_file)

    def getValues(self):
        """
        Function returning the values set in the form
        """
        return (self.startDate.convertIn(), self.endDate.convertIn(), self.account.valof(),
                self.base.valof(), self.maincat.valof(), self.exportFormat.valof())

def runReport():
    """
    Creates a select form
    """
    account_entry_form = AccountConflictForm("Account_Conflict")
    account_entry_form.show(1)
    if account_entry_form.loop() == Cfh.CfhOk:
        values = account_entry_form.getValues()
        startDate = values[0]
        endDate = values[1]
        account = values[2]
        base = values[3]
        maincat = values[4]
        exportFormat = values[5]

        if exportFormat == 'REPORT':
            arg = "startDate=" + startDate
            arg += " endDate=" + endDate
            arg += " account=" + account
            arg += " base=" + base
            arg += " maincat=" + maincat

            Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea,"plan","AccountConflictReport.py", 0, arg)

        elif exportFormat == 'CSV':
            duplicates = get_duplicates(startDate,endDate,account,base,maincat)

            filepath = exportToExcel(duplicates)
            tempFilePath = filepath+".temp"
            tempFile = open(tempFilePath, 'wb')
            tempFile.write("Data exported to:\n")
            tempFile.write(filepath)
            tempFile.close()
            cfhExtensions.showFile(tempFilePath, "Account Conflicts (Account: %s, Base: %s, Maincat: %s) " % (account, base, maincat))
            os.unlink(tempFilePath)
