#!/bin/env python


"""
CR 4073 CCR TR FC Need value on simulator trip

* Add new simulator types for sim with external instructor.
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from RelTime import RelTime

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom= int(AbsTime('01Jan1986'))
    validto = int(AbsTime('31Dec2035'))
    ops = []
        
    ops.append(fixrunner.createop('property_set', 'N', {'id': 'meal_order_update_offset',
                                                        'si': 'The time offset before and after the meal_order_update_horizon that will be considered'}))
    
    ops.append(fixrunner.createop('property_set', 'N', {'id': 'meal_order_update_horizon',
                                                        'si': 'The time ahead that will be conidered when update meal orders'}))
        
    ops.append(fixrunner.createop('property', 'N', {'id': 'meal_order_update_horizon',
                                                    'validfrom': validfrom,
                                                    'validto': validto,
                                                    'value_rel': int(RelTime("4:00")),
                                                    'si': 'Default value'}))

    ops.append(fixrunner.createop('property', 'N', {'id': 'meal_order_update_offset',
                                                    'validfrom': validfrom,
                                                    'validto': validto,
                                                    'value_rel': int(RelTime("0:10")),
                                                    'si': 'Default value'}))

    return ops


fixit.program = 'sascms-2040.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
