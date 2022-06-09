
import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2015-05_08_'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    #New trip areas for area_set   
    ops.append(fixrunner.createOp('area_set', 'N', {
            'id': 'FQA',
            'ix': 52,
            'name': 'Flightdeck Cimber'
        }))
    ops.append(fixrunner.createOp('area_set', 'N', {
            'id': 'CQA',
            'ix': 53,
            'name': 'Cabin Cimber'
        }))
    print "done"
    return ops


fixit.program = 'skcms_554.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


