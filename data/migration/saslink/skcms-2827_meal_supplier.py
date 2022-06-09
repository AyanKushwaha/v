"""
SKCMS-2827: Add meal supplier for link crew
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-02-24_1'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01Mar2022")
valid_to = val_date("31Dec2033")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()

    print("Adding new records for SAS link with region %s", 'SVS')
    
    for row in fixrunner.dbsearch(dc, 'meal_supplier', "region='%s' and validto>=%i" % ('SKD', valid_from)):
        #Create the new row to be inserted
        new = {'supplier_id': row['supplier_id'],
            'region': 'SVS',
            'validfrom' : valid_from,
            'validto': valid_to,
            'pref_stc': row['pref_stc'],
            'company': row['company'],
            'department': row['department'],
            'station': row['station'],
            'opening_time': row['opening_time'],
            'closing_time': row['closing_time'],
            'email': row['email'],
            'pdf': row['pdf'],
            'xml': row['xml'],
            'si': 'Added for SAS Link',   
            'update_support': row['update_support'],
            'sita_email': row['sita_email']}                               
        try:
            #Add new row if don't exists
            ops.append(fixrunner.createop("meal_supplier", "N", new))        
        except RuntimeError:
            print ("Error in updating the data")
   
    return ops    

fixit.program = 'skcms-2827_meal_supplier.py (%s)' % __version__
if __name__ == '__main__':
    fixit()