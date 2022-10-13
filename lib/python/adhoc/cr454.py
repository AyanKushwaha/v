#!/bin/env python


"""
CR 454 - Instructor's allowance

* Add new internal article ID's for the new salary types.
"""

import datetime
import utils.dt
import fixrunner


__version__ = '$Revision$'

template = {
    'validfrom': utils.dt.dt2m(datetime.datetime(2006, 1, 1)),
    'validto': utils.dt.dt2m(datetime.datetime(2034, 12, 31)),
}

codes = {
    'INST_LCI': ({
        'DK': '0515', 
        'NO': '3480',
        'SE': '360',
    }, "Instructor - LCI"),
    'INST_LIFUS_ACT': ({
        'DK': '0676',
        'NO': '3225',
        'SE': '379',
    }, "Instructor - LIFUS/AC-training"),
    'INST_LPC_OPC_OTS': ({
        'DK': '0677',
        'NO': '3226',
        'SE': '366',
    }, "Instructor - LPC/OPC/OTS"),
    'INST_LPC_OPC_OTS_BD': ({
        'DK': 'LPCOPCOTSBD',
        'NO': 'LPCOPCOTSBD',
        'SE': 'LPCOPCOTSBD',
    }, "Instructor - LPC/OPC/OTS (Brief/Debrief)"),
    'INST_TYPE_RATING': ({
        'DK': '0679',
        'NO': '3227',
        'SE': '368',
    }, "Instructor - Type rating"),
    'INST_TYPE_RATING_BD': ({
        'DK': 'TRBD',
        'NO': 'TRBD',
        'SE': 'TBBD',
    }, "Instructor - Type rating (Brief/Debrief)"),
    'INST_CRM': ({
        'DK': '0680',
        'NO': '3228',
        'SE': '378',
    }, "Instructor - CRM"),
}


#@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for rec in fixrunner.dbsearch(dc, 'salary_article', "intartid = 'INSTR_ALLOW'"):
        ops.append(fixrunner.createop('salary_article', 'D', rec))
    for intartid in codes:
        extartids, note = codes[intartid]
        for extsys in extartids:
            op = template.copy()
            op['extsys'] = extsys
            op['intartid'] = intartid
            op['extartid'] = extartids[extsys]
            op['note'] = note
            ops.append(fixrunner.createop('salary_article', 'N', op))
    return ops


fixit.program = 'cr454.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
