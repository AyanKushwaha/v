

"""
SASCMS-1847
Change filtering of 'account_entry'.
"""

import adhoc.fixrunner as fixrunner


__version__ = '$Revision$'


@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for entry in fixrunner.dbsearch(dc, 'dave_entity_select', ' AND '.join((
            "selection = 'baseline'",
            "entity = 'account_entry'",
            "tgt_entity = 'account_entry'",
        ))):
        entry['wtempl'] = '$.tim>=%:1'
        ops.append(fixrunner.createop('dave_entity_select', 'U', entry))
    return ops


if __name__ == '__main__':
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
