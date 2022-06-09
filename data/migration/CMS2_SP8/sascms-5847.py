"""
* Modify extartid 6048 and 6049
* Add entry to agreement_validity: '4exng_cc_ot_allowances' from 01Dec2012
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '2'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom1 = int(AbsTime('01Jan2006'))
    validto1 = int(AbsTime('01Apr2013'))
    validfrom = int(AbsTime('01Apr2013'))
    validto = int(AbsTime('31Dec2035'))
    ops = []

    if len(fixrunner.dbsearch(dc, 'salary_article', "extsys='NO' and extartid='6049' and validfrom=%i"%validfrom1)) == 0:
        
        ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'NO',
                                                              'extartid':'6049',
                                                              'validfrom':validfrom1,
                                                              'validto':validto,
                                                              'intartid':'TEMPDAY',
                                                              'note':'Temporary crew days'}))
    else:
        print "NO, 6049, %s already exist. Updating instead."%AbsTime(validfrom1)
        ops.append(fixrunner.createOp('salary_article', 'U', {'extsys':'NO',
                                                              'extartid':'6049',
                                                              'validfrom':validfrom1,
                                                              'validto':validto,
                                                              'intartid':'TEMPDAY',
                                                              'note':'Temporary crew days'}))

    ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'NO',
                                                              'extartid':'6048',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'TEMPCREW',
                                                              'note':'Temporary crew hours'}))

    validfrom_date = int(AbsDate('01Apr2013'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440
    ops.append(fixrunner.createOp('agreement_validity', 'N', {
            'id': '4exng_cc_tempcrew',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': '4EXNG CC temp crew',
        })),


    


    return ops

fixit.program = 'sascms-5847.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
