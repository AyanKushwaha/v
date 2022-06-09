

"""
Add new vacation code AUTO that is introduced for CR406 Create Leave in SP10.
"""

import fixrunner


__version__ = '$Revision$'

@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('est_task', 'W', {
            'code': 'AUTO',
            'cat': 'F',
            'taskgroup_code': 'VA',
            'taskgroup_cat': 'F',
        }),
        fixrunner.createOp('est_task', 'W', {
            'code': 'AUTO',
            'cat': 'C',
            'taskgroup_code': 'VA',
            'taskgroup_cat': 'C',
        })
    ]


fixit.program = 'sascms-2086.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
