#!/bin/env python


"""
SASCMS-5552: save data from preferred_hotel_exc
"""

import adhoc.fixrunner as fixrunner
import os

__version__ = '1'


#@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    data = fixrunner.dbsearch(dc, 'preferred_hotel_exc')

    savefile = open("%s/preferred_hotel_exc.dump"% os.getenv('LOG_DIR'), 'wb')
    for d in data:
        savefile.write(str(d) + "\n")
    savefile.close

    return ops


fixit.program = 'sascms-5552_save.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
