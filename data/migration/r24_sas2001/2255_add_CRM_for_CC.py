"""
SKCMS-2255 Add CMR course document for Cabin Crew. CRMC and OCRC valid from 1 January 2020
Release: SAS2001
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2020-01-23'

def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2020")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []


    ops.append(fixrunner.createOp('activity_group', 'N', {'id': 'CRMC', 'cat': 'REC', 'si': 'Recurrent training (CC)'}))
    ops.append(fixrunner.createOp('activity_group_period', 'N', {'id': 'CRMC', 'validfrom': validfrom*24*60, 'validto': validto*24*60, 'si': 'Recurrent training (CC)', 'fct': 0, 'sct': 0, 'fbt': 0, 'sbt': 0, 'fdt': 0, 'sdt': 0, 'onduty': True, 'npp': False, 'dayoff': False, 'color': 6, 'nodutylimitations': False, 'validfreeday': False, 'validptfreeday': False, 'freeweekend': False}))
    ops.append(fixrunner.createOp('activity_set_period', 'N', {'id': 'CRMC', 'validfrom': validfrom, 'validto': validto, 'si': ''}))
    ops.append(fixrunner.createOp('activity_set_period', 'N', {'id': 'OCRC', 'validfrom': validfrom, 'validto': validto, 'si': ''}))
    ops.append(fixrunner.createOp('activity_set', 'N', {'id': 'CRMC', 'grp': 'CRMC', 'si': 'CRM for CC', 'recurrent_typ': 'CRMC'}))
    ops.append(fixrunner.createOp('activity_set', 'N', {'id': 'OCRC', 'grp': 'CRMC', 'si': 'Basic/refr CRM CC', 'recurrent_typ': 'OCRC'}))
    ops.append(fixrunner.createOp('cabin_training', 'N', {'taskcode': 'OCRC', 'validfrom': validfrom, 'validto': validto, 'base': None, 'qualgroup': 'ANY', 'typ': 'REF'}))


    return ops

fixit.program = '2255_add_CRM_for_CC.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
