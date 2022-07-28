"""
Update empno similar to extperkey wherever it is not already matching .

Rewritten to use fixrunner.
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
import datetime
ct = datetime.datetime.now()

@fixrunner.run
def fixit(dc, *a, **k):
    now = 19185120  
    """ Above value is found using  carmdate.date2min('2022-07-24 00:00:00') in DB """
    now_udor = 13323 
    """ Above value is found using carmdate.date2udor('2022-07-24') in DB """
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
