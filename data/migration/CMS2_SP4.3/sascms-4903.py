#!/bin/env python


"""
SASCMS-4903 SKD CC K12 rolling 90 days block hours rule - need to load 90 days historic from accumulator block_time_daily_acc
"""

import adhoc.fixrunner as fixrunner

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # New entry for accperiod three months before start in table dave_selparam.
    ops.append(fixrunner.createop('dave_selparam', 'N', {'selection': 'accperiod',
                                                         'pind': 7,
                                                         'name': 'threemonthsbefstart',
                                                         'dtype': 'A',
                                                         'lbl': 'Three months before start time'}))

    # Update accumulator_rel filter in table dave_entity_select.
    for entry in fixrunner.dbsearch(dc, 'dave_entity_select'):
        if entry['selection'] == 'accperiod' and entry['entity'] == 'accumulator_rel':
            entry['wtempl'] = "$.tim<=%:2 and (($.name not in ('accumulators.block_time_acc','accumulators.block_time_daily_acc','accumulators.subq_duty_time_acc') and $.tim>=%:3) or ($.name='accumulators.block_time_acc' and $.tim>=%:4) or ($.name in ('accumulators.subq_duty_time_acc') and $.tim>=%:6) or ($.name in ('accumulators.block_time_daily_acc') and $.tim>=%:7))"
            ops.append(fixrunner.createop('dave_entity_select', 'U', entry))

    return ops


fixit.program = 'sascms-4903.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
