"""
SASCMS-2424
Change filtering of 'bought_days'.
"""

import fixrunner


__version__ = '$Revision$'


@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    for entry in fixrunner.dbsearch(dc, 'dave_entity_select', ' AND '.join((
            "selection = 'te_period_bought_days'",
            "entity = 'bought_days'",
            "tgt_entity = 'bought_days'",
        ))):
        entry['wtempl'] = '$.start_time>=%:3-367*1440 and $.start_time<=%:4'
        ops.append(fixrunner.createop('dave_entity_select', 'U', entry))

    for entry in fixrunner.dbsearch(dc, 'dave_entity_select', ' AND '.join((
            "selection = 'period'",
            "entity = 'bought_days'",
            "tgt_entity = 'bought_days'",
        ))):
        entry['wtempl'] = '$.start_time>=%:3-367*1440 and $.start_time<=%:4'
        ops.append(fixrunner.createop('dave_entity_select', 'U', entry))
        
    return ops


if __name__ == '__main__':
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
