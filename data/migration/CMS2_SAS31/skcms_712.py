import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2015_11_13_e'

validfrom = int(AbsTime('01Dec2015'))/60/24
validto = int(AbsTime('31Dec2035'))/60/24


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'rule_R441B_FC',
            'validfrom': validfrom,
            'validto': validto,
            'si': 'Activation date for rule resched_R441_FC - Jira SKCMS-527/712'
        }),
    ]

    print "done"
    return ops


fixit.program = 'skcms_712.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


