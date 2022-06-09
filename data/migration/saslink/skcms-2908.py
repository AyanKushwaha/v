"""
SKCMS-2908: Add preferred Hotel for link crew
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-02-28_3'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01Mar2022")
valid_to = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()

    print("Adding new records for SAS link with region %s", 'SKD')
    
    for row in fixrunner.dbsearch(dc, 'preferred_hotel_exc', "region='%s' and validto>=%i"  % ('SKD', valid_from)):
        #Create the new row to be inserted
        new = {'airport': row['airport'],
            'region': 'SVS',
            'maincat': row['maincat'],
            'airport_hotel': row['airport_hotel'],
            'validfrom' : valid_from,
            'arr_flight_nr': row['arr_flight_nr'],
            'dep_flight_nr': row['dep_flight_nr'],
            'week_days': row['week_days'],
            'validto': valid_to,
            'hotel': row['hotel'],
            'si': row['si']}                               
        try:
            #Add new row
            ops.append(fixrunner.createop("preferred_hotel_exc", "N", new))       
        except RuntimeError:
            print ("Error in updating the data")
    
    return ops   
    

fixit.program = 'skcms-2908.py (%s)' % __version__
if __name__ == '__main__':
    fixit()