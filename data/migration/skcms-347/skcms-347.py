#!/bin/env python


"""
SKCMS-5424: New database table flyover.
            This script populates the new table flyover.
"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []


    # Populate flyover table
    flyovers = [('DK', 'JP', 'RU'),
                ('DK', 'CN', 'RU'),
                ('NO', 'JP', 'RU'),
                ('NO', 'CN', 'RU'),
                ('SE', 'JP', 'RU'),
                ('SE', 'CN', 'RU')];

    for (country_a, country_b, flyover) in flyovers:
        and_expr = [' AND '.join(["country_a='%s'" % a,
                                  "country_b='%s'" % b,
                                  "flyover='%s'" % flyover]) for (a, b) in [(country_a, country_b), (country_b, country_a)]]
        expr = "(%s)" % ') OR ('.join(and_expr)
        if len(fixrunner.dbsearch(dc, 'flyover', expr)) == 0:
            ops.append(fixrunner.createop('flyover', 'N', {'country_a': country_a,
                                                           'country_b': country_b,
                                                           'flyover': flyover,
                                                           'validfrom': 0}))
        else:
            print "Flyover %s <-> %s => %s already exists" % (country_a, country_b, flyover)

    return ops


fixit.program = 'sascms-347.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
