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
    with open('new_rec_docs.csv') as f:
        new_rec_docs = [map(lambda s: s.strip('"'), line.split(','))[:5] for line in f ][1:]
    with open('prev_rec_revision.csv') as f:
        rec_prev_end_dates = [map(lambda s: s.strip('"'), line.split(','))[:5] for line in f ][1:]


    ops = []

    for doc in new_rec_docs:
        ops.append(fixrunner.createOp('crew_document', 'D', {'crew':doc[0],
                                                             'doc_typ':doc[1],
                                                             'doc_subtype':doc[2],
                                                             'validfrom':int(dateToAbsTime(doc[3]))}))
    for doc in rec_prev_end_dates:
        ops.append(fixrunner.createOp('crew_document', 'U', {'crew':doc[0],
                                                             'doc_typ':doc[1],
                                                             'doc_subtype':doc[2],
                                                             'validfrom':int(dateToAbsTime(doc[3])),
                                                             'validto':int(dateToAbsTime(doc[4]))
                                                        }))
    print ops
    return ops


fixit.program = 'sksd-4794.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except ValueError, err:
        print err
