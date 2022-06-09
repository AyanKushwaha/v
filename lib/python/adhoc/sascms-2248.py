#!/bin/env python


"""
SASCMS-2248 - F33 days incorrectly given to SKI crew.

This script will revert the results from previous batch runs.

NOTE: The command salary_batch.sh has to be re-run (corrected version of
course!).

$ salary_batch.sh F33GAIN -l 20100401

$ salary_batch.sh F33GAIN -l 20100501

"""

import adhoc.fixrunner as fixrunner


__version__ = '$Revision$'


@fixrunner.once
@fixrunner.run
def fixit(dc, revids, *a, **k):
    ops = []
    for revid in revids:
        ops.extend(fixrunner.backout(dc, revid))
    return ops


fixit.program = 'sascms-2248.py (%s)' % __version__


if __name__ == '__main__':
    # reverting results from earlier runs (revids)
    fixit([18972906, 18973141])


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
