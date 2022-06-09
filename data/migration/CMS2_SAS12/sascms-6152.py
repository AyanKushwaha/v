"""
* Add entry to agreement_validity: 'fs_ski_fc_limit_weekends' from 01Jan2014
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    ops = []


    validfrom_date = int(AbsDate('01Jan2014'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440
    ops.append(fixrunner.createOp('agreement_validity', 'N', {
            'id': 'fs_ski_fc_limit_weekends',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': 'Weekend super freedays limited to 3 per calendar year for FC SKI (see 6152)',
        })),


    


    return ops

fixit.program = 'sascms-6152.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
