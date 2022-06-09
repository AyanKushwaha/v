#!/bin/env python


"""
CR 454 - Instructor's allowance

* Add new internal article ID's for the new salary types.
"""

import datetime
import utils.dt
import adhoc.fixrunner as fixrunner


__version__ = '$Revision$'

template = {
    'validfrom': utils.dt.dt2m(datetime.datetime(2011, 1, 1)),
    'validto': utils.dt.dt2m(datetime.datetime(2034, 12, 31)),
}

codes = {
    'TEMPCREW': ({
        'SE': '013',
    }, "Temporary crew hours"),
    'TEMPCREWOT': ({
        'SE': '014',
    }, "Temporary crew overtime"),
}


#@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for intartid in codes:
        extartids, note = codes[intartid]
        for extsys in extartids:
            op = template.copy()
            op['extsys'] = extsys
            op['intartid'] = intartid
            op['extartid'] = extartids[extsys]
            op['note'] = note
            ops.append(fixrunner.createop('salary_article', 'N', op))
    return ops


fixit.program = 'sascms-2777.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
