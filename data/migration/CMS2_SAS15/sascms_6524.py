

import adhoc.fixrunner as fixrunner
import datetime
import RelTime
import AbsTime


__version__ = '2'

accstart = int(AbsTime.AbsTime('25Mar2014'))/60/24
accend =  int(AbsTime.AbsTime('25Mar2014'))/60/24


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    op_list = []
    if len(fixrunner.dbsearch(dc, 'accumulator_int_run', "acckey='SHORT'")) == 0:
        op_list.append(fixrunner.createOp('accumulator_int_run', 'N', {
            'acckey':'SHORT',
            'accstart':accstart,
            'accend':accend,
            'accname': 'balance',
        }))
    
    return op_list

fixit.program = 'sascms_6524.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


