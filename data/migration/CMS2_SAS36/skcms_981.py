import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2016_04_13'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    validfrom = int(AbsTime.AbsTime('01Jun2016'))
    validto = int(AbsTime.AbsTime('31Dec2035'))

    ops = []

    ops.append(fixrunner.createOp('crew_base_set', 'W', {
        'id': 'HKG',
        'airport': 'HKG',
        'country': 'CN'
    }))

    ops.append(fixrunner.createOp('crew_contract_set', 'W', {
        'id': 'V603',
        'dutypercent': 100,
        'grouptype': 'V',
        'pattern': 2575,
        'descshort': '100% V',
        'desclong': '100%',
        'noofvadays': 18,
        'bxmodule': 'C',
        'agmtgroup': 'SKK_CC_AG'
    }))

    ops.append(fixrunner.createOp('crew_contract_valid', 'W', {
        'contract': 'V603',
        'validfrom': validfrom,
        'validto': validto,
        'maincat': 'C',
        'base': 'HKG',
        'company': 'SK'
    }))

    print "done"
    return ops


fixit.program = 'skcms_981.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


