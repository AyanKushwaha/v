import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file (reference SASINC0200716)
    2. Change open statements to target correct files, change dates
    3. Update __version__
    4. Run using
        $ python insert_spc_schedules.py
'''
 
spcSchedule = []
def main():
    insert_spc_schedules()
    fixit()
 
def insert_spc_schedules():
    with open('./insert_spc_schedules.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            spcSchedule.append(dict({'id': row[0],'typ': row[1],'str_val': row[2],'si': row[3]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    time = AbsTime(date[:14])
    # rate = -100

    format = "%d%b%Y %H:%M:%S:%f"
    ae_tim = datetime(2022, 1, 1).strftime(format)
    tim1 = AbsTime(ae_tim[:15])
    be_tim = datetime(2023, 2, 1).strftime(format)
    tim2 = AbsTime(be_tim[:15])
    print(tim1)
    print(tim2)
 
    ops = list()
    for schedule in spcSchedule:
        ops.append(fixrunner.createOp('special_schedules', 'N', {'crewid': schedule['id'],
                                                            'typ': schedule['typ'],
                                                            'str_val': schedule['str_val'],
                                                            'validfrom': int(tim1),
                                                            'validto': int(tim2),
               		                                    'si': schedule['si']}))
    return ops
 
__version__ = '2021-12-05'
fixit.program = 'insert_spc_schedules.py (%s)' % __version__
 
main()
