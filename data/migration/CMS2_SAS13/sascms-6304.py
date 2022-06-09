"""
* Add entries to meal_prohibit_type_set and meal_prohibit_flight
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '1'

#@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    ops = []


    validfrom_date = int(AbsDate('01Jan2014'))/1440
    validto_date = int(AbsDate('31Dec2035'))/1440
    
    ops.append(fixrunner.createOp('meal_prohibit_type_set', 'N', {
            'id': 'Route',
            'si': 'Eg. CPH-LIN',
        }))
    ops.append(fixrunner.createOp('meal_prohibit_type_set', 'N', {
            'id': 'Flight',
            'si': 'Eg. SK 0401',
        }))
    ops.append(fixrunner.createOp('meal_prohibit_type_set', 'N', {
            'id': 'AC-type',
            'si': 'Eg. CR9',
        }))
    ops.append(fixrunner.createOp('meal_prohibit_flight', 'N', {
            'maincat': 'C',
            'region': '*',
            'type': 'AC-type',
            'identifier': 'CR9',
            'validfrom': validfrom_date,
            'validto': validto_date,
            'si': 'Prohibit meal on CRJ for cabin crew',
        }))

    return ops

fixit.program = 'sascms-6304.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
