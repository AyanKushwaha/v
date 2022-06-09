"""
* Add entry to agreement_validity: '4exng_cc_ot_allowances' from 01Dec2012
* Add entry to agreement_validity: '4exng_cc_ot' from 01Jan2013
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate
from AbsTime import AbsTime

__version__ = '1'
 
@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom_date = int(AbsDate('01Dec2012'))/1440
    validfrom_dateOT = int(AbsDate('01Jan2013'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440
    
    ops = [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': '4exng_cc_ot_allowances',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': '4EXNG CC Overtime allowance',
        }),
        fixrunner.createOp('agreement_validity', 'N', {
            'id': '4exng_cc_ot',
            'validfrom':validfrom_dateOT,
            'validto':validto_date,
            'si': '4EXNG CC Overtime',
        }),
    ]

    return ops


fixit.program = 'sascms-5371.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

    
