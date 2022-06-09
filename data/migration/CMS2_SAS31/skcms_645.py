import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2015_11_19'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('special_schedules_set', 'N', {
        'typ': 'SingleFUnbid',
        'si': 'Crew bidded avoiding single freedays',
    }))

    print "done"
    return ops


fixit.program = 'skcms_645.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


