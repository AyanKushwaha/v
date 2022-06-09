import adhoc.fixrunner as fixrunner

__version__ = '2015_10_01_a'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('account_set', 'N', {
            'id': 'F9',
            'si': 'High priority F day'
        }))

    print "done"
    return ops


fixit.program = 'skcms_648.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


