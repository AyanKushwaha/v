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
     with open('/users/tcskuyadm/repo/CARMUSR/SAS-Tracking/lib/python/adhoc/delete_account_entry/records_to_be_removed.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            accountList.append(dict({'id': row[0],'crew': row[1]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    print(date)
 
    ops = list()



    for account in accountList:
        ops.append(fixrunner.createOp('account_entry', 'D', {'id': str(account['id']),
                                                            'crew': int(account['crew']),
                                                            }))
    return ops
 
__version__ = 'SKCMS-3361_20230526_03'
fixit.program = 'remove_acc_entry_records.py (%s)' % __version__
 
main()
