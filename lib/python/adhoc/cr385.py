

"""
CR 385 - New rules for simulators starting and ending with passive

This script will add a new record to training_log_set:
SIM DEADHEAD
and two new records to property:

"""

import adhoc.fixrunner as fixrunner
import datetime


__version__ = '$Revision$'

# Time management stuff
EPOCH = datetime.datetime(1986, 1, 1)

def to_dave_date(dt):
    """Return now as DAVE date."""
    timestamp = dt - EPOCH
    return timestamp.days*24*60
    
validfrom = to_dave_date(datetime.datetime(2010, 5, 1))
validto = to_dave_date(datetime.datetime(2035, 12, 31))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('training_log_set', 'N', {
            'typ':'SIM DEADHEAD',
            'grp':'MISC',
            'si': ' ',
        }),
        fixrunner.createOp('property_set', 'N', {
            'id':'max_sim_duties_with_passive_SKD',
            'si': ' ',
        }),
        fixrunner.createOp('property_set', 'N', {
            'id':'max_sim_duties_with_passive_SKS',
            'si': ' ',
        }),
        fixrunner.createOp('property', 'N', {
            'id':'max_sim_duties_with_passive_SKD',
            'validfrom':validfrom,
            'validto':validto,
            'value_int':3,
            'si':'Max sim duties with passive flights in year, SKD',
        }),
        fixrunner.createOp('property', 'N', {
            'id':'max_sim_duties_with_passive_SKS',
            'validfrom':validfrom,
            'validto':validto,
            'value_int':2,
            'si':'Max sim duties with passive flights in year, SKS',
        }),
    ]


fixit.program = 'cr385.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
