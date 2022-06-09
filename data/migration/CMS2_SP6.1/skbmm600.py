#!/bin/env python


"""
 SKBMM 600

*  Change dave filter for bid_transaction table
"""

import adhoc.fixrunner as fixrunner

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # Remove the current filter
    for entry in fixrunner.dbsearch(dc, 'dave_entity_select'):
        if entry['selection'] == 'mppcategory' and entry['entity'] == 'bid_transaction' and entry['tgt_entity'] == 'crew':
            ops.append(fixrunner.createop('dave_entity_select', 'D', entry))


    ops.append(fixrunner.createop('dave_entity_select', 'N', {'selection': 'mppcategory',
                                                              'entity' : 'bid_transaction',
                                                              'tgt_entity' : 'crew_user_filter',
                                                              'wtempl': "($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|___') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|___'))",
                                                              'via_src_columns':'crew',
                                                              'via_tgt_columns':'crew',
                                                              'via_distinct':'true'}))

    return ops


fixit.program = 'skbmm600.py (%s)' % __version__


if __name__ == '__main__':
    fixit()            
