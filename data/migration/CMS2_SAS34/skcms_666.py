import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2016_01_28_a'

validfrom = int(AbsTime.AbsTime('01Jan2016'))
validto = int(AbsTime.AbsTime('31Dec2035'))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_article', 'W', {
        'extsys': 'SE',
        'extartid': '356',
        'validfrom': validfrom,
        'validto': validto,
        'intartid': 'INST_NEW_HIRE',
        'note': 'Instructor - New Hire Follow Up'
    }))
    print "done"
    return ops


fixit.program = 'skcms_666.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


