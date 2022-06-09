#!/bin/env python


"""
SKCMS-1564 Change validity date for FNC airport qualification to training date + 6 months (Not rounded to end of month).
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
import datetime

__version__ = '2'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    now = AbsTime(str(datetime.datetime.now().strftime('%Y%m%d')))

    flown = {}
    for entry in fixrunner.dbsearch(dc, 'crew_training_log', "((typ='FLIGHT AIRPORT') OR (typ='SIM AIRPORT')) AND (attr='FNC')"):
        if flown.get(entry['crew'], entry['tim']) <= entry['tim']:
            flown[entry['crew']] = entry['tim']

    for crew in flown:
        tim = AbsTime(flown[crew])
        validfrom = tim.day_ceil()
        validto = add_six_months(validfrom)

        # print crew, AbsTime(tim), AbsTime(validfrom), AbsTime(validto)

        for entry in fixrunner.dbsearch(dc, 'crew_qualification', "(crew=%s) AND (qual_typ='AIRPORT' AND qual_subtype='FNC' AND validto>%s)" % (crew, int(now))):
#            print "Need to delete:", entry['crew'], entry['qual_typ'], entry['qual_subtype'], AbsTime(entry['validfrom']), AbsTime(entry['validto'])
            ops.append(fixrunner.createop('crew_qualification', 'D', entry))
        if validto > int(now):
            new = {'crew' : crew,
                   'qual_typ' : 'AIRPORT',
                   'qual_subtype' : 'FNC',
                   'validfrom' : int(validfrom),
                   'validto' : int(validto)}
#            print "Will create:", new['crew'], new['qual_typ'], new['qual_subtype'], AbsTime(new['validfrom']), AbsTime(new['validto'])
            ops.append(fixrunner.createop('crew_qualification', 'N', new))

    ops.append(fixrunner.createop("apt_requirements", "U", {"airport":"FNC", "aoc":"SK", "fcreq":True, "fpreq":False, "fcqlnreq":True, "simreq":True, "valid_qual_interval":"6 months"}))

    return ops

def add_six_months(validfrom):
    the_date = AbsTime(validfrom)
    new_date = the_date.addmonths(6)
    return int(new_date)


fixit.program = 'skcms_1564.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
