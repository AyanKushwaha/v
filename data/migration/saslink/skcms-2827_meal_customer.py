"""
SKCMS-2827: Add meal customer for link crew
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-02-24'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01Mar2022")
valid_to = val_date("31Dec2033")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()

    print("Adding new records for SAS link with region %s", 'SVS')
    

    for row in fixrunner.dbsearch(dc, 'meal_customer', "region='%s'" % ('SKD')):
        #Create the new row to be inserted
        new = {'company': 'SVS',
            'region': 'SVS',
            'department' : row['department'],
            'phone1': '46 8797 4744',
            'phone2': '46 8797 4765',
            'email': row['email'],
            'invoicecompanyname': 'SAS Link AB',
            'invoicecontrolstaff': 'Ref CCC111/On Board/STONM',   
            'invoiceaddrname': 'SAS Link',
            'invoiceaddrline1': 'FE5819',
            'invoiceaddrline2': 'SE-195 87 Stockholm',
            'invoiceaddrline3': row['invoiceaddrline3'],
            'si': 'Added for SAS Link'}                               
        try:
            #Add new row if don't exists
            ops.append(fixrunner.createop("meal_customer", "N", new))    
        except RuntimeError:
            print ("Error in updating the data")  
    
    return ops   
    

fixit.program = 'skcms-2827_meal_customer.py (%s)' % __version__
if __name__ == '__main__':
    fixit()