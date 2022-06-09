#!/bin/env python


"""
SASCMS-4616 CCR FC TR Part from CR4081. Qual valid time on
            qualification on airports OM-C OPS Info 7.1- 7.2


"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []


    # Populate valid_qual_interval_set
    intervals = ['6 months',
                 '1 year',
                 '3 years',
                 '5 years',
                 'Inf.']

    for interval in intervals:
        if len(fixrunner.dbsearch(dc, 'valid_qual_interval_set', "id='%s'" % interval)) == 0:
            ops.append(fixrunner.createop('valid_qual_interval_set', 'N', {'id' : interval}))
        else:
            print "Interval %s already exists" % interval


    # Enter intervals supplied by SAS in apt_requirements
    table = [('INN','3 years'),
             ('JKH','5 years'),
             ('SMI','5 years'),
             ('UAK','3 years'),
             ('SFJ','5 years'),
             ('THU','5 years'),
             ('ORD','5 years'),
             ('EWR','5 years'),
             ('IAD','5 years'),
             ('ALF','3 years'),
             ('KSU','3 years'),
             ('KKN','5 years'),
             ('LYR','5 years'),
             ('FNC','6 months'),
             ('HMV','3 years'),
             ('GZP','3 years'),
             ('LCY','3 years')]

    for aoc in ['BU','SK']:
        for ap, interval in table:
            if len(fixrunner.dbsearch(dc, 'apt_requirements',
                                      "airport='%s' AND aoc='%s'" % (ap,aoc))) == 1:
                ops.append(fixrunner.createop('apt_requirements', 'U',
                                              {'airport'             : ap,
                                               'aoc'                 : aoc,
                                               'valid_qual_interval' : interval}))
            else:
                print "airport='%s' and aoc='%s' does not exist" % (ap,aoc)


    return ops


fixit.program = 'sascms-4616.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
