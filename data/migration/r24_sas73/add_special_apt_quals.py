#!/bin/env python


"""
SKCMS-1779 Tweak qualifications for some crew.
Sprint: SAS68
"""


import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
from adhoc.fixrunner import OnceException
from AbsTime import AbsTime


__version__ = '2018-06-01'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('crew_qual_acqual', 'N', {'crew': '37621', 'qual_typ': 'ACQUAL', 'qual_subtype' : 'A3A4', 'acqqual_typ' : 'AIRPORT', 'acqqual_subtype' : 'KKN', 'validfrom' : int(AbsTime('01JAN2012')), 'validto' : int(AbsTime('01OCT2019')), 'si' : 'Added in SKCMS-1779'}))
    ops.append(fixrunner.createOp('crew_qualification', 'D', {'crew': '37621', 'qual_typ' : 'AIRPORT', 'qual_subtype' : 'KKN', 'validfrom' : int(AbsTime('01JAN2012'))}))

    ops.append(fixrunner.createOp('crew_qual_acqual', 'N', {'crew': '37621', 'qual_typ': 'ACQUAL', 'qual_subtype' : 'A3A4', 'acqqual_typ' : 'AIRPORT', 'acqqual_subtype' : 'LYR', 'validfrom' : int(AbsTime('01MAY2012')), 'validto' : int(AbsTime('01JUN2019')), 'si' : 'Added in SKCMS-1779'}))
    ops.append(fixrunner.createOp('crew_qualification', 'D', {'crew': '37621', 'qual_typ' : 'AIRPORT', 'qual_subtype' : 'LYR', 'validfrom' : int(AbsTime('01MAY2012'))}))

    ops.append(fixrunner.createOp('crew_qual_acqual', 'N', {'crew': '11775', 'qual_typ': 'ACQUAL', 'qual_subtype' : 'A3A4', 'acqqual_typ' : 'AIRPORT', 'acqqual_subtype' : 'LYR', 'validfrom' : int(AbsTime('01JAN2012')), 'validto' : int(AbsTime('01OCT2018')), 'si' : 'Added in SKCMS-1779'}))
    ops.append(fixrunner.createOp('crew_qualification', 'D', {'crew': '11775', 'qual_typ' : 'AIRPORT', 'qual_subtype' : 'LYR', 'validfrom' : int(AbsTime('01JAN2012'))}))

    ops.append(fixrunner.createOp('crew_qual_acqual', 'N', {'crew': '13235', 'qual_typ': 'ACQUAL', 'qual_subtype' : 'A3A4', 'acqqual_typ' : 'AIRPORT', 'acqqual_subtype' : 'US', 'validfrom' : int(AbsTime('28OCT2013')), 'validto' : int(AbsTime('01NOV2018')), 'si' : 'Added in SKCMS-1779'}))
    ops.append(fixrunner.createOp('crew_qualification', 'D', {'crew': '13235', 'qual_typ' : 'AIRPORT', 'qual_subtype' : 'US', 'validfrom' : int(AbsTime('28OCT2013'))}))

    ops.append(fixrunner.createOp('crew_qual_acqual', 'N', {'crew': '10993', 'qual_typ': 'ACQUAL', 'qual_subtype' : 'A3A4', 'acqqual_typ' : 'AIRPORT', 'acqqual_subtype' : 'US', 'validfrom' : int(AbsTime('02NOV2009')), 'validto' : int(AbsTime('01JAN2036')), 'si' : 'Added in SKCMS-1779'}))
    ops.append(fixrunner.createOp('crew_qualification', 'D', {'crew': '10993', 'qual_typ' : 'AIRPORT', 'qual_subtype' : 'US', 'validfrom' : int(AbsTime('02NOV2009'))}))
    return ops


fixit.program = 'add_special_apt_quals.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
