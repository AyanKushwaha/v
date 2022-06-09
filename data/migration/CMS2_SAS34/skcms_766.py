import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2016_01_14_a'

validfrom = int(AbsTime.AbsTime('01Jan2016'))
validto = int(AbsTime.AbsTime('31Dec2035'))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid': '9166',
        'validfrom': validfrom,
        'validto': validto,
        'intartid': 'INST_CC_QA',
        'note': 'Instructor allowance for IX and IR for QA CC'
    }))
    print "done"
    return ops


fixit.program = 'skcms_766.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


