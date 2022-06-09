#!/bin/env python


"""
 SASCMS 4143

*  Add new filter for the Meal Client update tables
"""

import adhoc.fixrunner as fixrunner

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createop('dave_entity_select', 'N', {'selection': 'standalonemeal',
                                                                 'entity' : 'meal_order_update',
                                                                 'tgt_entity' : 'meal_order_update',
                                                                 'wtempl': '$.from_date BETWEEN %:1 AND %:2'}))
    
    ops.append(fixrunner.createop('dave_entity_select', 'N', {'selection': 'standalonemeal',
                                                                 'entity' : 'meal_order_update_line',
                                                                 'tgt_entity' : 'meal_order_update',
                                                                 'wtempl': '$.order_update_num = %:3',
                                                                 'via_src_columns' : 'order_order_update_num',
                                                                 'via_tgt_columns' : 'order_update_num'}))

    return ops


fixit.program = 'sascms-4143.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
