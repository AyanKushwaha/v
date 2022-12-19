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
        $ python update_spc_schedules.py
'''
 
spcSchedule = []
def main():
    update_spc_schedules()
    fixit()
 
def update_spc_schedules():
    with open('./update_spc_schedules.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            spcSchedule.append(dict({'id': row[0],'typ': row[1],'str_val': row[2],'validfrom': row[3], 'validto': row[4]}))         
    
@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    time = AbsTime(date[:14])
    # rate = -100
    to = 19460160
    format = "%d%b%Y %H:%M:%S:%f"
    ae_tim = datetime(2023, 1, 1).strftime(format)
    tim1 = AbsTime(ae_tim[:15])
    be_tim = datetime(2024, 1, 1).strftime(format)
    tim2 = AbsTime(be_tim[:15])
    print(tim1)
    print(tim2)
 
    ops = list()
    for schedule in spcSchedule:
        for entry in fixrunner.dbsearch(dc, 'special_schedules', ' AND '.join((
            "crewid = '%s'" % schedule['id'],
            "typ = '%s'" % schedule['typ'],
            "str_val = '%s'" % schedule['str_val'],
            "validfrom = '%s'" % schedule['validfrom'],
            "validto = '%s'" % schedule['validto'],
            "next_revid = 0",
            "deleted = 'N'"
        ))):
           entry['validto'] = int(to)
           ops.append(fixrunner.createOp('special_schedules', 'U', entry))
    return ops
 
__version__ = '2022-11-24'
fixit.program = 'update_spc_schedules.py (%s)' % __version__
 
main()
