"""
SASCMS-2289 - New rules for AST simulators needs starting and ending date

This script will add two new records to property:
"""

import fixrunner as fixrunner
import datetime


__version__ = '$Revision$'

# Time management stuff
EPOCH = datetime.datetime(1986, 1, 1)

def to_dave_date(dt):
    """Return now as DAVE date."""
    timestamp = dt - EPOCH
    return timestamp.days*24*60
    
#validfrom = to_dave_date(datetime.datetime(2010, 5, 1))
#validto = to_dave_date(datetime.datetime(2035, 12, 31))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('property_set', 'N', {
            'id':'ast_period_start',
            'si':'Date for AST sim session to be started',
        }),
        fixrunner.createOp('property_set', 'N', {
            'id': 'ast_period_end',
            'si': 'Date for AST sim session to be finished',
        }),
   
    ]


fixit.program = 'sascms-2289.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
