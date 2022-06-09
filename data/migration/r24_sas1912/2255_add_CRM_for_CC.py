"""
SKCMS-2255 Add CMR course document for Cabin Crew. CRMC and OCRC valid from 1 January 2020
Release: SAS1912
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-11-18_a'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))

validfrom = val_date("01Jan2020 00:00")
validto = val_date("31Dec2035 00:00")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('activity_set', 'N', {'id': 'CRMC', 'grp': 'CRM', 'si': 'CRM for CC', 'recurrent_typ': ''}))
    ops.append(fixrunner.createOp('activity_set', 'N', {'id': 'OCRC', 'grp': 'CRM', 'si': 'Basic/refr CRM CC', 'recurrent_typ': ''}))
    ops.append(fixrunner.createOp('activity_set_period', 'N', {'id': 'CRMC', 'validfrom': validfrom, 'validto': validto, 'si': ''}))
    ops.append(fixrunner.createOp('activity_set_period', 'N', {'id': 'OCRC', 'validfrom': validfrom, 'validto': validto, 'si': ''}))


    return ops


fixit.program = '2255_add_CRM_for_CC.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
