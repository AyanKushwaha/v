

"""
SASCMS-1914

Previous F33 calculations were faulty: 
- Pilots in segment RC got too many F33 days.
- The script did not consider contract or employment changes.
"""

import datetime
import getpass
import os
import re
import subprocess

import adhoc.fixrunner as fixrunner
import utils.dt

from carmensystems.basics.uuid import uuid
from salary.reasoncodes import REASONCODES

__version__ = '$Revision$'


# list of run dates, note that June and August don't give any results.
run_dates = ['20100401', '20100501', '20100701', '20100901']


new_env = dict(os.environ, CMS_SALARY_NOCOMMIT="1", CMS_SALARY_DEBUG="1")
script = os.path.join(os.environ['CARMUSR'], 'bin', 'salary_batch.sh')
regex = re.compile(r'^.*id=(\d{5}).*amount=(\d{3,4})$')
now = utils.dt.dt2m(datetime.datetime.now())
username = getpass.getuser()


def make_op(crew, amount, tim):
    record = {
        'id': uuid.makeUUID64(),
        'crew': crew,
        'account': 'F33',
        'source': 'sascms-1914.py',
        'amount': int(amount),
        'man': 'Y',
        'published': 'Y',
        'rate': 100 * (1, -1)[amount < 0],
        'reasoncode': REASONCODES['IN_CORR'],
        'tim': tim,
        'entrytime': now,
        'username': username,
        'si': 'Correction F33 conversion (SASCMS-1914)',
    }
    return fixrunner.createop('account_entry', 'N', record)


@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # First check what the new calculation would have given...
    # Run in debug mode and don't commit any changes!
    for date in run_dates:
        fixrunner.log.info('Checking F33 job for date %s.' % date)
        dave_date = utils.dt.dt2m(datetime.datetime(int(date[:4]), int(date[4:6]), int(date[6:8])))
        facit = {}
        handled = set()
        (sout, serr) = subprocess.Popen([script, 'F33GAIN', '-l', date],
                env=new_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        for row in serr.split('\n'):
            m = regex.match(row)
            if m:
                facit[m.group(1)] = int(m.group(2))

        # Now check what we saved in the database for this date...
        for entry in fixrunner.dbsearch(dc, 'account_entry', ' AND '.join((
                "account = 'F33'",
                "source = 'salary.compconv.Increment_F33'",
                "tim = %d" % dave_date
            ))):
            crewid = entry['crew']
            amount = entry['amount']
            if crewid in facit:
                if facit[crewid] == amount:
                    fixrunner.log.debug('%s: 0: crew %s - no changes.' % (date, crewid))
                else:
                    fixrunner.log.debug('%s: C: crew %s - old value was %s, new value is %s.' % (date, crewid, amount, facit[crewid]))
                    entry['amount'] = facit[crewid]
                    ops.append(fixrunner.createop('account_entry', 'W', entry))
            else:
                fixrunner.log.debug('%s: D: crew %s - was faulty given %s, removing.' % (date, crewid, amount))
                ops.append(fixrunner.createop('account_entry', 'D', entry))
            handled.add(crewid)

        for c in facit:
            if not c in handled:
                fixrunner.log.debug('%s: N: crew %s - creating new record with value %s.' % (date, c, facit[c]))
                ops.append(make_op(c, facit[c], dave_date))

    return ops


fixrunner.program = 'sascms-1914.py (%s)' % __version__


if __name__ == '__main__':
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
