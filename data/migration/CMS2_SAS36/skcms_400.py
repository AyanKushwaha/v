import adhoc.fixrunner as fixrunner

__version__ = '2016_03_07'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('crew_restriction_set', 'W', {
        'typ': 'TRAINING',
        'subtype': 'FOC',
        'descshort': '1171',
        'desclong': 'First officer candidate'
    }))
    ops.append(fixrunner.createOp('crew_restriction_set', 'W', {
        'typ': 'TRAINING',
        'subtype': 'REFR',
        'descshort': '1172',
        'desclong': 'Refresh'
    }))

    print "done"
    return ops


fixit.program = 'skcms_400.py (%s)' % __version__

if __name__ == '__main__':
    fixit()

