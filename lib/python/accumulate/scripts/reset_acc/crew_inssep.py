import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file 
    2. Change open statements to target correct files, change dates
    3. Update __version__
    4. Run using
        $ python crew_insaug.py
'''
 
crewList = []
nam = 'accumulators.blank_days_acc'

def main():
    ins_crew()
    fixit()
 
def ins_crew():
    with open('lib/python/accumulate/scripts/reset_acc/ins_crewsep.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            crewList.append(dict({'acckey': row[0],'val': row[1]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    time = AbsTime(date[:14])
    print(time)
    # rate = -100

    format = "%d%b%Y %H:%M:%S:%f"
    ae_tim = datetime(2021, 9, 1).strftime(format)
    tim = AbsTime(ae_tim[:15])
    print(tim)
    tim1 = 18758880
 
    ops = list()

    for crew in crewList:
        ops.append(fixrunner.createOp('accumulator_int', 'N', {'name': str(nam),
                                                            'acckey': crew['acckey'],
                                                            'tim': int(tim),
                                                            'val': int(crew['val'])}))
    return ops

 
__version__ = '2021-07-26'
fixit.program = 'crew_insaug.py (%s)' % __version__
 
main()

