#!/bin/env python


"""
SASCMS-5552: load data to preferred_hotel_exc
"""

import adhoc.fixrunner as fixrunner
import os

__version__ = '1'

data = []
loadfile = open("%s/preferred_hotel_exc.dump"% os.getenv('LOG_DIR'),'rb')

for line in loadfile:
    try:
        data.append(eval(line))
    except:
        print line
    
loadfile.close()


def makeEntry(data):
    entry = {}
    
    entry['airport'] = data['airport']
    entry['region'] = data['region']
    entry['maincat'] = data['maincat']
    entry['validfrom'] = data['validfrom']
    entry['validto'] = data['validto']
    entry['hotel'] = data['hotel']
    entry['si'] = data['si']
    entry['arr_flight_nr'] = '*'
    entry['dep_flight_nr'] = '*'
    entry['week_days'] = '1234567'
    
    if data['airport_hotel'] == 1:
        entry['airport_hotel'] = 'Y'
    else:
        entry['airport_hotel'] = 'N'

    return entry


#@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    for d in data:
        e = makeEntry(d)
        if len(fixrunner.dbsearch(dc, 'preferred_hotel_exc', ' AND '.join((
            "airport='%s'" % e['airport'],
            "region='%s'" % e['region'],
            "maincat='%s'" % e['maincat'],
            "airport_hotel='%s'" % e['airport_hotel'])))) == 0:
            ops.append(fixrunner.createop('preferred_hotel_exc', 'N', e))
        else:
            print 'Entry already exists'
    
    return ops


fixit.program = 'sascms-5552_load.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
