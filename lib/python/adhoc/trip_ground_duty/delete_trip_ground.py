import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file (reference SKS-483)
    2. Change open statements to target correct files, change dates
    3. Update __version__
    4. Run using
        $ python delete_trip_ground.py
'''
 
tripList = []
def main():
    delete_trip_ground()
    fixit()
 
def delete_trip_ground():
     with open('/opt/Carmen/CARMUSR/LIVEFEED/lib/python/adhoc/trip_ground_duty/delete_trip_ground.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            tripList.append(dict({'revid': row[0],'trip_udor': row[1],'trip_id': row[2],'task_udor': row[3],'task_id': row[4],'base': row[5]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    print(date)
 
    ops = list()
    for trip in tripList:
        print trip['revid'],trip['trip_udor'],trip['trip_id'],trip['task_udor'],trip['task_id'],trip['base']

    for trip in tripList:
        ops.append(fixrunner.createOp('trip_ground_duty', 'D', {'revid': int(trip['revid']),
                                                            'trip_udor': int(trip['trip_udor']),
                                                            'trip_id': str(trip['trip_id']),
                                                            'task_udor': int(trip['task_udor']),
                                                            'task_id': str(trip['task_id']),
                                                            'base': str(trip['base'])}))
    return ops
 
__version__ = 'SKS-483'
fixit.program = 'delete_trip_ground.py (%s)' % __version__
 
main()
