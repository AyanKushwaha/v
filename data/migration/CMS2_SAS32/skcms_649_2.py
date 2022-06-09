import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2015_12_17'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = [
        fixrunner.createOp('agreement_validity', 'W', {
                    'id': 'ib6_valid',
                    'validfrom': int(AbsTime('17Dec2015'))/60/24,
                    'validto': int(AbsTime('31Dec2035'))/60/24,
                    'si': 'Switch to new rules for interbids 6'
        }),

    ]
    return ops


fixit.program = 'skcms_649_2.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
