"""
* SASCMS-5161: Adding activities to activity_set and
               AC qualifications to course_ac_qual_set
"""

import adhoc.fixrunner as fixrunner
import os
from AbsTime import AbsTime

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    newacts = [{'id': 'Z4', 'grp': 'PC', 'si': 'CAA/skill test A340'},
               {'id': 'Z5', 'grp': 'PC', 'si': 'CAA/skill test F50'},
               {'id': 'Z6', 'grp': 'PC', 'si': 'CAA/skill test A330'},
               {'id': 'Z8', 'grp': 'PC', 'si': 'CAA/skill test MD80'},
               {'id': 'Z9', 'grp': 'PC', 'si': 'CAA/skill test 737-CL'}]

    newacquals = ['A3A4', '3738']

    for act in newacts:
        if len(fixrunner.dbsearch(dc, 'activity_set', "id='%s'" % act['id'])) == 0:
            op = fixrunner.createOp('activity_set', 'N', act)
            ops.append(op)
        else:
            print "Entry with id='%s' already exist" % act['id']

    for acqual in newacquals:
        if len(fixrunner.dbsearch(dc, 'course_ac_qual_set', "id='%s'" % acqual)) == 0:
            op = fixrunner.createOp('course_ac_qual_set', 'N', {'id': acqual})
            ops.append(op)
        else:
            print "Entry with id='%s' already exist" % acqual


    return ops


fixit.program = 'sascms-5161.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
