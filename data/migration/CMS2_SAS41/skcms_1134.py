import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2016_09_23'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    validfrom = int(AbsTime('01Jan2006'))
    validto   = int(AbsTime('31Dec2034'))

    ops.append(fixrunner.createOp('salary_region', 'W', {
        'region': 'HKG',
        'extsys': 'HK',
        'validfrom': validfrom,
        'validto': validto
    }))

    ops.append(fixrunner.createOp('salary_article', 'W', {
        'extsys': 'HK',
        'extartid': '0000',
        'validfrom': validfrom,
        'validto': validto,
        'intartid': 'PERDIEM_SALDO',
        'note': 'Per Diem Saldo (dummy entry)'
    }))

    print "done"
    return ops


fixit.program = 'skcms_1134.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__

