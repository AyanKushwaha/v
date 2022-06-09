"""
* Add entry to agreement_validity: '4exng_fs_day_logic' from 01Oct2013
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    ops = []


    validfrom_date = int(AbsDate('01Oct2013'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440
    ops.append(fixrunner.createOp('agreement_validity', 'N', {
            'id': '4exng_fs_day_logic',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': '4EXNG Superfreedays changes according to Jira 6102',
        })),


    


    return ops

fixit.program = 'sascms-6102.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
