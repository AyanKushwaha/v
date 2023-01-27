import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file (reference SASINC0248548)
    2. Change open statements to target correct files, change dates
    3. Update __version__
    4. Run using
        $ python account_corrections.py
'''
 
crewList = []
def main():
    create_account_corrections()
    fixit()
 
def create_account_corrections():
    with open('./account_corrections.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            crewList.append(dict({'id': row[0],'account': row[2],'source': row[3],'amount': row[4],'man': row[5],'si': row[6],'published': row[7], 'rate': row[8],'reasoncode': row[9]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    time = AbsTime(date[:14])
    print(time)
    # rate = -100

    format = "%d%b%Y %H:%M:%S:%f"
    ae_tim = datetime(2023, 1, 1).strftime(format)
    tim = AbsTime(ae_tim[:15])
    print(tim)
 
    ops = list()
    for crew in crewList:
        ops.append(fixrunner.createOp('account_entry', 'N', {'id': uuid.makeUUID64(),
                                                            'crew': crew['id'],
                                                            'tim': int(tim),
                                                            'account': crew['account'],
                                                            'source': crew['source'],
                                                            'amount': int(crew['amount']),
                                                            'man': 'Y',
							    'si': crew['si'],
                                                            'published': 'Y',
                                                            'rate': int(crew['rate']),
                                                            'reasoncode': crew['reasoncode'],
                                                            'entrytime': int(time),
                                                            'username': utils.Names.username()}))
    return ops
 
__version__ = '2023-01-27'
fixit.program = 'account_corrections.py (%s)' % __version__
 
main()
