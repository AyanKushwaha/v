import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file (reference SASINC0242139)
    2. Change open statements to target correct files, change dates
    3. Update __version__
    4. Run using
        $ python insert_spc_schedules.py
'''
 
CrewSeniority = []
def main():
    insert_crew_seniority()
    fixit()
 
def insert_crew_seniority():
    with open('./insert_crew_seniority.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            CrewSeniority.append(dict({'id': row[0],'grp': row[1],'seniority': row[2],'si': row[3]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    time = AbsTime(date[:14])
    # rate = -100

    format = "%d%b%Y %H:%M:%S:%f"
    tim1 = datetime(2023, 4, 1).strftime(format)
    validFrom= AbsTime(tim1[:15])
    tim2 = datetime(2035, 12, 31).strftime(format)
    validTo = AbsTime(tim2[:15])
    print(validFrom)
    print(validTo)
    ops = list()
    for crew in CrewSeniority:
        ops.append(fixrunner.createOp('crew_seniority', 'N', {'crew': crew['id'],
                                                            'grp': crew['grp'],
                                                            'validfrom': int(validFrom),
                                                            'validto': int(validTo),
                                                            'seniority': int(crew['seniority']),
               		                                    'si': crew['si']}))
    return ops
 
__version__ = 'SASINC0251680'
fixit.program = 'insert_crew_seniority.py (%s)' % __version__
 
main()
