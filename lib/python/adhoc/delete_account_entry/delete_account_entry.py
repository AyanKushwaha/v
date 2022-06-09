import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file (reference SASINC0217097)
    2. Change open statements to target correct files, change dates
    3. Update __version__
    4. Run using
        $ python delete_account_entry.py
'''
 
accountList = []
def main():
    delete_account_entry()
    fixit()
 
def delete_account_entry():
     with open('/opt/Carmen/CARMUSR/LIVEFEED/lib/python/adhoc/delete_account_entry/delete_account_entry.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            accountList.append(dict({'revid': row[0],'prev_revid': row[1],'next_revid': row[2],'branchid': row[3],'id': row[4],'crew': row[5],'tim': row[6],'account': row[7]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    print(date)
 
    ops = list()



    for account in accountList:
        ops.append(fixrunner.createOp('account_entry', 'D', {'revid': int(account['revid']),
                                                            'prev_revid': int(account['prev_revid']),
                                                            'next_revid': int(account['next_revid']),
                                                            'branchid': int(account['branchid']),
                                                            'id': str(account['id']),
                                                            'crew': int(account['crew']),
                                                            'tim': int(account['tim']),
                                                            'account': str(account['account'])}))
    return ops
 
__version__ = 'INC0217097a'
fixit.program = 'delete_account_entry.py (%s)' % __version__
 
main()
