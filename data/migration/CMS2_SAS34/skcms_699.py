import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2016_02_09_a'

validfrom = int(AbsTime.AbsTime('01Jan2016'))
validto = int(AbsTime.AbsTime('31Dec2035'))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('crew_restriction_set', 'W', {
        'typ': 'NEW',
        'subtype': 'ACTYPE',
        'descshort': '212',
        'desclong': 'New on AC type'
    }))
    print "done"
    return ops


fixit.program = 'skcms_699.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


