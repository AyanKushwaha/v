import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file (reference SKSD-10241)
    2. Change open statements to target correct files, change dates
    3. Update __version__
    4. Run using
        $ python PR_OutCorrection_Entry.py
    5. This Script create records for PR_out_correction from Jan to Apr
'''
 
corrEntries = []
def main():
    create_corrections()
    fixit()
 
def create_corrections():
    with open('/users/tcskuyadm/repo/CARMUSR/SAS-Tracking/lib/python/adhoc/pr_account_entry_correction/PR_OutCorrection.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=',', quotechar='|')
        for row in data:
            corrEntries.append(dict({'id': row[0],'NoOfPR':  row[1]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    time = AbsTime(date[:14])

    format = "%d%b%Y %H:%M:%S:%f"
    ae_tim = datetime(2023, 4, 30).strftime(format)
    tim = AbsTime(ae_tim[:15])
    reason_code = 'OUT Correction'
    ops = list()
    for corrEntry in corrEntries:
        
        temp=fixrunner.dbsearch(dc, 'crew', "id='%s'" % corrEntry['id'])
        if(temp == []):
            print("CREW ID DOES NOT EXITS -->{0}".format(corrEntry['id']))
        else:
            existingAccEntry = fixrunner.dbsearch(dc, 'account_entry', 'AND ' .join((
            "si= 'PR Correction(Jan-Apr)'",
            "deleted = 'N'",
            "next_revid = 0",
                "crew='%s'" % corrEntry['id'],
            )))
        
        if(existingAccEntry==[]):
            amount = int(corrEntry['NoOfPR']) * -100
            ops.append(fixrunner.createOp('account_entry', 'N', {'id': uuid.makeUUID64(),
                                                                'crew': corrEntry['id'],
                                                                'tim': int(tim),
                                                                'account': 'PR',
                                                                'source': 'OUT Correction',
                                                                'amount': int(amount),
                                                                'man': 'Y',
                                                                'si': 'PR Correction(Jan-Apr)',
                                                                'published': 'Y',
                                                                'rate': int(-100),
                                                                'reasoncode': reason_code,
                                                                'entrytime': int(time),
                                                                'username': utils.Names.username()}))

        else:
            amount = (int(corrEntry['NoOfPR'])-(int(existingAccEntry[0]['amount']))/100) * -100
            ops.append(fixrunner.createOp('account_entry', 'U', {'id': existingAccEntry[0]['id'],
                                                                'crew': existingAccEntry[0]['crew'],
                                                                'amount': int(amount),
                                                                'username': utils.Names.username()}))
        
    return ops
 
__version__ = 'SKCMS-3210_20230403_09'
fixit.program = 'acc_entr_corrections.py (%s)' % __version__
 
main()
