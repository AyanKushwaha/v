"""
* Add entry to agreement_validity: 'apis_russia' from 01Dec2013
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    ops = []


    validfrom_date = int(AbsDate('01Dec2013'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440
    ops.append(fixrunner.createOp('agreement_validity', 'N', {
            'id': 'apis_russia',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': 'APIS for Russia',
        })),


    


    return ops

fixit.program = 'sascms-6255.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
