"""
* Add entry to agreement_validity: '4exng_fc_ot_valid' from 01Apr2013
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '2'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    ops = []


    validfrom_date = int(AbsDate('01Apr2013'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440
    ops.append(fixrunner.createOp('agreement_validity', 'N', {
            'id': '4exng_fc_ot_valid',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': '4EXNG FC Overtime',
        })),


    


    return ops

fixit.program = 'sascms-5906.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
