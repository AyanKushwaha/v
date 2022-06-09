"""
* Modify extartid 6048 and 6049
* Add entry to agreement_validity: '4exng_cc_ot_allowances' from 01Dec2012
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom = int(AbsTime('01May2013'))
    validto = int(AbsTime('31Dec2035'))
    ops = []


    ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'SE',
                                                              'extartid':'372',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'INST_LCI_LH',
                                                              'note':'Instructor - LCI (LH)'}))

    ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'DK',
                                                              'extartid':'0512',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'INST_LCI_LH',
                                                              'note':'Instructor - LCI (LH)'}))

    ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'NO',
                                                              'extartid':'3482',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'INST_LCI_LH',
                                                              'note':'Instructor - LCI (LH)'}))

    return ops

fixit.program = 'sascms-5913.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
