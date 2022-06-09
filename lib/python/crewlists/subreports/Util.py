import crewlists.html as HTML

from utils.xmlutil import XMLElement
from salary.accounts import CrewAccountList, CrewAccountDict
from AbsTime import AbsTime

class detailsTable(HTML.table):
    """
    Creates a table with each transaction for the selected year
    """
    def __init__(self, current_account):
        """ <table>...</table> where activities are listed. """
        HTML.table.__init__(self,
                            'Updated',
                            'By',
                            'Reason code',
                            'Reason date',
                            'Comment',
                            'Amount',
                            'Balance'
                            )
        self['id'] = "details"
        self['border'] = "1"
        for entry in current_account:
            try:
                comment = ""
                if entry.si is not None:
                    comment = entry.si
                self.append(
                    "%04d-%02d-%02d" % entry.entrytime.split()[:3],
                    entry.username,
                    entry.reasoncode,
                    "%04d-%02d-%02d" % entry.tim.split()[:3],
                    comment,
                    HTML.span_right("%.2f" % (entry.value / 100.0)),
                    HTML.span_right("%.2f" % (entry.balance / 100.0))
                )
            except:
                # The record is a baseline entry.
                self.append(
                    "%04d-%02d-%02d" % entry.tim.split()[:3],
                    '',
                    'BASELINE',
                    "%04d-%02d-%02d" % entry.tim.split()[:3],
                    '',
                    HTML.span_right("%.2f" % (entry.value / 100.0)),
                    HTML.span_right("%.2f" % (entry.balance / 100.0))
                )

class summaryTable(HTML.table):
    """
    Creates a summary table.
    """
    def __init__(self,accounts):
        """ <table>...</table> for crew information.  """
        HTML.table.__init__(self,
                            'Account',
                            'Last updated',
                            'Balance'
                            )
        self['id'] = "overview"
        for account in accounts:
            last_upd = AbsTime(0)
            balance = 0
            for entry in accounts[account]:
                try:
                    if entry.entrytime > last_upd:
                        last_upd = e.entrytime
                except:
                    # Was a baseline record
                    if entry.tim > last_upd:
                        last_upd = entry.tim
                balance += entry.value
            self.append(
                account,
                "%04d-%02d-%02d %02d:%02d" % last_upd.split(),
                HTML.span_right("%.2f" % (balance / 100.0))
            )

class infoTable(HTML.table):
    """
    Creates a table with crew information.
    """
    def __init__(self, input):
        """ <table>...</table> for crew information.  """
        HTML.table.__init__(self,
                            'Employee no',
                            'Name',
                            'Account',
                            'Year'
                            )
        self['id'] = "basics"
        self.append(
            input.extperkey,
            input.logname,
            "%s" % (input.account),
            "%02d" % (input.year)
        )


def run(inputdata, filter, report_name, title):
    """ Here is where the report gets generated. """


    all_accounts_dict = CrewAccountDict(inputdata.crewid, inputdata.lastDate, filter=filter)
    current_account_data = CrewAccountList(inputdata.crewid, inputdata.account, inputdata.lastDate)

    # Add running balance
    balance = 0
    detailed_list_records = []
    for entry in current_account_data:
        balance += entry.value
        if entry.tim >= inputdata.firstDate:
            entry.balance = balance
            detailed_list_records.append(entry)

    html = HTML.html(title="%s (%s)" % (title, inputdata.extperkey), report=report_name)
    html.append(XMLElement('h1', title))
    html.append(XMLElement('h2', 'BASICS'))
    html.append(infoTable(inputdata))
    html.append(XMLElement('h2', 'OVERVIEW'))
    html.append(summaryTable(all_accounts_dict))
    html.append(XMLElement('h2', inputdata.account + " DETAILS"))
    html.append(detailsTable(detailed_list_records))

    return html