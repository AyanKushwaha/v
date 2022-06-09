#!/bin/env python


"""
SKBMM-700 Add SKS CC to FDA (Transition)


"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # Remove the current old BIDS_CCAC_QUAL types
    for entry in fixrunner.dbsearch(dc, 'crew_qualification_set'):
        if entry['typ'] == 'BIDS_CCAC_QUAL':
            ops.append(fixrunner.createop('crew_qualification_set', 'D', entry))

    crew_qualification_set_data = [('BIDS_CCAC_QUAL_SKD','CJ'),
                                   ('BIDS_CCAC_QUAL_SKD','AL'),
                                   ('BIDS_CCAC_QUAL_SKD','A2'),
                                   ('BIDS_CCAC_QUAL_SKS','SH'),
                                   ('BIDS_CCAC_QUAL_SKS','SH/LH')]

    for typ, subtyp in crew_qualification_set_data:
        if len(fixrunner.dbsearch(dc, 'crew_qualification_set', "typ='%s' AND subtype='%s'" % (typ, subtyp))) == 0:
            ops.append(fixrunner.createop('crew_qualification_set', 'N', {'typ' : typ, 'subtype': subtyp}))
        else:
            print "Crew qualification %s %s already exists" % (typ, subtyp)

    return ops


fixit.program = 'skbmm700.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
