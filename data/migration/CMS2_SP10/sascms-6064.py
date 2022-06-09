"""
* Modify extartid 0425 and 3160
* Add new agreement valid from 01Sep2013

"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '2'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom = int(AbsTime('01Sep2013'))
    validto = int(AbsTime('31Dec2035'))
    validfrom_date = int(AbsDate('01Sep2013'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440

    ops = []

    ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'DK',
                                                              'extartid':'0425',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'OTPTC',
                                                              'note':'Mertid - Part time crew'}))

    ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'NO',
                                                              'extartid':'3160',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'OTPTC',
                                                              'note':'Mertid - Part time crew'}))

    ops.append(fixrunner.createOp('agreement_validity', 'N', {
            'id': 'part_time_cc_ot_validity',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': 'Mertid and overtime for part time cc validity period',
        }))

    return ops

fixit.program = 'sascms-6064.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except ValueError, err:
        print err
