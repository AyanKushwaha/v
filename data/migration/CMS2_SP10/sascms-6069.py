"""
* Adds a bunch of airports to the apt_restrictions table. All these airports
  are restricted for NEW+NEW now, regardless of A/C type.
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    ops = []

    # Airports that should be restricted for NEW+NEW (new employee at SAS)
    restricted_airports = ['SZG', 'INN', 'JKH', 'CFU', 'SMI', 'UAK', 'SFJ', 'THU', 
                           'ALF', 'KSU', 'KKN', 'LYR', 'BDU', 'EVE', 'MOL', 'RRS',
                           'TOS', 'FNC', 'HOR', 'HMV', 'GZP', 'LCY']

    for apt in restricted_airports:
        if len(fixrunner.dbsearch(dc, 'apt_restrictions', 
               "station='%s' and restr_typ='NEW' and restr_subtype='NEW'" % apt)) == 0:
            ops.append(fixrunner.createOp('apt_restrictions', 'N', {
                       'station': apt,
                       'restr_typ': 'NEW',
                       'restr_subtype': 'NEW',
                       'ac_qual': 'ALL',
            }))
        else:
            print "'%s' together with NEW+NEW already exists in table 'apt_restrictions'" % apt

    return ops

fixit.program = 'sascms-6069.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except ValueError, err:
	print err
