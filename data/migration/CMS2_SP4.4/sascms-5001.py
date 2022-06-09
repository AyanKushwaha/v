"""
* Add entry to agreement_validity: 'K12_SKS_CC' from 01Dec2012
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom = int(AbsDate('01Dec2012'))/1440
    validto = int(AbsDate('31Dec2035'))/1440
    
    ops = [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'K12_SKS_CC',
            'validfrom':validfrom,
            'validto':validto,
            'si': 'K12 SKS CC',
        }),
    ]
    return ops


fixit.program = 'sascms-5001.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

