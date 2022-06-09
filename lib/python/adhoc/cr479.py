

"""
Add rave parameterset data that had to be introduced for CR 479.
"""

import adhoc.fixrunner as fixrunner
import datetime

__version__ = '$Revision$'

# Time management stuff
EPOCH = datetime.datetime(1986, 1, 1)

def to_dave_date(dt):
    """Return now as DAVE date."""
    timestamp = dt - EPOCH
    return timestamp.days
    
validfrom = to_dave_date(datetime.datetime(1986, 1, 1))
validto = to_dave_date(datetime.datetime(2035, 12, 31))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('rave_paramset_set', 'N', {
            'id': 'sim_requiring_min_sfe',
            'description': 'FFS task codes that require min SFE instructor',
        }),
        fixrunner.createOp('rave_paramset_set', 'N', {
            'id': 'sim_requiring_tri',
            'description': 'FFS task codes that require TRI instructor',
        }),
        fixrunner.createOp('rave_string_paramset', 'N', {
            'ravevar': 'sim_requiring_min_sfe',
            'val': 'C441',
            'validfrom':validfrom,
            'validto':validto,
        }),
        fixrunner.createOp('rave_string_paramset', 'N', {
            'ravevar': 'sim_requiring_min_sfe',
            'val': 'C631',
            'validfrom':validfrom,
            'validto':validto,
        }),
        fixrunner.createOp('rave_string_paramset', 'N', {
            'ravevar': 'sim_requiring_min_sfe',
            'val': 'C221',
            'validfrom':validfrom,
            'validto':validto,
        }),
        fixrunner.createOp('rave_string_paramset', 'N', {
            'ravevar': 'sim_requiring_tri',
            'val': 'C443',
            'validfrom':validfrom,
            'validto':validto,
        }),
        fixrunner.createOp('rave_string_paramset', 'N', {
            'ravevar': 'sim_requiring_tri',
            'val': 'C633',
            'validfrom':validfrom,
            'validto':validto,
        }),
        fixrunner.createOp('rave_string_paramset', 'N', {
            'ravevar': 'sim_requiring_tri',
            'val': 'C223',
            'validfrom':validfrom,
            'validto':validto,
        }),
    ]


fixit.program = 'cr479.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
