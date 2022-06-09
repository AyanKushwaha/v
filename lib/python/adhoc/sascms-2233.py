

"""
CR SASCMS-2233  - Create a new role - Superuser

This script will add a 4 new records to cms_views:
Superuser+upd_roster
Superuser+read_crewbase
Superuser+read_all
Superuser+crewinfo
"""

import fixrunner

__version__ = '$Revision$'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('cms_views', 'N', {
        'cms_role':'Superuser',
        'cms_view':'upd_roster',
        'cms_view_acl':6,
        }),
        fixrunner.createOp('cms_views', 'N', {
        'cms_role':'Superuser',
        'cms_view':'read_crewbase',
        'cms_view_acl':4,
        }),
        fixrunner.createOp('cms_views', 'N', {
        'cms_role':'Superuser',
        'cms_view':'read_all',
        'cms_view_acl':4,
        }),
        fixrunner.createOp('cms_views', 'N', {
        'cms_role':'Superuser',
        'cms_view':'crewinfo',
        'cms_view_acl':6,
        }),
    ]


fixit.program = 'sascms-2233.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
