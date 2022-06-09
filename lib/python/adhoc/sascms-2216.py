

"""
SASCMS-2216

Script to recreate data as it was before revid 17201055, which was a session
that destroyed data for crew '23300'.
"""

import adhoc.fixrunner as fixrunner


__version__ = '$Revision$'


@fixrunner.once
@fixrunner.run
def fixit(dc, revid, *a, **k):
    return fixrunner.backout(dc, revid)


fixit.program = 'sascms-2216.py (%s)' % __version__


if __name__ == '__main__':
    fixit(17201055)
