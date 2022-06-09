

import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2015-04_10_'


def addRow(ops, id, desc):
    ops.append(fixrunner.createOp('agmt_group_set', 'N', {
        'id': id,
        'validfrom': timestart,
        'validto': timeend,
        'si': desc
    }))




@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('crew_log_acc_set', 'N', {
        'acc_type': "oagblkhrs",
        'is_reltime':True,
        'si': "Block Time Other Airlines"
    }))

    print "done"
    return ops


fixit.program = 'skcms_410.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


