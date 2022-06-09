

"""
CR 436 - Manual handling of FCM

This script will add a couple of new records:
(1) a new attribute category 'Error', that can be used to signal for errors, and
(2) a new attribute 'FCMERROR' that triggers a Rave rule.
"""

import fixrunner


__version__ = '$Revision$'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('attr_category_set', 'N', {
            'id': 'Error',
            'si': 'Attributes for error conditions',
        }),
        fixrunner.createOp('leg_attr_set', 'N', {
            'id': 'FCMERROR',
            'category': 'Error',
            'si': 'Error when generating Flight Crew Manifest (APIS)',
        }),
    ]


fixit.program = 'cr436.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
