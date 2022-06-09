#!/bin/env python


"""
SASCMS-2174 - Balancing report distribution
"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.run
@fixrunner.once
def fixit(dc, *a, **k):
    ops = []
    ops += [
        fixrunner.createOp('dig_protocol_set', 'N', {
            'protocol': 'file',
            'si': 'File written to the file system',
        }),
        fixrunner.createOp('dig_protocol_set', 'N', {
            'protocol': 'mail',
            'si': 'E-mail',
        }),
        fixrunner.createOp('dig_protocol_set', 'N', {
            'protocol': 'ftp',
            'si': 'FTP upload',
        }),
    ]
    for rpt in ['*','PERDIEM','OVERTIME','TEMP_CREW','SUPERVIS']:
        ops += [
            fixrunner.createOp('dig_reporttype_set', 'N', {
                'maintype': 'BALANCING_REPORT',
                'subtype': rpt
            })]
        for rcpt in ['*','DK','SE','NO','JP','CN']:
            if rpt == 'TEMP_CREW' and rcpt != 'DK': continue
            ops += [
                fixrunner.createOp('dig_reportrecipient_set', 'N', {
                    'reporttype_maintype': 'BALANCING_REPORT',
                    'reporttype_subtype':rpt,
                    'rcpttype': rcpt
                })]
            
    ops += [
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'*',
            'recipient_rcpttype':'*',
            'protocol':'mail',
            'target':'CPHOH.Support@sas.dk',
            'si': 'Default recipient',
        }),
        ]
    return ops


fixit.program = 'sascms-2174.py (%s)' % __version__


if __name__ == '__main__':
    # reverting results from earlier runs (revids)
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
