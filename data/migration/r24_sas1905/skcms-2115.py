#!/bin/env/python

"""
SKCMS-2115 Cabin crew training for A350 part 2
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2019-05-22'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    validfrom = int(AbsTime('1JUL2019'))
    validto = int(AbsTime('31JAN2020'))
    si_str = 'Safety training'
    parameters = [{'id': 'ofdx_agmt_groups_TW99',
                   'value_str': 'SKD_CC_AG;SKS_CC_AG;NKF_CC_AG;SNK_CC_AG',
                   'validfrom': validfrom,
                   'validto': validto,
                   'si': si_str},
                  {'id': 'ofdx_qualifications_TW99',
                   'value_str': 'ACQUAL+AL',
                   'validfrom': validfrom,
                   'validto': validto,
                   'si': si_str},
                  {'id': 'ofdx_attend_goal_TW99',
                   'value_int': 1,
                   'validfrom': validfrom,
                   'validto': validto,
                   'si': si_str},
                  {'id': 'ofdx_attend_limit_TW99',
                   'value_int': 1,
                   'validfrom': validfrom,
                   'validto': validto,
                   'si': si_str},
                  {'id': 'ofdx_name_TW99',
                   'value_str': 'Safety training',
                   'validfrom': validfrom,
                   'validto': validto,
                   'si': si_str},
                  {'id': 'ofdx_period_start_TW99',
                   'value_abs': validfrom,
                   'validfrom': validfrom,
                   'validto': validto,
                   'si': si_str},
                  {'id': 'ofdx_period_end_TW99',
                   'value_abs': validto,
                   'validfrom': validfrom,
                   'validto': validto,
                   'si': si_str}]
    for parameter in parameters:
        ops.append(fixrunner.createOp('property_set', 'N',
                                      {'id': parameter['id'],
                                       'si': parameter['si']}))
        ops.append(fixrunner.createOp('property', 'N',
                                      parameter))
    return ops


fixit.program = 'skcms-2115.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
