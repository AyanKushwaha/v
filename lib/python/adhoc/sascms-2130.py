

"""
SASCMS-2130 - "Crew Phone number. Same in Tracking and Crew Services"

Part of the full solution - add a few entries to 'crew_contact_which'.
"""

import fixrunner


__version__ = '$Revision$'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    table = 'crew_contact_which'
    ops = [
        fixrunner.createop(table, 'N', {
            'which': 'main',
            'si': 'Preferred contact for the primary address',
        }),
        fixrunner.createop(table, 'N', {
            'which': 'secondary',
            'si': 'Preferred contact for the secondary address',
        }),
    ]
    for i in range(1, 10):
        ops.append(fixrunner.createop(table, 'N', {
            'which': 'main%d' % i,
            'si': 'Contact #%d (primary address)' % i,
        }))
        ops.append(fixrunner.createop(table, 'N', {
            'which': 'secondary%d' % i,
            'si': 'Contact #%d (secondary address)' % i,
        }))
    return ops


fixit.remark = 'sascms-2130.py (%s)' % __version__


if __name__ == '__main__':
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
