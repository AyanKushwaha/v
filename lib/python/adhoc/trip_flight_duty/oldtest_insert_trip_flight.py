import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file (reference SKAM-1071)
    2. Change open statements to target correct files, change dates
    3. Update __version__
    4. Run using
        $ python insert_trip_flight.py
'''
 
tripList = []
def main():
    insert_trip_flight()
    fixit()
 
def insert_trip_flight():
     with open('/opt/Carmen/CARMUSR/LIVEFEED/lib/python/adhoc/trip_flight_duty/insert_trip_flight.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            tripList.append(dict({'branchid': row[0],'trip_udor': row[1],'trip_id': row[2],'leg_udor': row[3],'leg_fd': row[4],'leg_adep': row[5],'base': row[6],'pos': row[7],'locktype': row[8]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    print(date)
 
    ops = list()
    for trip in tripList:
        print trip['branchid'],trip['trip_udor'],trip['trip_id'],trip['leg_udor'],trip['leg_fd'],trip['leg_adep']

    for trip in tripList:
        ops.append(fixrunner.createOp('trip_flight_duty', 'N', {'branchid': int(trip['branchid']),
                                                            'trip_udor': int(trip['trip_udor']),
                                                            'trip_id': trip['trip_id'],
                                                            'leg_udor': int(trip['leg_udor']),
                                                            'leg_fd': trip['leg_fd'],
                                                            'leg_adep': trip['leg_adep'],
                                                            'base': trip['base'],
                                                            'pos': trip['pos'],
                                                            'locktype': trip['locktype']}))
    return ops
 
__version__ = 'SKAM-1071l'
fixit.program = 'insert_trip_flight.py (%s)' % __version__
 
main()
