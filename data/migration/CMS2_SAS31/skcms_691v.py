import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2015_11_24_a'

validfrom = int(AbsTime('01Jan2016'))/60/24
validto = int(AbsTime('31Dec2035'))/60/24


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': 'f3_overtime_comp',
            'validfrom': validfrom,
            'validto': validto,
            'si': 'Activation or F3-overtime-replacement and OT_CO_LATE_FC. SKCMS-691'
        }),
    ]

    print "done"
    return ops


fixit.program = 'skcms_691v.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


