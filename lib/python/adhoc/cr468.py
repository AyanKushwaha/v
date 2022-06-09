

"""
CR 468 - Remigration of Blockhours
"""

import logging
import fixrunner
import utils.dt

from AbsTime import AbsTime
from carmensystems.dave import baselib


__version__ = '$Revision$'


log = fixrunner.log


ac_map = {
    'DH8': 'Q400',
    'Others': 'OTHER',
}


def ac_translate(af):
    return ac_map.get(af, af)
    

def get_cabin(dc):
    """Return set of cabin crew."""
    cabin = set()
    params = baselib.Result(1)
    params.setString(0, 'C')
    filt = baselib.Filter('crew_employment')
    filt2 = baselib.Filter('crew_rank_set')
    filt2.where2('maincat', '= %:1')
    filt.relating2(filt2, baselib.KeySpec('titlerank'), baselib.KeySpec('id'))
    conn = dc.getConnection()
    spec = conn.getEntitySpec('crew_employment')
    conn.beginReadTxn()
    try:
        conn.setSelectParams(params)
        conn.select('crew_employment', filt)
        rec = conn.readRecord()
        while rec:
            cabin.add(rec.valuesAsDict(spec)['crew'])
            rec = conn.readRecord()
    finally:
        conn.endReadTxn()
    return cabin


@fixrunner.once
@fixrunner.run
def fixit(dc, filename, *a, **k):
    ops = []

    dh8_save = {}
    log.info("STEP 0: Collecting DH8.")
    for rec in fixrunner.dbsearch(dc, 'crew_log_acc', "acfamily = 'DH8'"):
        dh8_save[(rec['crew'], rec['typ'], rec['acfamily'], rec['tim'])] = rec

    log.info("STEP 1: Moving from Others -> OTHER.")
    for rec in fixrunner.dbsearch(dc, 'crew_log_acc_mod', "acfamily = 'Others'"):
        ops.append(fixrunner.createop('crew_log_acc_mod', 'D', rec))
        newrec = rec.copy()
        newrec['acfamily'] = 'OTHER'
        ops.append(fixrunner.createop('crew_log_acc_mod', 'N', newrec))

    log.info("STEP 2: Removing data with A/C family 'OTHER' and typ 'blockhrs' or 'logblkhrs'.")
    for rec in fixrunner.dbsearch(dc, 'crew_log_acc', "acfamily = 'OTHER' and typ in ('blockhrs', 'logblkhrs')"):
        ops.append(fixrunner.createop('crew_log_acc', 'D', rec))

    log.info("STEP 3: Adding data from file %s." % filename)
    inf = None
    try:
        inf = open(filename, "r")
        for line in inf:
            if line.startswith('#'):
                continue
            crew, typ, acfamily, tim, accvalue = line.split(';')
            tim = int(AbsTime(tim))
            accvalue = int(accvalue)
            ops.append(fixrunner.createop('crew_log_acc', 'W', {
                'crew': crew,
                'typ': typ,
                'acfamily': ac_translate(acfamily),
                'tim': tim,
                'accvalue': accvalue,
            }))
            if acfamily == 'DH8':
                key = (crew, typ, acfamily, tim)
                if key in dh8_save:
                    ops.append(fixrunner.createop('crew_log_acc', 'D', dh8_save[key]))
                    del dh8_save[key]
    finally:
        if inf:
            inf.close()

    log.info("STEP 4: Removing data for Cabin Crew.")
    cabin = get_cabin(dc)
    for rec in fixrunner.dbsearch(dc, 'crew_log_acc', "typ <> 'blockhrs'"):
        if rec['crew'] in cabin:
            if rec['acfamily'] == 'DH8':
                try:
                    del dh8_save[(rec['crew'], rec['typ'], rec['acfamily'], rec['tim'])]
                except:
                    pass
            ops.append(fixrunner.createop('crew_log_acc', 'D', rec))

    log.info("STEP 5: Moving remaining DH8 -> Q400.")
    for key in dh8_save:
        rec = dh8_save[key]
        crew, typ, acfamily, tim = key
        ops.append(fixrunner.createop('crew_log_acc', 'D', rec))
        ops.append(fixrunner.createop('crew_log_acc', 'N', dict(crew=crew,
            typ=typ, acfamily="Q400", tim=tim,
            accvalue=rec['accvalue'])))
    
    return ops


fixit.program = 'cr468.py (%s)' % __version__


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print >>sys.stderr, "usage: cr468.py csv-file"
        sys.exit(2)
    fixit()
