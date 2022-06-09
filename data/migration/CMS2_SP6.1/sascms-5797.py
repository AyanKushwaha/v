"""
* Add entry to agreement_validity: 'meal_not_too_close_cc' from 01Jun2013
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate
from AbsTime import AbsTime

__version__ = '1'
 
@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom_date = int(AbsDate('01Jun2013'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440
    
    ops = [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'meal_not_too_close_cc',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': 'Meal not too close to landing and takeoff CC (SASCMS-5797)',
        }),]

    return ops


fixit.program = 'sascms-5797.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
