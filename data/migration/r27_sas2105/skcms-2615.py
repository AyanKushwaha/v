"""
* Add entry to agreement_validity: 'dispensation_a2_cc_new_skn' 
* Add entry to agreement_validity: 'dispensation_a2_cc_new_skd' 
* Add entry to agreement_validity: 'dispensation_a2_cc_new_sks' 
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate
from AbsTime import AbsTime

__version__ = '1'
 
@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    a_date = int(AbsDate('01Apr2021'))/1440
    b_date = int(AbsDate('31Dec2035'))/1440
    
    ops = [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'dispensation_a2_cc_new_skn',
            'validfrom':a_date,
            'validto':b_date,
            'si': 'Dispensation for A2 in SKN',
        }),
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'dispensation_a2_cc_new_skd',
            'validfrom':b_date,
            'validto':b_date,
            'si': 'Dispensation for A2 in SKD',
        }),
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'dispensation_a2_cc_new_sks',
            'validfrom':b_date,
            'validto':b_date,
            'si': 'Dispensation for A2 in SKS',
        }),
    ]

    return ops


fixit.program = 'sascms-2615.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

    
