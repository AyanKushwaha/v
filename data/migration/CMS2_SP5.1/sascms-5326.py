"""
* Add entry to agreement_validity: '4exng_fc_instructor_allowance' from 01Dec2012
* Add entries to salary_article for new intartid INST_SIM and INST_SIM_BR.
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate
from AbsTime import AbsTime

__version__ = '1'
 
@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom_date = int(AbsDate('01Dec2012'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440

    validfrom = int(AbsTime('01Dec2012'))
    validto = int(AbsTime('31Dec2035'))
    
    ops = [
        fixrunner.createOp('agreement_validity', 'N', {
            'id': '4exng_fc_instructor_allowance',
            'validfrom':validfrom_date,
            'validto':validto_date,
            'si': '4EXNG FC instructor allowance',
        }),
    ]


    new_salary_articles = (
        {'extsys': 'DK',
         'validfrom': validfrom,
         'validto': validto,
         'intartid': 'INST_SIM',
         'extartid': '0717',
         'note': 'Instructor - Simulator'},
        {'extsys': 'NO',
         'validfrom': validfrom,
         'validto': validto,
         'intartid': 'INST_SIM',
         'extartid': '3229',
         'note': 'Instructor - Simulator'},
        {'extsys': 'SE',
         'validfrom': validfrom,
         'validto': validto,
         'intartid': 'INST_SIM',
         'extartid': '361',
         'note': 'Instructor - Simulator'},
        {'extsys': 'DK',
         'validfrom': validfrom,
         'validto': validto,
         'intartid': 'INST_SIM_BR',
         'extartid': '0718',
         'note': 'Instructor - Simulator (Brief/Debrief)'},
        {'extsys': 'NO',
         'validfrom': validfrom,
         'validto': validto,
         'intartid': 'INST_SIM_BR',
         'extartid': '3224',
         'note': 'Instructor - Simulator (Brief/Debrief)'},
        {'extsys': 'SE',
         'validfrom': validfrom,
         'validto': validto,
         'intartid': 'INST_SIM_BR',
         'extartid': '362',
         'note': 'Instructor - Simulator (Brief/Debrief)'},
        {'extsys': 'DK',
         'validfrom': validfrom,
         'validto': validto,
         'intartid': 'INST_LIFUS_ACT',
         'extartid': '0719',  # Replaces '0676'
         'note': 'Instructor - Simulator'},
        {'extsys': 'SE',
         'validfrom': validfrom,
         'validto': validto,
         'intartid': 'INST_LIFUS_ACT',
         'extartid': '374',  # Replaces '379'
         'note': 'Instructor - Simulator'},
        )

    validfrom_upd = int(AbsTime('01Jan2006'))
    validto_upd = int(AbsTime('30Nov2012'))
    update_salary_articles = (
        {'extsys': 'DK',
         'validfrom': validfrom_upd,
         'validto': validto_upd,
         'intartid': 'INST_LIFUS_ACT',
         'extartid': '0676',  # Replaced to by '0719'
         'note': 'Instructor - Simulator'},
        {'extsys': 'SE',
         'validfrom': validfrom_upd,
         'validto': validto_upd,
         'intartid': 'INST_LIFUS_ACT',
         'extartid': '379',  # Replaced to by '374'
         'note': 'Instructor - Simulator'},)

    for salary_article in new_salary_articles:
        ops.append(fixrunner.createOp('salary_article', 'N', salary_article))

    for salary_article in update_salary_articles:
        ops.append(fixrunner.createOp('salary_article', 'U', salary_article))
        
    return ops


fixit.program = 'sascms-5326.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

    
