"""
SKCMS-2827: Add meal airport for link crew
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-02-24_3'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01Mar2022")
valid_to = val_date("31Dec2033")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()

    print("Adding new records for SAS link with region %s", 'SVS')
    
    for row in fixrunner.dbsearch(dc, 'meal_airport', "region='%s' and validto>=%i" % ('SKD', valid_from)):
        #Create the new row to be inserted
        new = {'station': row['station'],
            'region': 'SVS',
            'validfrom' : valid_from,
            'validto': valid_to,
            'mealstop_mincnx': row['mealstop_mincnx'],
            'rest_open': row['rest_open'],
            'rest_close': row['rest_close'],
            'si': 'Added for SAS Link',   
            'meal_in_ac_mincnx': row['meal_in_ac_mincnx']}                               
        try:
            #Add new row
            ops.append(fixrunner.createop("meal_airport", "N", new))       
        except RuntimeError:
            print ("Error in updating the data")
    
    return ops   
    

fixit.program = 'skcms-2827_meal_airport.py (%s)' % __version__
if __name__ == '__main__':
    fixit()