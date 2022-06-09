"""
* Add entry to agreement_validity: '4exng_cc_ot_allowances' from 01Dec2012
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom_date = int(AbsDate('01Apr2013'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440

    ops = []
    ops.append(fixrunner.createOp('agreement_validity', 'N', {
            'id': 'K4ExNG_cc_cpg',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': '4EXNG CC crew planning guide',
        })),

    return ops

fixit.program = 'sascms-5833.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
