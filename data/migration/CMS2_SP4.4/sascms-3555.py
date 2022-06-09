

"""
Add some new calculation methods for drivers that were introduced for CR sascms-3555.
"""

import adhoc.fixrunner as fixrunner


__version__ = '$Revision$'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('est_param_type_set', 'W', {
            'param_type': 'MUL',
        }),
        fixrunner.createOp('est_param_type_set', 'W', {
            'param_type': 'DIV',
        }),
        fixrunner.createOp('est_param_type_set', 'W', {
            'param_type': 'IDIV',
        }),

    ]


fixit.program = 'sascms-3555.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
