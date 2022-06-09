#!/usr/bin/env python

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '1.0'


monthName = {'01':'Jan', '02':'Feb', '03':'Mar', '04':'Apr', '05':'May',
          '06':'Jun', '07':'Jul', '08':'Aug', '09':'Sep', '10':'Oct',
          '11':'Nov', '12':'Dec'}

def dateToAbsTime(d):
    year, month, day = d.split('-')
    return AbsTime(day+monthName[month]+year)

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    with open('./prev_crewqual_records.csv') as f:
        prev_crewqual_records = [map(lambda s: s.strip('"'), line.split(','))[:5] for line in f ][1:]
    with open('./new_crewqual_records.csv') as f:
        new_crewqual_records = [map(lambda s: s.strip('"'), line.split(','))[:5] for line in f ][1:]


    ops = []

    for doc in prev_crewqual_records:
        ops.append(fixrunner.createOp('crew_qualification', 'D', {'crew':doc[0],
                                                             'qual_typ':doc[1],
                                                             'qual_subtype':doc[2],
                                                             'validfrom':int(doc[3]),
                                                             'validto':int(doc[4])}))
												 

    for doc in new_crewqual_records:
	    ops.append(fixrunner.createOp('crew_qualification', 'N', {'crew':doc[0],
                                                             'qual_typ':doc[1],
                                                             'qual_subtype':doc[2],
                                                             'validfrom':int(doc[3]),
                                                             'validto':int(doc[4])}))
															 
    print ops
    return ops


fixit.program = 'skcms-2613.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except ValueError, err:
        print err
