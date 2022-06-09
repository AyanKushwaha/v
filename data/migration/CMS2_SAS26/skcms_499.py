

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2015-04_20_'


def addRow(ops, id, desc):
    ops.append(fixrunner.createOp('agmt_group_set', 'N', {
        'id': id,
        'validfrom': timestart,
        'validto': timeend,
        'si': desc
    }))



@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'S2',
        'extartid':'070',
        'validfrom': int(AbsTime('01FEB2015 00:00')),
        'validto':  int(AbsTime('31DEC2035 00:00')),
        'intartid': 'INST_NEW_HIRE',
        'note': 'Instructor - New Hire Follow Up'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'0720',
        'validfrom': int(AbsTime('01FEB2015 00:00')),
        'validto':  int(AbsTime('31DEC2035 00:00')),
        'intartid': 'INST_NEW_HIRE',
        'note': 'Instructor - New Hire Follow Up'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'3222',
        'validfrom': int(AbsTime('01FEB2015 00:00')),
        'validto':  int(AbsTime('31DEC2035 00:00')),
        'intartid': 'INST_NEW_HIRE',
        'note': 'Instructor - New Hire Follow Up'
    }))



    print "done"
    return ops


fixit.program = 'skcms_499.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


