import datetime
import getpass
import fixrunner
from salary.reasoncodes import REASONCODES


__version__ = '1.0'


EPOCH = datetime.datetime(1986, 1, 1)


def to_dave_time(dt):
    """Return now as DAVE time."""
    timestamp = dt - EPOCH
    return timestamp.days * 1440 + timestamp.seconds / 60


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    now = to_dave_time(datetime.datetime.now())
    username = getpass.getuser()

    ops = [
        fixrunner.createOp('account_set', 'N', {
            'id': 'F89',
            'si': 'F89 compensation day',
        }),
       fixrunner.createOp('activity_set', 'N', {
            'id': 'F89',
            'grp': 'CMP',
            'si': 'Compensation day for SKD crew with summer contract',
        }),
        fixrunner.createOp('activity_set_period', 'N', {
                'id': 'F89',
                'validfrom': 0,
                'validto': 18261*1440,
        }),
    ]
    
    return ops


fixit.program = 'SASCMS-3110.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
