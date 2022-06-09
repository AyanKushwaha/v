#/usr/bin/env python

"""
CR 470 - No MDC CC SKD

* Add entry to agreement_validity: 'no_mdc_skd' from 01Mar2010
"""

import datetime
import getpass
import fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

EPOCH = datetime.datetime(1986, 1, 1)

def to_dave_date(dt):
    """Return now as DAVE date."""
    timestamp = dt - EPOCH
    return timestamp.days

validfrom = to_dave_date(datetime.datetime(2010, 3, 1))
validto = to_dave_date(datetime.datetime(2035, 12, 31))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'no_mdc_skd',
            'validfrom':validfrom,
            'validto':validto,
            'si': 'No MDC allowance SKD CC',
        }),
    ]
    return ops


fixit.program = 'cr470.py'


if __name__ == '__main__':
    fixit()

