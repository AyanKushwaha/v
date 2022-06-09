

"""
Add new type of revtag for new revision handling in CMP for SP7.
"""

import fixrunner


__version__ = '$Revision$'

@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('revtag_category_set', 'W', {
            'name': 'cmp',
        }),
    ]


fixit.program = 'sascms-344.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
