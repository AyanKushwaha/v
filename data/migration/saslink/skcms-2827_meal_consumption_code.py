"""
SKCMS-2827: Add meal consumption codes for link crew
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-02-24_2'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01Mar2022")
valid_to = val_date("31Dec2033")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()

    print("Adding new records for SAS link with region %s", 'SVS')

    for row in fixrunner.dbsearch(dc, 'meal_consumption_code', "region='%s' and validto>='%s'" % ('SKD', valid_from)):
        #Create the new row to be inserted
        new = {'region': 'SVS',
            'maincat' : row['maincat'],
            'stc': row['stc'],
            'meal_code': row['meal_code'],
            'start_time': row['start_time'],
            'end_time': row['end_time'],
            'validfrom': valid_from,   
            'validto': valid_to,
            'cons_code': row['cons_code'],
            'si': 'Added for SAS Link'}                               
        try:
            #Add new row
            ops.append(fixrunner.createop("meal_consumption_code", "N", new))
        except RuntimeError:
            print ("Error in updating the data")
       
    return ops   
    


fixit.program = 'skcms-2827_meal_consumption_code.py (%s)' % __version__
if __name__ == '__main__':
    fixit()