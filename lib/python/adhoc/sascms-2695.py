#/usr/bin/env python
# @(#) $

"""
SASCMS-2695 Max duty 47,5 hrs in 7x24 rolling periods to be effective from 01Jul 2010.

* Add entry to agreement_validity:
    'overtime_7x24_fd_sks' and 'overtime_7x24_fd_skd' from 01Jul2010
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

validfrom = to_dave_date(datetime.datetime(2010, 7, 1))
validto = to_dave_date(datetime.datetime(2035, 12, 31))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'overtime_7x24_fd_sks',
            'validfrom':validfrom,
            'validto':validto,
            'si': 'SKS Max 47,5 hrs in 7x24 rolling periods'
        }),
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'overtime_7x24_fd_skd',
            'validfrom':validfrom,
            'validto':validto,
            'si': 'SKD Max 47,5 hrs in 7x24 rolling periods'
        }),
    ]


fixit.program = 'sascms-2695.py'


if __name__ == '__main__':
    fixit()

