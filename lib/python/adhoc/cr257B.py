

"""
Add some new vacation codes that were introduced for CR 257B.
"""

import fixrunner


__version__ = '$Revision$'

@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('est_task', 'W', {
            'code': 'VAD',
            'cat': 'F',
            'taskgroup_code': 'VA',
            'taskgroup_cat': 'F',
        }),
        fixrunner.createOp('est_task', 'W', {
            'code': 'VAH',
            'cat': 'F',
            'taskgroup_code': 'VA',
            'taskgroup_cat': 'F',
        }),
        fixrunner.createOp('est_task', 'W', {
            'code': 'VA1D',
            'cat': 'F',
            'taskgroup_code': 'VA1',
            'taskgroup_cat': 'F',
        }),
        fixrunner.createOp('est_task', 'W', {
            'code': 'VA1H',
            'cat': 'F',
            'taskgroup_code': 'VA1',
            'taskgroup_cat': 'F',
        }),
        fixrunner.createOp('activity_set', 'W', {
            'id': 'VAD',
            'grp': 'VAC',
            'si': 'Vacation with double rate SKN',
        }),
        fixrunner.createOp('activity_set', 'W', {
            'id': 'VAH',
            'grp': 'VAC',
            'si': 'Vacation with high rate SKN',
        }),
        fixrunner.createOp('activity_set', 'W', {
            'id': 'VA1D',
            'grp': 'VAC',
            'si': 'Vacation without salary double rate SKN',
        }),
        fixrunner.createOp('activity_set', 'W', {
            'id': 'VA1H',
            'grp': 'VAC',
            'si': 'Vacation without salary high rate SKN',
        }),
    ]


fixit.program = 'cr257B.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
