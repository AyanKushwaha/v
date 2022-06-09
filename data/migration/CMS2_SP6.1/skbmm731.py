#!/bin/env python


"""
SKBMM-731 Remove AC 90 Type from crew_qualification_set


"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    
    ops = []

    data_to_be_removed = [("BIDS_CCAC_QUAL", "90")]

    for (typ, subtype) in data_to_be_removed:
        for entry in fixrunner.dbsearch(dc, 'crew_qualification_set', "typ='%s' and subtype='%s'" % (typ,subtype)):
            ops.append(fixrunner.createop('crew_qualification_set', 'D', entry))

    return ops


fixit.program = 'skbmm731.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
