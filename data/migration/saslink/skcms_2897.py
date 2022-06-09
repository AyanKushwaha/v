
import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2022-02_23_'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    #New trip areas for area_set   
    ops.append(fixrunner.createOp('area_set', 'N', {
            'id': 'FSVS',
            'ix': 54,
            'name': 'Flightdeck Link'
        }))
    ops.append(fixrunner.createOp('area_set', 'N', {
            'id': 'CSVS',
            'ix': 55,
            'name': 'Cabin Link'
        }))
    print "done"
    return ops


fixit.program = 'skcms_2897.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


