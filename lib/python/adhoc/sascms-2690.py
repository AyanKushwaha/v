

"""
SASCMS-2690

Remove all F33 days with source 'salary.compconv.Increment_F33'.
Re-run all periods.
"""

import datetime
import os
import subprocess

import adhoc.fixrunner as fixrunner


__version__ = '$Revision$'


# list of run dates, note that June and August don't give any results.
run_dates = ['20100401', '20100501', '20100701', '20100901', '20101001']


script = os.path.join(os.environ['CARMUSR'], 'bin', 'salary_batch.sh')


@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for entry in fixrunner.dbsearch(dc, 'account_entry', ' AND '.join((
            "account = 'F33'",
            "source = 'salary.compconv.Increment_F33'",
        ))):
        ops.append(fixrunner.createop('account_entry', 'D', entry))

    return ops


fixrunner.program = 'sascms-2690.py (%s)' % __version__


def rerun():
    for date in run_dates:
        fixrunner.log.info('Re-running F33 job for date %s.' % date)
        proc = subprocess.Popen([script, 'F33GAIN', '-l', date])
        proc.wait()


def do_all():
    fixit()
    rerun()


if __name__ == '__main__':
    do_all()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
