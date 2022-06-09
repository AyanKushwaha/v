import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2015_11_11_c'

validfrom = int(AbsTime.AbsTime('01Oct2015'))
validto = int(AbsTime.AbsTime('31Dec2035'))
intartid = 'OT_CO_LATE_FC'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid': '9498',
        'validfrom': validfrom,
        'validto': validto,
        'intartid': intartid,
        'note': 'Overtime pr half hour for FD (except CJ)'
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid': '3774',
        'validfrom': validfrom,
        'validto': validto,
        'intartid': intartid,
        'note': 'Overtime pr half hour for FD'
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'SE',
        'extartid': '206',
        'validfrom': validfrom,
        'validto': validto,
        'intartid': intartid,
        'note': 'Overtime pr half hour for FD'
    }))

    print "done"
    return ops


fixit.program = 'skcms_691.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


