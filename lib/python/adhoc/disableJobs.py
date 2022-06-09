

"""
Update jobs in the job table, so they are not run.
Used when copying schema's from PROD to TEST.
"""

import fixrunner
import datetime
import os

__version__ = '$Revision$'

@fixrunner.run
def myfixit(dc, *a, **k):
    ops = []
    user = os.environ.get("USER")
    # Search for entries that are not started yet
    for entry in fixrunner.dbsearch(dc, 'job', ' AND '.join((
            "started_at = 'not started'",
            "status is null",
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        entry['started_at'] = datetime.datetime.now().replace(microsecond=0).isoformat()
        entry['status'] = 'Manually stopped by %s' % (user)
        ops.append(fixrunner.createOp('job', 'U', entry))
    return ops


myfixit.program = 'disableJobs.py (%s)' % __version__


if __name__ == '__main__':
    myfixit()
