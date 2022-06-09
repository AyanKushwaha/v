import adhoc.fixrunner as fixrunner

__version__ = '2015_12_15_b'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = [
        fixrunner.createOp('activity_set', 'W', {
            'id': 'FW',
            'grp': 'FRE',
            'si': 'Prioritized free weekend'
        }),
        fixrunner.createOp('bid_periods_type_set', 'W', {
            'bid_type': 'C_FW',
        }),
    ]
    return ops


fixit.program = 'skcms_649.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
