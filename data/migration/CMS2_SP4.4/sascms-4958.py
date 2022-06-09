"""
* Populates accumulator nr_actual_instr_sim_duty_acc with historic data
* from file sascms-4958.dat.
"""

import adhoc.fixrunner as fixrunner
import os
from AbsTime import AbsTime

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    f = open("sascms-4958.dat")
    for line in f.readlines():
        (acckey, tim, val) = line.split(",")

        acckey = acckey.strip()
        tim = int(AbsTime(tim))
        val = int(val)

        if len(fixrunner.dbsearch(dc, 'accumulator_int', "name='accumulators.nr_actual_instr_sim_duty_acc' and acckey='%s' and tim='%d'" % (acckey, tim))) == 0:
            actual_op_type = 'N'
        else:
            actual_op_type = 'U'

        if len(fixrunner.dbsearch(dc, 'accumulator_int', "name='accumulators.nr_planned_instr_sim_duty_acc' and acckey='%s' and tim='%d'" % (acckey, tim))) == 0:
            publish_op_type = 'N'
        else:
            publish_op_type = 'U'
            
        actual_op = fixrunner.createOp('accumulator_int', actual_op_type, {
                                'name': 'accumulators.nr_actual_instr_sim_duty_acc',
                                'acckey': acckey,
                                'tim': tim,
                                'val': val})

        publish_op = fixrunner.createOp('accumulator_int', publish_op_type, {
                                'name': 'accumulators.nr_planned_instr_sim_duty_acc',
                                'acckey': acckey,
                                'tim': tim,
                                'val': val})

        ops.append(actual_op)
        ops.append(publish_op)
        
    f.close()
    
    return ops


fixit.program = 'sascms-4958.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
