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
        $ python crew_upd.py
'''
 
crewList = []

def main():
    upd_crew()
    fixit()
 
def upd_crew():
    with open('lib/python/accumulate/scripts/reset_acc/del_crew.csv') as csvFile:
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
    ae_tim = datetime(2021, 7, 1).strftime(format)
    tim = AbsTime(ae_tim[:15])
    print(tim)
    tim1 = 18669600
 
    ops = []
    for crew in crewList:
        for entry in fixrunner.dbsearch(dc, 'accumulator_int', ' AND '.join((
                "name = 'accumulators.blank_days_acc'",
                "acckey = %s" % crew['acckey'],
                "deleted = 'N'",
                "to_char(tim) in ('18669600','18626400','18581760','18538560','18493920','18453600','18408960')",
                "next_revid = 0",
            ))):
            entry['val'] = 0
            ops.append(fixrunner.createOp('accumulator_int', 'U', entry))
    return ops

 
__version__ = '2021-07-26'
fixit.program = 'crew_upd.py (%s)' % __version__
 
main()
