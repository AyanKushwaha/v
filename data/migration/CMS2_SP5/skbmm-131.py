#!/bin/env python

"""
SKBMM-131 Handle bid periods i CMS
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    groups = ["FD SH VG","FD SH FG", "FD LH", "CC SKN VG", "CC SKN FG", "CC SKS VG", "CC SKS FG", "CC SKD VG", "CC SKD FG", "FD SH", "FD ALL", "CC SKN", "CC SKS", "CC SKD", "CC ALL", "ALL"]
    types = ["standard", "A_FS", "B_F7S"]
    periods = [{"bid_group": "ALL", "period_start": int(AbsTime("20130101 00:00")), "period_end": int(AbsTime("20130131 23:59")) + 1, "window_open": int(AbsTime("20121106 00:00")), "window_close": int(AbsTime("20121205 23:59")) + 1, "bid_type": "standard"},
               {"bid_group": "ALL", "period_start": int(AbsTime("20130201 00:00")), "period_end": int(AbsTime("20130228 23:59")) + 1, "window_open": int(AbsTime("20121206 00:00")), "window_close": int(AbsTime("20130105 23:59")) + 1, "bid_type": "standard"},

               {"bid_group": "FD LH", "period_start": int(AbsTime("20130106 00:00")), "period_end": int(AbsTime("20130405 23:59")) + 1, "window_open": int(AbsTime("20121026 00:00")), "window_close": int(AbsTime("20121125 23:59")) + 1, "bid_type": "A_FS"},
               {"bid_group": "FD LH", "period_start": int(AbsTime("20130206 00:00")), "period_end": int(AbsTime("20130505 23:59")) + 1, "window_open": int(AbsTime("20121126 00:00")), "window_close": int(AbsTime("20121225 23:59")) + 1, "bid_type": "A_FS"},
               {"bid_group": "FD LH", "period_start": int(AbsTime("20130306 00:00")), "period_end": int(AbsTime("20130605 23:59")) + 1, "window_open": int(AbsTime("20121226 00:00")), "window_close": int(AbsTime("20130125 23:59")) + 1, "bid_type": "A_FS"},

               {"bid_group": "FD SH", "period_start": int(AbsTime("20130106 00:00")), "period_end": int(AbsTime("20130705 23:59")) + 1, "window_open": int(AbsTime("20121026 00:00")), "window_close": int(AbsTime("20121125 23:59")) + 1, "bid_type": "A_FS"},
               {"bid_group": "FD SH", "period_start": int(AbsTime("20130206 00:00")), "period_end": int(AbsTime("20130805 23:59")) + 1, "window_open": int(AbsTime("20121126 00:00")), "window_close": int(AbsTime("20121225 23:59")) + 1, "bid_type": "A_FS"},
               {"bid_group": "FD SH", "period_start": int(AbsTime("20130306 00:00")), "period_end": int(AbsTime("20130905 23:59")) + 1, "window_open": int(AbsTime("20121226 00:00")), "window_close": int(AbsTime("20130125 23:59")) + 1, "bid_type": "A_FS"},
 
               {"bid_group": "CC SKD", "period_start": int(AbsTime("20130106 00:00")), "period_end": int(AbsTime("20131205 23:59")) + 1, "window_open": int(AbsTime("20121106 00:00")), "window_close": int(AbsTime("20121205 23:59")) + 1, "bid_type": "A_FS"},
               {"bid_group": "CC SKD", "period_start": int(AbsTime("20130206 00:00")), "period_end": int(AbsTime("20140105 23:59")) + 1, "window_open": int(AbsTime("20121206 00:00")), "window_close": int(AbsTime("20130105 23:59")) + 1, "bid_type": "A_FS"},

               {"bid_group": "CC SKN", "period_start": int(AbsTime("20130106 00:00")), "period_end": int(AbsTime("20130805 23:59")) + 1, "window_open": int(AbsTime("20121102 00:00")), "window_close": int(AbsTime("20121201 23:59")) + 1, "bid_type": "A_FS"},
               {"bid_group": "CC SKN", "period_start": int(AbsTime("20130206 00:00")), "period_end": int(AbsTime("20130905 23:59")) + 1, "window_open": int(AbsTime("20121202 00:00")), "window_close": int(AbsTime("20130101 23:59")) + 1, "bid_type": "A_FS"},

               {"bid_group": "CC SKS", "period_start": int(AbsTime("20130201 00:00")), "period_end": int(AbsTime("20130430 23:59")) + 1, "window_open": int(AbsTime("20121106 00:00")), "window_close": int(AbsTime("20121205 23:59")) + 1, "bid_type": "A_FS"},
               {"bid_group": "CC SKS", "period_start": int(AbsTime("20130301 00:00")), "period_end": int(AbsTime("20130531 23:59")) + 1, "window_open": int(AbsTime("20121206 00:00")), "window_close": int(AbsTime("20130105 23:59")) + 1, "bid_type": "A_FS"},

               {"bid_group": "CC SKD", "period_start": int(AbsTime("20130106 00:00")), "period_end": int(AbsTime("20140105 23:59")) + 1, "window_open": int(AbsTime("20121106 00:00")), "window_close": int(AbsTime("20121205 23:59")) + 1, "bid_type": "B_F7S"},
               {"bid_group": "CC SKD", "period_start": int(AbsTime("20130206 00:00")), "period_end": int(AbsTime("20140205 23:59")) + 1, "window_open": int(AbsTime("20121206 00:00")), "window_close": int(AbsTime("20130105 23:59")) + 1, "bid_type": "B_F7S"},
                
               {"bid_group": "CC SKN", "period_start": int(AbsTime("20130106 00:00")), "period_end": int(AbsTime("20130905 23:59")) + 1, "window_open": int(AbsTime("20121102 00:00")), "window_close": int(AbsTime("20121201 23:59")) + 1, "bid_type": "B_F7S"},
               {"bid_group": "CC SKN", "period_start": int(AbsTime("20130206 00:00")), "period_end": int(AbsTime("20131005 23:59")) + 1, "window_open": int(AbsTime("20121202 00:00")), "window_close": int(AbsTime("20130101 23:59")) + 1, "bid_type": "B_F7S"},
              
               {"bid_group": "CC SKS", "period_start": int(AbsTime("20130101 00:00")), "period_end": int(AbsTime("20131231 23:59")) + 1, "window_open": int(AbsTime("20121106 00:00")), "window_close": int(AbsTime("20121205 23:59")) + 1, "bid_type": "B_F7S"},
               {"bid_group": "CC SKS", "period_start": int(AbsTime("20130201 00:00")), "period_end": int(AbsTime("20140131 23:59")) + 1, "window_open": int(AbsTime("20121206 00:00")), "window_close": int(AbsTime("20130105 23:59")) + 1, "bid_type": "B_F7S"}]
 
    for entry in fixrunner.dbsearch(dc, 'bid_periods'):
        ops.append(fixrunner.createop('bid_periods', 'D', entry))

    for entry in fixrunner.dbsearch(dc, 'bid_periods_group_set'):
        ops.append(fixrunner.createop('bid_periods_group_set', 'D', entry))    

    for entry in fixrunner.dbsearch(dc, 'bid_periods_type_set'):
        ops.append(fixrunner.createop('bid_periods_type_set', 'D', entry))
        
    for group in groups:
        ops.append(fixrunner.createop('bid_periods_group_set', 'N', {'bid_group': group}))                  

    for type in types:
        ops.append(fixrunner.createop('bid_periods_type_set', 'N', {'bid_type': type}))

    for period in periods:
        ops.append(fixrunner.createop('bid_periods', 'N', dict({"id": uuid.makeUUID64()}.items() + period.items())))

    return ops

fixit.program = 'skbmm-131.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
