import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2020_11_03'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('special_schedules_set', 'N', {
        'typ': 'LimitLHUnbid',
        'si': 'Crew bid to disregard number of LH trips restriction',
    }))

    print "done"
    return ops


fixit.program = 'skcms_2514.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


