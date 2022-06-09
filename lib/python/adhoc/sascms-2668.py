

"""
SASCMS-2668 CR Xmas Rotations for FD LH shall not involve rot 03
This file adds two rotations in leave_rotation_order.
These rotations should then connect to two new xmas
groups in leave_rotation_set. In christmas_freedays 
these xmas groups should get some dates for 2011.
"""

import fixrunner
import datetime
import RelTime
import AbsTime

EPOCH = datetime.datetime(1986, 1, 1)

def to_dave_date(dt):
    """Return now as DAVE date."""
    timestamp = dt - EPOCH
    return timestamp.days*24*60
    
date1 = to_dave_date(datetime.datetime(2011, 12, 24))
date2 = to_dave_date(datetime.datetime(2011, 12, 31))

__version__ = '2011-01-26b'

leave_rotation_set_1A = ({'name':'01A',
                          'si':'Christmas vacation F/D. Christmas free. (LH)'})

leave_rotation_set_2A = ({'name':'02A',
                          'si':'Christmas vacation F/D. New Year free. (LH)'})

leave_rotation_order_1A = ({'rotation':'01A',
                            'nextrotation':'02A'})

leave_rotation_order_2A = ({'rotation':'02A',
                            'nextrotation':'01A'})

christmas_freedays_1A = ({'lseason_season':'F AUTUMN',
                          'lseason_planyear':2011,
                          'rotation':'01A',
                          'region':'SKI',
                          'startdate':date1,
                          'nooffreedays':1,
                          'activity':'F14'})

christmas_freedays_2A = ({'lseason_season':'F AUTUMN',
                          'lseason_planyear':2011,
                          'rotation':'02A',
                          'region':'SKI',
                          'startdate':date2,
                          'nooffreedays':1,
                          'activity':'F14'})

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops += [fixrunner.createOp('leave_rotation_set', 'N', leave_rotation_set_1A)]
    ops += [fixrunner.createOp('leave_rotation_set', 'N', leave_rotation_set_2A)]
    ops += [fixrunner.createOp('leave_rotation_order', 'N', leave_rotation_order_1A)]
    ops += [fixrunner.createOp('leave_rotation_order', 'N', leave_rotation_order_2A)]
    ops += [fixrunner.createOp('christmas_freedays', 'N', christmas_freedays_1A)]
    ops += [fixrunner.createOp('christmas_freedays', 'N', christmas_freedays_2A)]
    
    return ops

fixit.program = 'SASCMS-2668 (%s)' % __version__

if __name__ == '__main__':
    fixit()


