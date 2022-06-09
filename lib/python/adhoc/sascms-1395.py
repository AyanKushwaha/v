

"""
SASCMS-1395 - "Set validto to max allowed AbsTime in table crew_document where
    validto is null"

Problem: When 'validto' is empty in 'crew_document' Rave calculations crash and
    Crew Manifest cannot be created.

Solution: This script will set the validto to a 'max' value for those entries
    where 'validto' is NULL.

Q: Should this script also check for overlaps?
"""

import fixrunner


__version__ = '$Revision$'

# 2035-12-31 0:00 is used everywhere else so...
MAXVALUE = 26295840


@fixrunner.run
def fixit(dc, table, *a, **k):
    ops = []
    for entry in fixrunner.dbsearch(dc, table, ' AND '.join((
            "validto is NULL",
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        entry['validto'] = MAXVALUE
        ops.append(fixrunner.createOp(table, 'U', entry))
    return ops


fixit.remark = 'SASCMS-1395 (%s)' % __version__


if __name__ == '__main__':
    fixit('crew_document')
