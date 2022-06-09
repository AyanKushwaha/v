"""
* Add entry to agreement_validity: '4exng_cc_fs' from 01Jan2013
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate
from AbsTime import AbsTime

__version__ = '1'
 
@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom_date = int(AbsDate('01Jan2013'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440
    
    ops = [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': '4exng_cc_fs',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': '4EXNG CC FS Super freedays',
        }),
    ]

    return ops


fixit.program = 'sascms-5417.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

    
