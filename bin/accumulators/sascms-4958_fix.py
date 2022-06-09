"""
* Populates accumulator nr_planned_instr_sim_duty_acc with
  data from nr_actual_instr_sim_duty_acc
"""

import adhoc.fixrunner as fixrunner
import os
from AbsTime import AbsTime

__version__ = '1'

#@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    acc_from = int(AbsTime("01Oct2012"))
    acc_to   = int(AbsTime("01Dec2012"))

    entries = fixrunner.dbsearch(dc, 'accumulator_int', "name='accumulators.nr_actual_instr_sim_duty_acc' and tim>=%s and tim<=%s"% (acc_from,acc_to))

    for entry in entries:
        if len(fixrunner.dbsearch(dc, 'accumulator_int', "name='accumulators.nr_planned_instr_sim_duty_acc' and acckey='%s' and tim='%d'" % (entry['acckey'], entry['tim']))) == 0:
            op = fixrunner.createOp('accumulator_int', 'N', {
                                    'name'  : 'accumulators.nr_planned_instr_sim_duty_acc',
                                    'acckey': entry['acckey'],
                                    'tim'   : entry['tim'],
                                    'val'   : entry['val']})
            ops.append(op)
        else:
            print "An entry like this already exists:\n%s"%entry


    return ops


fixit.program = 'sascms-4958_fix.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
