

"""
Add some new salary codes that had to be introduced for CR 364.
"""

import fixrunner
import datetime


__version__ = '$Revision$'
EPOCH = datetime.datetime(1986, 1, 1)


def to_dave_time(dt):
    """Return now as DAVE time."""
    timestamp = dt - EPOCH
    return timestamp.days * 1440 + timestamp.seconds / 60
    

validstart = to_dave_time(datetime.datetime(2006, 1, 1))
validend = to_dave_time(datetime.datetime(2034, 12, 31))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('salary_article', 'N', {
            'extsys': 'NO',
            'extartid': '100',
            'validfrom': validstart,
            'validto': validend,
            'intartid': 'VA_PERFORMED',
            'note': 'Performed Vacation (with salary)',
        }),
        fixrunner.createOp('salary_article', 'N', {
            'extsys': 'NO',
            'extartid': '101',
            'validfrom': validstart,
            'validto': validend,
            'intartid': 'VA1_PERFORMED',
            'note': 'Performed Vacation (without salary)',
        }),
    ]


fixit.program = 'cr346.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
