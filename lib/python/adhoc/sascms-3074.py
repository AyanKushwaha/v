#!/bin/env python


"""
SASCMS-3074 - Distribution of Resource Pool Illness Report
"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.run
@fixrunner.once
def fixit(dc, *a, **k):
    ops = []

    for rpt in ['TEMP_CREW']:
        ops += [
            fixrunner.createOp('dig_reporttype_set', 'N', {
                'maintype': 'RESOURCE_ILL_REPORT',
                'subtype': rpt
            })]

        for rcpt in ['SE']:
            ops += [
                fixrunner.createOp('dig_reportrecipient_set', 'N', {
                    'reporttype_maintype': 'RESOURCE_ILL_REPORT',
                    'reporttype_subtype':rpt,
                    'rcpttype': rcpt
                })]

    d = '$CARMDATA/REPORTS/SALARY_RELEASE/'
    ops += [
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'RESOURCE_ILL_REPORT',
            'recipient_reporttype_subtype':'TEMP_CREW',
            'recipient_rcpttype':'SE',
            'protocol':'mail',
            'target':"HRDirect.se@sas.se",
            'subject':"RESOURCE POOL ILLNESS REPORT",
        }),
        ]
    
    return ops


fixit.program = 'sascms-3074.py (%s)' % __version__


if __name__ == '__main__':
    # reverting results from earlier runs (revids)
    fixit()