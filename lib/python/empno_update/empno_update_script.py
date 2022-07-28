"""
Update empno similar to extperkey wherever it is not already matching .

Rewritten to use fixrunner.
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
import datetime
EPOCH = datetime.datetime(1986, 1, 1)
ct = datetime.datetime.now()

def get_now():
    """Return now as DAVE time."""
    timestamp = datetime.datetime.now() - EPOCH
    return timestamp.days * 1440 + timestamp.seconds / 60

@fixrunner.run
def fixit(dc, *a, **k):
    now = get_now()
    now_udor = get_now() / 1440
    print "The value of now is " , now
    print "The value of now_udor is ", now_udor
    ops = []
    for crew in fixrunner.dbsearch(dc, 'crew_employment', ' AND '.join((
            "deleted = 'N'",
            "next_revid = 0",
            "validfrom <= '%s'" % now,
            "validto > '%s'" % now,
        ))):
        for entry in fixrunner.dbsearch(dc, 'crew', ' AND '.join((
            "id = '%s'" % crew['crew'],
            "empno <> '%s'" % crew['extperkey'],
            "(retirementdate > '%s' OR retirementdate IS NULL)" % now_udor,
            "deleted = 'N'",
            "next_revid = 0",
        ))):
           print "The value of id is ", entry['id'] , "crew is ", crew['crew'], " and the value of extperkey is " , crew['extperkey'] , "and empno is ", entry['empno'] , " and retirementdate is " , entry['retirementdate']
           entry['empno'] = crew['extperkey'] 
           ops.append(fixrunner.createOp('crew', 'U', entry))
    return ops

fixit.program = 'empno_update_script.py_(%s)' % ct

if __name__ == '__main__':
    fixit()
