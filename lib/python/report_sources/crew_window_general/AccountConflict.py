from report_sources.include.AccountConflictReport import AccountConflictReport as Report
from report_sources.include.AccountConflictReport import AccountConflictForm as AccountConflictForm
import report_sources.include.AccountConflictReport as AccountConflictReport
import Cfh

class AccountConflict(Report):
    def create(self):
        account_entry_form = AccountConflictForm("Account_Conflict")
        account_entry_form.show(1)
        if account_entry_form.loop() == Cfh.CfhOk:
            values = account_entry_form.getValues()
            self.startDate = values[0]
            self.endDate = values[1]
            self.account = values[2]
            self.base = values[3]
            self.maincat = values[4]
            self.exportFormat = values[5]

            if self.exportFormat == 'REPORT':
                Report.create(self)

            elif self.exportFormat == 'CSV':
                duplicates = AccountConflictReport.get_duplicates(self.startDate,self.endDate,self.account,self.base,self.maincat)

                self.filepath = AccountConflictReport.exportToExcel(duplicates) )
                Report.createCSVReport(self)

