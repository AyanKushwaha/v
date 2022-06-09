

"""
Script to force Master Crew List to ADD or UPDATE selected crew members.

(See SASCMS-689).
"""

import adhoc.fixrunner as fixrunner
import datetime


__version__ = '$Revision$'
default_country = 'US'
EPOCH = datetime.datetime(1986, 1, 1)


class MCLParser(fixrunner.BasicParser):
    def __init__(self, *a, **k):
        fixrunner.BasicParser.__init__(self, *a, **k)
        self.usage = '%prog [-c COUNTRY] {add|deladd|update} crewid1 [crewid2 [...]]'
        self.add_option("-C", "--country",
            dest="country",
            default=default_country,
            help="Master crew list for country (default '%s')." % default_country)
        

def get_now():
    """Return now as DAVE time."""
    timestamp = datetime.datetime.now() - EPOCH
    return timestamp.days * 1440 + timestamp.seconds / 60
    

@fixrunner.run
def fixit(dc, *a, **k):
    args = list(a)
    if len(args) < 2:
        fixrunner.get_parser().error("Wrong number of arguments")
    ops = []
    operation = args.pop(0)
    country = k.get('country', default_country)
    crewids = []
    now = get_now()
    for empno in args:
        for rec in fixrunner.dbsearch(dc, 'crew_employment', ' AND '.join((
                'validfrom <= %s' % now,
                'validto > %s' % now,
                "extperkey = '%s'" % empno,
            ))):
            crewids.append(rec['crew'])
            break
        else:
            raise ValueError("Cannot find crew with extperkey '%s'." % empno)
    for entry in fixrunner.dbsearch(dc, 'mcl', ' AND '.join((
            "mcl = '%s'" % country,
            "id IN (%s)" % ', '.join(["'%s'" % x for x in crewids]),
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        if operation.lower() == 'add':
            ops.append(fixrunner.createOp('mcl', 'D', entry))
        elif operation.lower() == 'deladd':
            entry['sn'] += ' '
            entry['gn'] += ' '
            ops.append(fixrunner.createOp('mcl', 'U', entry))
        elif operation.lower() == 'update':
            entry['nationality'] = ''
            ops.append(fixrunner.createOp('mcl', 'U', entry))
        else:
            fixrunner.get_parser().error("First argument must be one of ('add', 'deladd', 'update').")
    return ops


fixit.program = 'mcl.py (%s)' % __version__
fixrunner.set_parser(MCLParser)


if __name__ == '__main__':
    fixit()
