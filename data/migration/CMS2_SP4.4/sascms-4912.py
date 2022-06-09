"""
CR 470 - No MDC CC SKN

* Add entry to agreement_validity: 'no_mdc_skn' from 01May2012
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom = int(AbsDate('01May2012'))/1440
    validto = int(AbsDate('31Dec2035'))/1440
    
    ops = [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'no_mdc_skn',
            'validfrom':validfrom,
            'validto':validto,
            'si': 'No MDC allowance SKN CC',
        }),
    ]
    return ops


fixit.program = 'sascms-4912.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

