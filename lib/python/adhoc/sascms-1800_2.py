#!/bin/env python


"""
SASCMS-1800 - F3 -> F3S conversion job.
"""

import datetime
import adhoc.fixrunner as fixrunner
import utils.dt
import getpass

from carmensystems.basics.uuid import uuid
from salary.reasoncodes import REASONCODES

now = utils.dt.dt2m(datetime.datetime.now())
username = getpass.getuser()

__version__ = '$Revision$'

@fixrunner.once
@fixrunner.run
def fixit(dc, csv_file, *a, **k):
    """Using f3s.csv resulting from sascms-1800.py"""
    ops = []
    debug = 'debug' in k
    csvf = open(csv_file, "r")
    for line in csvf:
        if line[0].isdigit():
            parts = line.split('\t')
            crewid = parts[0]
            new_f3 = parts[7]
            new_f3s = parts[8]
            rm_f3 = parts[9]
            rm_f3s = parts[10]
            try:
                add_f3 = int(new_f3)
                add_f3s = int(new_f3s)
                if debug:
                    print "ADD     %s f3: %s, f3s: %s" % (crewid, add_f3, add_f3s)
            except:
                try:
                    add_f3 = int(rm_f3)
                    add_f3s = int(rm_f3s)
                    if debug:
                        print "REVERSE %s f3: %s, f3s: %s" % (crewid, add_f3, add_f3s)
                except:
                    print "Skipping line: [%s]" % line
                    continue
            ops.append(make_op(crewid, 'F3', add_f3))
            ops.append(make_op(crewid, 'F3S', add_f3s))
        else:
            if debug:
                print "skipping %s" % line
    csvf.close()
    return ops


def make_op(crew, account, amount):
    record = {
        'id': uuid.makeUUID64(),
        'crew': crew,
        'account': account,
        'source': 'sascms-1800_2.py',
        'amount': int(amount),
        'man': 'Y',
        'published': 'Y',
        'rate': 100 * (1, -1)[amount < 0],
        'reasoncode': REASONCODES['IN_CORR'],
        'tim': now,
        'entrytime': now,
        'username': username,
        'si': 'Correction F3->F3S conversion (SASCMS-1800)',
    }
    return fixrunner.createop('account_entry', 'N', record)


fixit.program = 'sascms-1800_2.py (%s)' % __version__


if __name__ == '__main__':
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
